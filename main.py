import os
import time 
import requests
import openai


start_time = time.time()

openai.api_key = ""
speech_key = ""
service_region = "northeurope"

import_audio="masal.mp3"
export_audio="translated_audio.mp3"


with open(import_audio, "rb") as audio_file:
    transcript = openai.Audio.transcribe(
        file = audio_file,
        model= "whisper-1",
        response_format="text",
        language="en"
    )


print("Speech to Text: {original_text}\n".format(original_text=transcript))


response = openai.ChatCompletion.create(
  model="gpt-4",
  messages=[
      {
          "role": "user",
          "content": "translate this text to English: {text}".format(text=transcript)
      }
      ],
  temperature=0,
  max_tokens=256
)

translate = response['choices'][0]['message']['content']

print("Translate Text: {translate}\n".format(translate=translate))



url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}".format(voice_id="pNInz6obpgDQGcFmaJgB")

headers = {
  "Accept": "audio/mpeg",
  "Content-Type": "application/json",
  "xi-api-key": "{api_key}".format(api_key="6271905524fb3f8f865f9dfeaabbfe33")
}

data = {
  "text": "{input_text}".format(input_text=transcript),
  "model_id": "eleven_monolingual_v1",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.5
  }
}

response = requests.post(url, json=data, headers=headers)
with open('{export_audio}'.format(export_audio=export_audio), 'wb') as f:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk)
    print("Translated speech has been created.\n")

end_time = time.time()

print("Elapsed time: {seconds}s\n".format(seconds=round(end_time-start_time,2)))


os.system("mpg123 " + export_audio)