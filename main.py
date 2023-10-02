import asyncio
import subprocess
import websockets
import json
import base64
import time
import curses
from config import config, preset
from virtual_device import virtualmic

from multiprocessing import Process, Queue, Manager
import azure.cognitiveservices.speech as speechsdk

virtual_device_id = 0

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

status_codes = {"record_on":"🔴",
                "sound": "🔊",
                "mail":"📨",
                "success":"✅",
                "write":"📄",
                "transfer":"🔃",
                "plug":"🔌",
                "record_off":"⚫",
                "speech":"🗣️",
                "wait":"⌛",
                "get_data":"📡",
                "download": "📥",
                "error":"❌",
                "warning":"⚠️",
                "skull": "☠️"
                }

manager = Manager()
status_dict = manager.dict()

status_dict["device"] = status_codes["wait"]
status_dict["record"] = status_codes["record_off"]
status_dict["stt"] = status_codes["wait"]
status_dict["tts"] = status_codes["wait"]
status_dict["stream"] = status_codes["wait"]



#buffer yapılacak
def stream_audio():
    ffmpeg_stream = [
        'ffmpeg',
        '-re',
        '-i',
        f'{preset.file.virtual_stream}',
        '-f',
        's16le',
        '-ar',
        '16000',
        '-ac',
        '1',
        '-loglevel',
        'error',
        '-',
    ]
    while True:
        while not speech_queue.empty():
            info_queue.put("Info: Speech is playing...")
            status_dict['stream'] = status_codes["speech"]
            
            data = speech_queue.get()
            with open(preset.file.virtual_stream, "wb") as audio_file:
                audio_file.write(data)
     
            with subprocess.Popen(ffmpeg_stream, stdout=subprocess.PIPE) as ffmpeg_process:
               
                while True:
                    audio_data = ffmpeg_process.stdout.read(128)
                    if not audio_data:
                        break
                    with open(preset.file.virtual_input, 'ab') as virtmic:
                        virtmic.write(audio_data)
            status_dict['stream'] = status_codes["wait"]
        time.sleep(.1)        

def speech_to_text():

    while True:
        
        status_dict['record'] = status_codes["record_on"]
        info_queue.put("Info: Microphone is recording...")

        speech_config = speechsdk.translation.SpeechTranslationConfig(subscription=config.azure.speech_key, region=config.azure.region)
        speech_config.speech_recognition_language=config.setting.input_language
        speech_config.add_target_language(config.setting.target_language)
        status_dict['stt'] = status_codes["get_data"]
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        recognizer = speechsdk.translation.TranslationRecognizer(translation_config=speech_config, audio_config=audio_config)


        result = recognizer.recognize_once_async().get()
        status_dict['record'] = status_codes["record_off"]
        if result.reason == speechsdk.ResultReason.TranslatedSpeech:
            #print("\nRecognized: {}".format(result.text))
            #print("Translated: {}\n".format(text))
            recognize_queue.put(result.text)
            translated_queue.put(result.translations[config.setting.target_language])
            translated_queue2.put(result.translations[config.setting.target_language])
            info_queue.put("Info: Recording translated.")
        elif result.reason == speechsdk.ResultReason.NoMatch:
            #print("No speech could be recognized: {}".format(result.no_match_details))
            info_queue.put("Warning: No speech detected!")# {result.no_match_details}
            status_dict['record'] = status_codes["record_off"]
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            #print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            info_queue.put(f"Warning: Speech recognition canceled: {cancellation_details.reason}")
            status_dict['record'] = status_codes["warning"]
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                info_queue.put(f"Error: {cancellation_details.error_details}")
                status_dict['record'] = status_codes["error"]
                # print("Error details: {}".format(cancellation_details.error_details))

async def text_to_speech():
    # sourcery skip: remove-unnecessary-else, swap-if-else-branches
    while True:
        while not translated_queue.empty():
            
            status_dict['tts'] = status_codes["write"]
            _message = f"{translated_queue.get()} "
            info_queue.put("Info: Sending text data...")
            voice_id = config.elevenlabs.voice_id
            model = config.elevenlabs.model
            uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id={model}"

            async with websockets.connect(uri) as websocket:
                
                # Initialize the connection
                bos_message = {
                    "text": " ",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": True
                    },
                    "xi_api_key": config.elevenlabs.api_key,  # Replace with your API key
                }
                await websocket.send(json.dumps(bos_message))

                status_dict['tts'] = status_codes["transfer"]
                input_message = {"text": f"{_message} ", "try_trigger_generation": True}
                await websocket.send(json.dumps(input_message))

                # Send EOS message with an empty string instead of a single space
                # as mentioned in the documentation
                eos_message = {
                    "text": ""
                }
                await websocket.send(json.dumps(eos_message))

                # Added a loop to handle server responses and print the data received
                while True:
                    try:
                        response = await websocket.recv()
                        status_dict['tts'] = status_codes["get_data"]
                        data = json.loads(response)

                        if data["audio"]:                  
                            chunk = base64.b64decode(data["audio"])     
                            
                            speech_queue.put(chunk)

                            if data["normalizedAlignment"] != None:
                                text = "".join([str(i) for i in data["normalizedAlignment"]["chars"]])
                                speech_queue2.put(text)
                               
                            info_queue.put("Info: Receiving speech data...")
                        else:
                            #print("No audio data in the response.")
                            break
                    except websockets.exceptions.ConnectionClosed:
                        info_queue.put("Warning: Elevenlabs connection closed.")
                        break
                status_dict['tts'] = status_codes["wait"]
        await asyncio.sleep(.1)

