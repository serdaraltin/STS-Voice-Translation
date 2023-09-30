from config import config
from virtual_device import virtualmic

from time import time, sleep
import azure.cognitiveservices.speech as speechsdk
from elevenlabs import generate, set_api_key


class Transvoice(object):
    
    def __init__(self) -> None:
        pass
    
    def __repr__(self) -> str:
        pass
    
    def realtime_recognize(self, _recognition_language=config.setting.input_language, _target_language=config.setting.target_language):
    
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

    def text_to_speech(self, _input_text, _voice=config.elevenlabs.voice):
        set_api_key(config.elevenlabs.api_key)
        audio = generate(text=_input_text, voice=_voice, model=config.elevenlabs.model)

        return audio

    def speech_translate(self):
        start_time = time()
        speech_recognition_result = self.realtime_recognize()
        recognition_time = time()
        print("Recognition and Translation: {}s\n".format(round(recognition_time-start_time, 2)))
        
        audio = self.text_to_speech(speech_recognition_result)
        speech_time = time()
        
        print("Text to Speech: {}s\n".format(round(speech_time-recognition_time, 2)))
        print("Elapsed time: {}s\n\n".format(round(speech_time-start_time, 2)))
        
        with open("export.mp3", "wb") as file:
            file.write(audio)
    
        virtualmic.stream_audio("export.mp3")
        


if __name__ == "__main__":
    virtualmic.load_device()
    Transvoice().speech_translate()
    sleep(1)
    virtualmic.unload_device()



