import asyncio
import subprocess
import websockets
import json
import base64
import time
import curses
import pyaudio
import boto3

from ctypes import *
from multiprocessing import Process, Queue, Manager
from config import config, preset
from virtual_device import virtualmic

virtual_device_id = 0

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

audio_queue = asyncio.Queue()
all_mic_data = []
all_transcripts = []

ffmpeg_stream = [
    "ffmpeg",
    "-re",
    "-i",
    f"{preset.file.virtual_stream}",
    "-f",
    "s16le",
    "-ar",
    "16000",
    "-ac",
    "1",
    "-loglevel",
    "0",
    "-",
]

recognize_queue = Queue()
recognize_text = ""

translated_queue = Queue()
translated_queue2 = Queue()
translated_text = ""

speech_queue = Queue()
speech_queue2 = Queue()
speech_text = ""

info_queue = Queue()
info_text = ""

status_codes = {
    "record_on": "🔴",
    "sound": "🔊",
    "mail": "📨",
    "success": "✅",
    "write": "📄",
    "transfer": "🔃",
    "plug": "🔌",
    "record_off": "⚫",
    "speech": "🗣️",
    "wait": "⌛",
    "get_data": "📡",
    "download": "📥",
    "error": "❌",
    "warning": "⚠️",
    "skull": "☠️",
}

manager = Manager()
status_dict = manager.dict()

status_dict["device"] = status_codes["wait"]
status_dict["record"] = status_codes["record_off"]
status_dict["stt"] = status_codes["wait"]
status_dict["tts"] = status_codes["wait"]
status_dict["stream"] = status_codes["wait"]


# buffer yapılacak
def stream_audio():
    while True:
        while not speech_queue.empty():
            info_queue.put("Info: Speech is playing...")
            status_dict["stream"] = status_codes["speech"]

            data = speech_queue.get()
            info_queue.put("Info: Data Lenght={}bytes".format(len(data)))
            with open(preset.file.virtual_stream, "wb") as audio_file:
                audio_file.write(data)
                audio_file.close()

            with subprocess.Popen(
                ffmpeg_stream, stdout=subprocess.PIPE
            ) as ffmpeg_process:
                while True:
                    audio_data = ffmpeg_process.stdout.read(128)
                    if not audio_data:
                        break
                    with open(preset.file.virtual_input, "ab") as virtmic:
                        virtmic.write(audio_data)

            status_dict["stream"] = status_codes["wait"]
        time.sleep(0.1)


def translate(
    text, source=config.setting.input_language, target=config.setting.target_language
):
    translate = boto3.client(
        service_name="translate",
        region_name=config.aws.region_name,
        use_ssl=True,
        aws_access_key_id=config.aws.access_key_id,
        aws_secret_access_key=config.aws.secret_access_key,
    )

    result = translate.translate_text(
        Text=text, SourceLanguageCode=source, TargetLanguageCode=target
    )
    return result.get("TranslatedText")
    print("TranslatedText: " + result.get("TranslatedText"))
    print("SourceLanguageCode: " + result.get("SourceLanguageCode"))
    print("TargetLanguageCode: " + result.get("TargetLanguageCode"))


def mic_callback(input_data, frame_count, time_info, status_flag):
    audio_queue.put_nowait(input_data)
    return (input_data, pyaudio.paContinue)


