import re
import os
import json
import requests
from urllib.parse import urljoin
from config import config


class Preset(object):
    preset = {
        "file": {
            "api": "api.json",
        },
        "elevenlabs": {"tags": {"voices": "voices"}},
    }

    def __init__(self):
        self.file = self.File(self.preset["file"])

    def __repr__(self):
        return repr(self.preset)

    class File(object):
        def __init__(self, value):
            self.file = value

        def __repr__(self):
            return repr(self.file)

        @property
        def api(self):
            return self.file["api"]


preset = Preset()


class Api(object):
    api_file = preset.file.api
    api = None

    def __init__(self):
        self.load()
        self.elevenlabs = self.Elevenlabs(self.api["elevenlabs"])
        self.aws_translate = self.Aws_Translate(self.api["aws_translate"])
        self.deepgram = self.Deepgram(self.api["deepgram"])

    def __repr__(self):
        return repr(self.api)

    class Deepgram(object):
        def __init__(self, value):
            self.deepgram = value

        def __repr__(self):
            return repr(self.deepgram)

        @property
        def host(self):
            return self.deepgram["host"]

        @host.setter
        def host(self, value):
            self.deepgram["host"] = value

        @property
        def version(self):
            return self.deepgram["version"]

        @version.setter
        def version(self, value):
            self.deepgram["version"] = value

    class Aws_Translate(object):
        def __init__(self, value):
            self.aws_translate = value

        def __repr__(self):
            return repr(self.aws_translate)

        @property
        def supported_languages(self):
            return self.aws_translate["supported_languages"]

        @supported_languages.setter
        def supported_languages(self, value):
            self.aws_translate["supported_languages"] = value

        @property
        def languages(self):
            return self.aws_translate["supported_languages"].keys()

    class Elevenlabs(object):
        def __init__(self, value):
            self.elevenlabs = value

        def __repr__(self):
            return repr(self.elevenlabs)

        @property
        def url(self):
            self.elevenlabs["url"] = urljoin(self.elevenlabs["url"], self.version)
            return self.elevenlabs["url"]

        @url.setter
        def url(self, value):
            self.elevenlabs["url"] = value

        @property
        def version(self):
            return self.elevenlabs["version"]

        @version.setter
        def version(self, value):
            self.elevenlabs["version"] = value

        @property
        def voices(self):
            voices_url = urljoin(self.url + "/", "voices")
            headers = {"xi-api-key": config.elevenlabs.api_key}
            response = requests.request("GET", voices_url, headers=headers).text
            try:
                self.elevenlabs["voices"] = json.loads(response)["voices"]
            except:
                pass
            return self.elevenlabs["voices"]

        @voices.setter
        def voices(self, value):
            self.elevenlabs["voices"] = value

        @property
        def voice_names(self):
            voices = []
            for voice in self.elevenlabs["voices"]:
                voices.append(voice["name"])
            return voices

        @property
        def models(self):
            models_url = urljoin(self.url + "/", "models")
            headers = {"xi-api-key": config.elevenlabs.api_key}
            response = requests.request("GET", models_url, headers=headers).text
            try:
                self.elevenlabs["models"] = json.loads(response)
            except:
                pass
            return self.elevenlabs["models"]

        @models.setter
        def models(self, value):
            self.elevenlabs["models"] = value

        @property
        def models_names(self):
            elements = []
            elements.append("Auto")
            for element in self.elevenlabs["models"]:
                _eleven = re.search("Eleven", element["name"])
                elements.append(element["name"][_eleven.end() :])
            return elements

        @property
        def output_format(self):
            return self.elevenlabs["output_format"]

        @output_format.setter
        def output_format(self, value):
            self.elevenlabs["output_format"] = value

        def voice_add(self):
            voices_url = urljoin(self.url + "/", "voices")
            voices_url = urljoin(voices_url + "/", "add")

            headers = {
                "xi-api-key": config.elevenlabs.api_key
                
            }
            files = {'file': open('/home/main/Project/STS-Voice-Translation/samples/audios/tr-masal.mp3', 'rb')}
            form_data = {
               "name": "Test1",
               "description": "Test11",
               "files": files
            }
            response = requests.request(
                method="POST",url=voices_url, data=form_data, headers=headers).text
            try:
                response = json.loads(response)["voice_id"]
            except:
                pass
            return response

    def save(self):
        with open(self.api_file, "w") as outfile:
            outfile.write(json.dumps(self.api, indent=4))

    def load(self):
        if (
            os.path.exists(self.api_file) == False
            or open(self.api_file, "r").read() == ""
        ):
            self.save()
        with open(self.api_file, "r") as openfile:
            self.api = json.load(openfile)
        return repr(self.api)


api = Api()