def run_tts():
    asyncio.run(text_to_speech())


p0 = Process(target=run_tts)
p1 = Process(target=speech_to_text)


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


    section1 = f"ORIGINAL LANGUAGE [{config.setting.input_language}]"
    section2 = f"TARGET LANGUAGE [{config.setting.target_language}]"
    section3 = "SPEECH DATA"
    section4 = "PROCESS LOG"


    counter = 0

    while True:
        # Initialization

        height, width = stdscr.getmaxyx()
        cols_tot = width
        rows_tot = height
        cols_mid = int(cols_tot/2)  # middle point of the stdscr
        rows_mid = int(rows_tot/2)


        # Title
        program_title = "Transvoice {version}".format(version="v0.0.1 Alpha - press 'q' to exit")
        program_title_center = int((width // 2) - (len(program_title) // 2) - len(program_title) % 2)
        stdscr.attron(curses.color_pair(2))
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(0,program_title_center, program_title)

        statusbar = f"Device: {config.setting.output_device} | Input Lang: {config.setting.input_language} | Target Lang: {config.setting.target_language}\nVoice: {config.elevenlabs.voice_id} | Model: {config.elevenlabs.model}"
        stdscr.addstr(height-2, 0, statusbar, curses.color_pair(7))

        pad11 = curses.newpad(rows_mid, cols_mid-3)
        pad12 = curses.newpad(rows_mid, cols_mid)
        pad21 = curses.newpad(rows_mid, cols_mid-3)
        pad22 = curses.newpad(rows_mid, cols_mid)

        
        section1_center = int((cols_mid / 2) - (len(section1) / 2) - len(section1) % 2)
        pad11.addstr(1, section1_center , section1, curses.color_pair(5))

        if len(recognize_text) >= 1000:
            recognize_text = ""
            translated_text = ""
            speech_text = ""
        if not recognize_queue.empty():
            recognize_text += f"{recognize_queue.get()} "
        pad11.addstr(3, 0, f"{recognize_text}")

        section2_center = int((cols_mid / 2) - (len(section2) / 2) - len(section2) % 2)
        pad12.addstr(1, section2_center , section2, curses.color_pair(4))

        if not translated_queue2.empty():
            translated_text += f"{translated_queue2.get()} "
        pad12.addstr(3, 0, f"{translated_text}")


        section3_center = int((cols_mid / 2) - (len(section3) / 2) - len(section3) % 2)
        pad21.addstr(0, section3_center , section3, curses.color_pair(6))

        if not speech_queue2.empty():
            speech_text += f"{speech_queue2.get()}"

        pad21.addstr(2, 0, f"{speech_text}")


        section4_center = int((cols_mid / 2) - (len(section4) / 2) - len(section4) % 2)
        pad22.addstr(0, section4_center , section4, curses.color_pair(1))

        if len(info_text) >= 400 or counter >= 150:
            info_text = ""
            counter = 0
        if not info_queue.empty():
            info_text += f"{info_queue.get()}\n"
        else:
            counter += 1

        
        pad22.addstr( 2,0,f"Virtual Device\t: {status_dict['device']}", curses.A_BOLD)
        pad22.addstr(3, 0, f"Record\t\t: {status_dict['record']}", curses.A_BOLD)
        pad22.addstr(4, 0, f"Speech to Text\t: {status_dict['stt']}", curses.A_BOLD)
        pad22.addstr(5, 0, f"Text to Speech\t: {status_dict['tts']}", curses.A_BOLD)
        pad22.addstr(6, 0, f"Audio Stream\t: {status_dict['stream']}", curses.A_BOLD)
        pad22.addstr(7, 0, "-"*40)
        pad22.addstr(8, 0, f"{info_text}", curses.color_pair(4))


        pad11.refresh(0, 0, 1, 0, rows_mid, cols_mid-3)

        pad12.refresh(0, 0, 1, cols_mid, rows_mid, cols_tot-1)

        pad21.refresh(0, 0, rows_mid, 0, rows_tot-1, cols_mid-3)

        pad22.refresh(0, 0, rows_mid, cols_mid, rows_tot-1, cols_tot-1)


        # Refresh the screen
        stdscr.refresh()

        # Wait for next input
        k = control.getch()
        if (k == ord('q')):
            virtualmic.unload_device()
            info_queue.put("Info: Exiting the program.")
            info_queue.put("Info: Unload virtual device.")
            info_queue.put("Serdar Eyup ALTIN: Good bye.")
            p0.kill()
            p1.kill()
            p2.kill()
       
            exit()
        time.sleep(.1)
      
if __name__ == "__main__":

    info_queue.put("Info: Initializing...")
     
    info_queue.put("Info: Initializing virtual device...")
    status,retval = virtualmic.load_device()
    if status:
        status_dict["device"] = status_codes["plug"]
        info_queue.put(f"Info: Virtual device id: {retval}")
    else:
        status_dict["device"] = status_codes["error"]
        status_dict["stream"] = status_codes["warning"]
        info_queue.put(f"Error: {retval}")
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