async def speech2text(
    key=config.deepgram.api_key,
    host=config.deepgram.host,
    version=config.deepgram.version,
    punctuate=config.deepgram.panctuate,
    model=config.deepgram.model,
    tier=config.deepgram.tier,
    language=config.deepgram.language,
    encoding=config.deepgram.encoding,
    sample_rate=config.deepgram.sample_rate,
):
    deepgram_url = host + "/" + version + "/listen?"
    deepgram_url += f"punctuate={punctuate}"
    deepgram_url += f"&model={model}"
    deepgram_url += f"&tier={tier}"
    deepgram_url += f"&language={language}"
    deepgram_url += f"&encoding={encoding}"
    deepgram_url += f"&sample_rate={sample_rate}"

    async with websockets.connect(
        deepgram_url, extra_headers={"Authorization": "Token {}".format(key)}
    ) as ws:
        info_queue.put(f'Info: Request ID: {ws.response_headers.get("dg-request-id")}.')
        info_queue.put("Info: Successfully opened streaming connection.")

        async def sender(ws):
            info_queue.put("Info: Ready to stream.")
            status_dict["record"] = status_codes["record_on"]
            info_queue.put("Info: Microphone is recording...")
            try:
                while True:
                    mic_data = await audio_queue.get()
                    all_mic_data.append(mic_data)
                    await ws.send(mic_data)
            except websockets.exceptions.ConnectionClosedOK:
                await ws.send(json.dumps({"type": "CloseStream"}))
                info_queue.put(
                    "Info: Successfully closed STT connection, waiting for final transcripts if necessary."
                )

            except Exception as e:
                info_queue.put(f"Error: while sending: {str(e)}")
                status_dict["record"] = status_codes["error"]
                raise
            return

        async def receiver(ws):
            first_message = True
            first_transcript = True
            transcript = ""
            async for msg in ws:
                res = json.loads(msg)
                if first_message:
                    info_queue.put("Info: Successfully receiving messages.")
                    first_message = False
                try:
                    if res.get("is_final"):
                        transcript = (
                            res.get("channel", {})
                            .get("alternatives", [{}])[0]
                            .get("transcript", "")
                        )
                        if transcript != "" and transcript != "Bin":
                            if first_transcript:
                                info_queue.put("Info: Begin receiving transcription.")
                                first_transcript = False
                            status_dict["stt"] = status_codes["get_data"]
                            translated_text = translate(transcript)
                            # print("Original: {}\nTranslated: {}\n".format(transcript,translate(transcript)))
                            recognize_queue.put(transcript)
                            translated_queue2.put(translated_text)
                            translated_queue.put(translated_text)
                            all_transcripts.append(transcript)

                        # if using the microphone, close stream if user says "goodbye"
                        if "goodbye" in transcript.lower():
                            await ws.send(json.dumps({"type": "CloseStream"}))
                            info_queue.put("Info: Successfully closed STT connection.")
                            status_dict["record"] = status_codes["record_off"]
                except KeyError:
                    info_queue.put(f"Error: Received unexpected API response! {msg}")
                    status_dict["record"] = status_codes["error"]

        async def microphone():
            ERROR_HANDLER_FUNC = CFUNCTYPE(
                None, c_char_p, c_int, c_char_p, c_int, c_char_p
            )

            def py_error_handler(filename, line, function, err, fmt):
                # print('messages are yummy')
                pass

            c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

            asound = cdll.LoadLibrary("libasound.so")
            asound.snd_lib_error_set_handler(c_error_handler)
            audio = pyaudio.PyAudio()
            asound.snd_lib_error_set_handler(None)

            stream = audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=mic_callback,
            )

            stream.start_stream()

            global SAMPLE_SIZE
            SAMPLE_SIZE = audio.get_sample_size(FORMAT)

            while stream.is_active():
                await asyncio.sleep(0.1)

            stream.stop_stream()
            stream.close()

        functions = [
            asyncio.ensure_future(sender(ws)),
            asyncio.ensure_future(receiver(ws)),
        ]

        functions.append(asyncio.ensure_future(microphone()))

        await asyncio.gather(*functions)


async def text_to_speech():
    # sourcery skip: remove-unnecessary-else, swap-if-else-branches
    while True:
        while not translated_queue.empty():
            status_dict["tts"] = status_codes["write"]
            _message = f"{translated_queue.get()}"
            info_queue.put("Info: Sending text data...")
            voice_id = config.elevenlabs.voice_id
            model = config.elevenlabs.model
            uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id={model}"

            async with websockets.connect(uri) as websocket:
                bos_message = {
                    "text": " ",
                    "voice_settings": {"stability": 0.5, "similarity_boost": True},
                    "xi_api_key": config.elevenlabs.api_key,  # Replace with your API key
                }
                await websocket.send(json.dumps(bos_message))

                status_dict["tts"] = status_codes["transfer"]
                input_message = {"text": f"{_message} ", "try_trigger_generation": True}
                await websocket.send(json.dumps(input_message))

                eos_message = {"text": ""}
                await websocket.send(json.dumps(eos_message))

                while True:
                    try:
                        response = await websocket.recv()
                        status_dict["tts"] = status_codes["get_data"]
                        data = json.loads(response)

                        if data.get("audio"):
                            chunk = base64.b64decode(data["audio"])

                            speech_queue.put(chunk)

                            if data["normalizedAlignment"] != None:
                                text = "".join(
                                    [
                                        str(i)
                                        for i in data["normalizedAlignment"]["chars"]
                                    ]
                                )
                                speech_queue2.put(text)
                            info_queue.put("Info: Receiving speech data...")
                        else:
                            break
                    except websockets.exceptions.ConnectionClosed:
                        info_queue.put("Warning: Elevenlabs connection closed.")
                        break
                status_dict["tts"] = status_codes["wait"]
        await asyncio.sleep(0.1)


def run_tts():
    asyncio.run(text_to_speech())


def run_stt():
    asyncio.run(speech2text())


