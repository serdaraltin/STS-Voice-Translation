import re
import os
import json
import requests
from urllib.parse import urljoin
from config import config


class Preset(object):
    preset = {
        "file": {
            "resource": "resource.json",
        }
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
        def resource(self):
            return self.file["resource"]


preset = Preset()


class Resource(object):
    resource_file = preset.file.resource
    resource = None

    def __init__(self):
        self.load()
        self.path = self.Path(self.resource["path"])

    def __repr__(self):
        return repr(self.resource)

    class Path(object):
        def __init__(self, value):
            self.path = value

        def __repr__(self):
            return repr(self.path)

        @property
        def logo(self):
            return self.path["logo"]

        @logo.setter
        def logo(self, value):
            self.path["logo"] = value

     

    def save(self):
        with open(self.resource_file, "w") as outfile:
            outfile.write(json.dumps(self.resource, indent=4))

    def load(self):
        if (
            os.path.exists(self.resource_file) == False
            or open(self.resource_file, "r").read() == ""
        ):
            self.save()
        with open(self.resource_file, "r") as openfile:
            self.resource = json.load(openfile)
        return repr(self.resource)


resource = Resource()
