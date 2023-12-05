import base64
from pathlib import Path
import streamlit as st
from ctypes import *
from config import config
from api import api

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def set_png_as_page_bg(png_file):
    bin_str = img_to_bytes(png_file)
    page_bg_img = (
        """
   <style>
   body {
   background-image: url("data:image/png;base64,%s");
   background-size: cover;
   }
   </style>
   """
        % bin_str
    )

    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

def save_settings():
    config.save()

def reset_settings():
    pass

def reload_settings():
    config.load()

def voice_add():
    print(api.elevenlabs.voice_add())

# set_png_as_page_bg("images/background.jpg")

# st.markdown(
#     f"""
#      <style>
#      .stApp {{
#          background: url(data:image/bacground.jpg;base64,{base64.b64encode(open("./images/background.jpg", "rb").read()).decode()});
#          background-repeat: no-repeat;
#          background-position: center;
#          width: 100%;
#          height: 100%;
#          background-color: black;
#          background-size: cover;
#      }}
#      </style>
#      """,
#     unsafe_allow_html=True,
# )

# --------------------------------------------------------------
# personal_details = st.markdown(
#    "<p style='text-align: left; color: gray;'>Personal Details</p>",
#    unsafe_allow_html=True,
# )
# --------------------------------------------------------------
# title_settings = st.markdown(
#    "<p style='text-align: left; color: gray;'>Settings</p>", unsafe_allow_html=True
# )

logo_url = "./images/translation.png"

# st.set_page_config(layout="wide")

css = """
   <style>
      .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
      font-size:1.2rem;
      margin-right:1rem;    
      }
      .column {
      float: left;
      width: 25%;
      }
      .row:after {
      content: "";
      display: table;
      clear: both;
      }
      div[data-baseweb="select"] > div {
      background-color: rgba(255,255,255,0.4);
      }
      div[role="listbox"] ul {
      background-color: red;
      }
   </style>
"""

# st.markdown(css, unsafe_allow_html=True)

tab_debug,tab_panel, tab_cloning, tab_info = st.tabs(
    [ "🪲Debug", "⚙️ Panel", "🎙️ Cloning", "ℹ️ Info"])

# sidebar ---------------------------------------------------------------
with st.sidebar:
    imgSideBar = st.image(logo_url, width=200)
    title = st.markdown(
        "<h1 style='text-align: center; color: #58a5ec; font-size:2rem;'>Transvoice</h1>",
        unsafe_allow_html=True,
    )
    # st.divider()
    st.header("", divider="rainbow")
    st.header("New Features")
    feature = st.markdown(
        """<p style='color: #b5b5b5; height:200px;'>
                         - Lorem Ipsum is simply dummy text of the printing and <b>typesetting</b> industry.<br>
                         - Lorem Ipsum has been the industry's <b>standard</b> dummy text ever since the 1500s,<br>
                         - There are many variations of <b>passages</b> of Lorem Ipsum available,<br>
                          </p>""",
        unsafe_allow_html=True,
    )