def draw_menu(stdscr):  # sourcery skip: low-code-quality
    global recognize_text, translated_text, speech_text, info_text

    control = curses.initscr()
    curses.noecho()
    control.nodelay(1)

    k = 0
    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    section1 = f"SOURCE LANGUAGE [{config.setting.input_language}]"
    section2 = f"TARGET LANGUAGE [{config.setting.target_language}]"
    section3 = "SPEECH DATA"
    section4 = "PROCESS LOG"

    counter = 0

    while True:
        # Initialization

        height, width = stdscr.getmaxyx()
        cols_tot = width
        rows_tot = height
        cols_mid = int(cols_tot / 2)  # middle point of the stdscr
        rows_mid = int(rows_tot / 2)

        # Title
        program_title = "Transvoice {version}".format(
            version="v0.0.2 Alpha - press 'q' to exit"
        )
        program_title_center = int(
            (width // 2) - (len(program_title) // 2) - len(program_title) % 2
        )
        stdscr.attron(curses.color_pair(2))
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(0, program_title_center, program_title)

        statusbar = f"Device: {config.setting.output_device} | Input Lang: {config.setting.input_language} | Target Lang: {config.setting.target_language}\nVoice: {config.elevenlabs.voice_id} | Model: {config.elevenlabs.model}"
        stdscr.addstr(height - 2, 0, statusbar, curses.color_pair(7))

        pad11 = curses.newpad(rows_mid, cols_mid - 3)
        pad12 = curses.newpad(rows_mid, cols_mid)
        pad21 = curses.newpad(rows_mid, cols_mid - 3)
        pad22 = curses.newpad(rows_mid, cols_mid)

        section1_center = int((cols_mid / 2) - (len(section1) / 2) - len(section1) % 2)
        pad11.addstr(1, section1_center, section1, curses.color_pair(5))

        if len(recognize_text) >= 1000:
            recognize_text = ""
            translated_text = ""
            speech_text = ""
        if not recognize_queue.empty():
            recognize_text += f"{recognize_queue.get()} "
        pad11.addstr(3, 0, f"{recognize_text}")

        section2_center = int((cols_mid / 2) - (len(section2) / 2) - len(section2) % 2)
        pad12.addstr(1, section2_center, section2, curses.color_pair(4))

        if not translated_queue2.empty():
            translated_text += f"{translated_queue2.get()} "
        pad12.addstr(3, 0, f"{translated_text}")

        section3_center = int((cols_mid / 2) - (len(section3) / 2) - len(section3) % 2)
        pad21.addstr(0, section3_center, section3, curses.color_pair(6))

        if not speech_queue2.empty():
            speech_text += f"{speech_queue2.get()}"

        pad21.addstr(2, 0, f"{speech_text}")

        section4_center = int((cols_mid / 2) - (len(section4) / 2) - len(section4) % 2)
        pad22.addstr(0, section4_center, section4, curses.color_pair(1))

        if counter >= 20:
            info_text = ""
            counter = 0
        if not info_queue.empty():
            info_text += f"{info_queue.get()}\n"
            counter += 1

        pad22.addstr(2, 0, f"Virtual Device\t: {status_dict['device']}", curses.A_BOLD)
        pad22.addstr(3, 0, f"Record\t\t: {status_dict['record']}", curses.A_BOLD)
        pad22.addstr(4, 0, f"Speech to Text\t: {status_dict['stt']}", curses.A_BOLD)
        pad22.addstr(5, 0, f"Text to Speech\t: {status_dict['tts']}", curses.A_BOLD)
        pad22.addstr(6, 0, f"Audio Stream\t: {status_dict['stream']}", curses.A_BOLD)
        pad22.addstr(7, 0, "-" * 40)
        pad22.addstr(8, 0, f"{info_text}", curses.color_pair(4))

        pad11.refresh(0, 0, 1, 0, rows_mid, cols_mid - 3)

        pad12.refresh(0, 0, 1, cols_mid, rows_mid, cols_tot - 1)

        pad21.refresh(0, 0, rows_mid, 0, rows_tot - 1, cols_mid - 3)

        pad22.refresh(0, 0, rows_mid, cols_mid, rows_tot - 1, cols_tot - 1)

        # Refresh the screen
        stdscr.refresh()

        # Wait for next input
        k = control.getch()
        if k == ord("q"):
            virtualmic.unload_device(virtual_device_id)
            info_queue.put("Info: Exiting the program.")
            info_queue.put("Info: Unload virtual device.")
            info_queue.put("Serdar Eyup ALTIN: Good bye.")
            p0.kill()
            p1.kill()
            p2.kill()

            exit()
        time.sleep(0.1)


p0 = Process(target=run_tts)
p1 = Process(target=run_stt)

if __name__ == "__main__":
    info_queue.put("Info: Initializing...")

    info_queue.put("Info: Initializing virtual device...")
    status, virtual_device_id = virtualmic.load_device()
    if status:
        status_dict["device"] = status_codes["plug"]
        info_queue.put(f"Info: Virtual device id: {virtual_device_id}")
        config.setting.device_id = virtual_device_id
        config.save()
    else:
        status_dict["device"] = status_codes["error"]
        status_dict["stream"] = status_codes["warning"]
        info_queue.put(f"Error: {virtual_device_id}")
    p0.daemon = True
    p0.start()

    info_queue.put("Info: STT service is started.")
    p1.daemon = True
    p1.start()

    info_queue.put("Info: TTS service is started.")
    p2 = Process(target=stream_audio)
    p2.daemon = True
    p2.start()

    info_queue.put("Info: Stream service is started.")
    p3 = Process(target=curses.wrapper(draw_menu))
    p3.daemon = True
    p3.start()
    virtualmic.unload_device()
    info_queue.put("Info: Stopping virtual device.")
