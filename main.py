from config import config
import time
import azure.cognitiveservices.speech as speechsdk
from elevenlabs import play, generate, set_api_key
    

azure_speech_key = config.azure.speech_key
azure_region = config.azure.region

elevenlabs_api_key = config.elevenlabs.api_key
elevenlabs_voice = config.elevenlabs.voice

def realtime_recognize(_recognition_language="tr-TR", _target_language="en"):
    
    speech_translation_config = speechsdk.translation.SpeechTranslationConfig(subscription=azure_speech_key, region=azure_region)
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

def text_to_speech(_input_text, _voice=elevenlabs_voice):
    set_api_key(elevenlabs_api_key)
    audio = generate(text=_input_text, voice=_voice, model="eleven_multilingual_v2")

    return audio

def speech_translate():
    start_time = time.time()
    speech_recognition_result = realtime_recognize()
    recognition_time = time.time()
    print("Recognition and Translation: {}s\n".format(round(recognition_time-start_time, 2)))
    
    audio = text_to_speech(speech_recognition_result)
    speech_time = time.time()
    
    print("Text to Speech: {}s\n".format(round(speech_time-recognition_time, 2)))
    print("Elapsed time: {}s\n\n".format(round(speech_time-start_time, 2)))
    play(audio)

#speech_translate()