# tab panel -------------------------------------------------------------
with tab_panel:
    st.write()

    st.subheader("Personal Details", divider="rainbow")
    info_col1, info_col2, info_col3 = st.columns([1, 1, 1])

    with info_col1:
        st.caption("Selected Language")
        st.subheader(config.setting.source_language)

        st.caption("Delay")
        st.subheader("1.5s")

    with info_col2:
        st.caption("Translated Language")
        st.subheader(config.setting.target_language)

        st.caption("Used")
        st.subheader("2Hr")

    with info_col3:
        st.caption("Voice")
        st.subheader(config.setting.voice)

        st.caption("Credits Left")
        st.subheader("80%")

    st.subheader("Devices", divider="gray")
    (
        input_device,
        output_device,
        record_quality,
    ) = st.columns([1, 1, 1])
    with input_device:
        input_device = st.selectbox(
            key="input_device",
            label="Input Device",
            options=([config.setting.input_device]),
            index=0,
            disabled=True,
        )
    with output_device:
        output_device = st.selectbox(
            key="output_device",
            label="Output Device",
            options=([config.setting.output_device]),
            index=0,
            disabled= True,
        )
    with record_quality:
        output_device = st.selectbox(
            key="record_quality",
            label="Record Quality ",
            options=([config.setting.record_quality]),
            index=0,
            disabled= True,
        )

    # --------------------------------------------------------------
    st.subheader("Source Voice", divider="gray")
    (input_language, Null) = st.columns([3, 1])

    with input_language:
        input_language = st.selectbox(
            key="input_language",
            label="Input Language",
            options=(api.aws_translate.languages),
            index=0,
        )

    # --------------------------------------------------------------
    st.subheader("Target Voice", divider="gray")

    (ai_model, target_language, voice) = st.columns([1, 1, 1])
    with ai_model:
        ai_model = st.selectbox(
            key="ai_model",
            label="AI Model",
            options=(api.elevenlabs.models_names),
            index=0,
        )
    with target_language:
        target_language = st.selectbox(
            key="target_language",
            label="Target Language",
            options=(api.aws_translate.languages),
            index=0,
        )
    with voice:
        # st.subheader("Cloned Voice")
        cloned_voice = st.selectbox(
            key="cloned_voice",
            label="Voice",
            options=(api.elevenlabs.voice_names),
            index=0,
        )

    (
        col_voice_quality,
        col_voice_optimizing,
        col_speaker_boost,
    ) = st.columns([1, 1, 1])
    with col_voice_quality:
        voice_quality = st.selectbox(
            key="voice_quality",
            label="Quality",
            options=(api.elevenlabs.output_format.keys()),
            index=0,
        )
    with col_voice_optimizing:
        voice_stability = st.slider("Optimizing", 0, 4, 0)
    with col_speaker_boost:
        st.text("Speaker Boost")
        speaker_boost = st.toggle(key="speaker_boost", label="Disable")
        if speaker_boost:
            st.write(label="Active", key="speaker_boost")

    (
        voice_stability,
        voice_similarty,
        voice_style,
    ) = st.columns([1, 1, 1])
    
    with voice_stability:
        voice_stability = st.slider("Stability", 0, 100, 30)
    with voice_similarty:
        voice_similarty = st.slider("Clarity + Similarity", 0, 100, 29)
    with voice_style:
        voice_quality = st.slider("Style", 0, 100, 0)

    # --------------------------------------------------------------
    st.subheader("Options", divider="rainbow")

    (options_save, options_reload, options_reset) = st.columns((1, 1, 1))
    with options_save:
        btn_save = st.button(
            key="save", label="SAVE SETTINGS", on_click=save_settings, type="primary"
        )
    with options_reset:
        btn_reset = st.button(
            key="reset", label="RESET SETTINGS", on_click=reset_settings
        )
    with options_reload:
        btn_reset = st.button(
            key="reload", label="RELOAD SETTINGS", on_click=reload_settings
        )

# cloning tab -----------------------------------------------------------
with tab_cloning:
    # title_add_voice = st.markdown(
    #    "<p style='text-align: left; color: gray;'>Add Voice</p>",
    #    unsafe_allow_html=True,
    # )
    st.subheader("Add Voice", divider="rainbow")

    txt_voice_name = st.text_input(
        key="voice_name", label="Name", placeholder="Cloning Voice Name"
    )
    uploaded_voice = st.file_uploader("Audio or Video files, up to 10MB each", type=["mp3","wav"])

    txt_description = st.text_area(
        key="description",
        label="Description",
        placeholder='How would you describe the voice? e.g. "An old American male voice with a slight hoarseness in his throat. Perfect for news."',
    )
    st.header("", divider="rainbow")
    agree = st.checkbox(
        "I hereby confirm that I have all necessary rights or consents to upload and clone these voice samples and that I will not use the platform-generated content for any illegal, fraudulent, or harmful purpose. I reaffirm my obligation to abide by ElevenLabs’ Terms of Service and Privacy Policy."
    )

    btn_add_voice = st.button(
        key="add_voice", label="Add Voice", disabled=False, on_click=voice_add)
    


# info tab --------------------------------------------------------------
with tab_info:
    title_info = st.markdown(
        "<p style='text-align: left; color: gray;'>Info</p>", unsafe_allow_html=True
    )
    st.image(logo_url, width=200)
    st.header("", divider="rainbow")
    info = st.markdown(
        """Lorem Ipsum is simply dummy text of the printing and typesetting industry.
      Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
      when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries,
      but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages,
      and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."""
    )

    info = st.markdown(
        """Lorem Ipsum is simply dummy text of the printing and typesetting industry.
      Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
      when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries,
      but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing."""
    )

