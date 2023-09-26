import os
import time
import requests, uuid
import azure.cognitiveservices.speech as speechsdk

azure_speech_key = ""
azure_region = "northeurope"

azure_translate_key = ""
azure_translate_endpoint = "https://api.cognitive.microsofttranslator.com"

elevenlabs_api_key = ""
elevenlabs_voice_id = "pNInz6obpgDQGcFmaJgB"

export_audio = "export.mp3"

def realtime_recognize(_speech_recognition_language="tr-TR"):
    
    speech_config = speechsdk.SpeechConfig(subscription=azure_speech_key, region=azure_region)
    speech_config.speech_recognition_language=_speech_recognition_language
    #speech_config.set_property_by_name("OPENSSL_DISABLE_CRL_CHECK", "true") 

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("Speak into your microphone.\n")
    start_time = time.time()
    speech_recognition_result = speech_recognizer.recognize_once_async().get()
    
    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:

        print("Recognized: {}".format(speech_recognition_result.text))
        return "{}".format(speech_recognition_result.text)
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
        return False
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
        return False


def text_translate(_text, _original_language="tr",_target_language="en"):
    
    params= {
        'api-version': '3.0',
        'from': '{original_language}'.format(original_language=_original_language),
        'to': ['{target_language}'.format(target_language=_target_language)]
    }
    headers = {
        'Ocp-Apim-Subscription-Key': azure_translate_key,
        'Ocp-Apim-Subscription-Region': azure_region,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    
    body = [{
        'text': '{text}'.format(text=_text)
    }]
    
    path = '/translate'
    constructed_url = azure_translate_endpoint + "/translate"
    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()
    translate_data = response[0]['translations'][0]['text'] #json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))
    print("Translated: {translate_data}".format(translate_data=translate_data))
    return translate_data


def text_to_speech(_input_text, _export_audio="export.mp3", _voice_id=elevenlabs_voice_id):
    
    url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}".format(voice_id=_voice_id)

    headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": "{api_key}".format(api_key=elevenlabs_api_key)
    }

    data = {
    "text": "{input_text}".format(input_text=_input_text),
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
    }
    }

    response = requests.post(url, json=data, headers=headers)
    with open('{export_audio}'.format(export_audio=_export_audio), 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
        print("Translated speech: {export_audio}".format(export_audio=_export_audio))


def speech_translate():
    start_time = time.time()
    speech_recognition_result = realtime_recognize()
    recognition_time = time.time()
    print("Recognition time: {}s\n".format(round(recognition_time-start_time, 2)))
    
    text_translate_result = text_translate(speech_recognition_result, "tr", "en")
    translation_time = time.time()
    print("Translation time: {}s\n".format(round(translation_time-recognition_time, 2)))
    
    text_to_speech(text_translate_result,export_audio)
    speech_time = time.time()
    print("Speech time: {}s\n".format(round(speech_time-translation_time, 2)))
    
    print("Elapsed time: {}s\n\n".format(round(speech_time-start_time, 2)))
    
    os.system("mpg123 " + export_audio)


speech_translate()
