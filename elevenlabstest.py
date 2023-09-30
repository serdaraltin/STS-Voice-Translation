import asyncio
import subprocess
import websockets
import json
import base64
from config import config, preset
import azure.cognitiveservices.speech as speechsdk


    
def realtime_recognize(_recognition_language=config.setting.input_language, _target_language=config.setting.target_language):
    speech_translation_config = speechsdk.translation.SpeechTranslationConfig(subscription=config.azure.speech_key, region=config.azure.region)
    speech_translation_config.speech_recognition_language=_recognition_language

    target_language=_target_language
    speech_translation_config.add_target_language(target_language)

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    translation_recognizer = speechsdk.translation.TranslationRecognizer(translation_config=speech_translation_config, audio_config=audio_config)

    print("Speak into your microphone.")
    translation_recognition_result = translation_recognizer.recognize_once_async().get()

    if translation_recognition_result.reason == speechsdk.ResultReason.TranslatedSpeech:
        print("\nRecognized: {}".format(translation_recognition_result.text))
        print("Translated: {}".format(translation_recognition_result.translations[target_language]))
        return translation_recognition_result.translations[target_language]
    elif translation_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(translation_recognition_result.no_match_details))
    elif translation_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = translation_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")


queue = asyncio.Queue()

#buffer yapılacak
async def stream_audio_binary():
    while True:
        if not queue.empty():
            while not queue.empty():
                data = queue.get_nowait()
                with open(preset.file.virtual_stream, "wb") as audio_file:
                    audio_file.write(data)
                    
                ffmpeg_stream = [
                    'ffmpeg',
                    '-re',
                    '-i',
                    '{}'.format(preset.file.virtual_stream),
                    '-f', 's16le',
                    '-ar', '16000',
                    '-ac', '1',
                    '-loglevel',
                    'error',
                    '-'
                ]
                
                with subprocess.Popen(ffmpeg_stream, stdout=subprocess.PIPE) as ffmpeg_process:
                    while True:
                        audio_data = ffmpeg_process.stdout.read(1024)
                        if not audio_data:
                            break
                        with open(preset.file.virtual_input, 'wb') as virtmic:
                            virtmic.write(audio_data)
                    print("Writed the audio data.")
                queue.task_done()
                await asyncio.sleep(.1)
        await asyncio.sleep(.2)
        
async def text_to_speech():
    while True:
        _message = realtime_recognize()
        voice_id = "21m00Tcm4TlvDq8ikWAM"
        model = 'eleven_monolingual_v1'
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

            # Send "Hello World" input
            input_message = {
                "text": "{} ".format(_message),
                "try_trigger_generation": True
            }
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
                    data = json.loads(response)
                    #print("Server response:", data)

                    if data["audio"]:                  
                        chunk = base64.b64decode(data["audio"])     
                        queue.put_nowait(chunk)
                        
                        print("Received audio chunk")
                    else:
                        print("No audio data in the response")
                        break
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed")
                    break
        await asyncio.sleep(.5)

async def main():

    f1 = loop.create_task(text_to_speech())
    f2 = loop.create_task(stream_audio_binary())
    await asyncio.wait([f1, f2])

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()