# info debug --------------------------------------------------------------
with tab_debug:
    col1_info, col2_info, col3_info  = st.columns([1,1,1])
    with col1_info:
        st.caption("Source Language: :green[{}] (:blue[{}])".format(config.setting.source_language,config.setting.source_language_code))
        st.caption("Target Language: :green[{}] (:blue[{}])".format(config.setting.target_language,config.setting.target_language_code))
        st.caption("Voice Model: :green[{}](:blue[{}...])".format(config.setting.voice,config.elevenlabs.voice_id[:12]))
    
    with col2_info:
        st.caption("Input Device: :green[{}]".format(config.setting.input_device))
        st.caption("Output Device: :green[{}]".format(config.setting.output_device))
        st.caption("Virtual Device Id: :green[{}]".format(config.setting.device_id))
    
    with col3_info:
        st.caption("Recoid Quality: :green[{}]".format(config.setting.record_quality))
        st.caption("Voice Quality: :green[{}]".format(config.setting.voice_quality))
        st.caption("Optimizing: :green[{}]".format("..."))
    
   
    col_input_text, col_target_text = st.columns([1,1])
    
    with col_input_text:
        if "recognize_text" not in st.session_state:
            st.session_state["recognize_text"] = ""
            
        txt_input_text = st.text_area(value=st.session_state["recognize_text"],key="txt_input_text", label="Source Text", height=300, disabled= True)
   
    with col_target_text:
        txt_target_text = st.text_area(key="txt_target_text", label="Target Text", height=300, disabled= True)

    col_speech_voice, col_process = st.columns([1,1])
    
    with col_speech_voice:
        txt_speech = st.text_area(key="txt_speech", label="Speech", height=300, disabled= True)

    with col_process:
        txt_process = st.text_area(key="txt_process", label="Process", height=300, disabled= True)



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
    text, source=config.setting.source_language_code, target=config.setting.target_language_code
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


def debug():
    global recognize_text, translated_text, speech_text, info_text
    while True:
        if not recognize_queue.empty():
            recognize_text += f"{recognize_queue.get()} "
            
        if not translated_queue2.empty():
            translated_text += f"{translated_queue2.get()} "
            
        if not speech_queue2.empty():
            speech_text += f"{speech_queue2.get()}"
            
        if not info_queue.empty():
            info_text += f"{info_queue.get()}\n"
            
        st.session_state["recognize_text"] = recognize_text
        
        st.rerun()
        time.sleep(0.2)

p0 = Process(target=run_tts)
p1 = Process(target=run_stt)

if __name__ == "__main__":
    info_queue.put("Info: Initializing...")

    info_queue.put("Info: Initializing virtual device...")
    # status, virtual_device_id = virtualmic.load_device()
    # if status:
    #     status_dict["device"] = status_codes["plug"]
    #     info_queue.put(f"Info: Virtual device id: {virtual_device_id}")
    #     config.setting.device_id = virtual_device_id
    #     config.save()
    # else:
    #     status_dict["device"] = status_codes["error"]
    #     status_dict["stream"] = status_codes["warning"]
    #     info_queue.put(f"Error: {virtual_device_id}")
    
    #p0.daemon = True
    #p0.start()

    info_queue.put("Info: STT service is started.")
    #p1.daemon = True
    #p1.start()

    info_queue.put("Info: TTS service is started.")
    p2 = Process(target=stream_audio)
    #p2.daemon = True
    #p2.start()

    info_queue.put("Info: Stream service is started.")
    #p3 = Process(target=debug())
    #p3.daemon = True
    #p3.start()
    
    #virtualmic.unload_device(virtual_device_id)
    info_queue.put("Info: Exiting the program.")
    info_queue.put("Info: Unload virtual device.")
    info_queue.put("Serdar Eyup ALTIN: Good bye.")
    # p0.kill()
    # p1.kill()
    # p2.kill()
    #virtualmic.unload_device()
    info_queue.put("Info: Stopping virtual device.")
