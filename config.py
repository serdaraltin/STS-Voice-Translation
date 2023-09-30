import os
import json

os.environ["SSL_CERT_DIR"]="/etc/ssl/certs"

class Preset(object):
    preset = {
        'file': {
            "config": "config.json",
            "logo": "./images/record2-fill.svg",
            "virtual_input": "/tmp/transvoicemic",
            "virtual_stream": "/tmp/stream_audio"
        }
    }

    def __init__(self):
        self.file = self.File(self.preset['file'])

    def __repr__(self):
        return repr(self.preset)


    class File(object):
        def __init__(self, value):
            self.file = value

        def __repr__(self):
            return repr(self.file)
        
        @property
        def config(self):
            return self.file['config']
        
        @property
        def logo(self):
            return self.file['logo']
        
        @property
        def virtual_input(self):
            return self.file['virtual_input']
        
        @property
        def virtual_stream(self):
            return self.file['virtual_stream']
        
preset = Preset()


class Config(object):
    config_file = preset.file.config
    config = None
    
    def __init__(self):
        self.read()
        self.setting = self.Setting(self.config['setting'])
        self.azure = self.Azure(self.config['azure'])
        self.elevenlabs = self.Elevenlabs(self.config['elevenlabs'])
        
    def __repr__(self):
        return repr(self.config)
    
    class Setting(object):

        def __init__(self, value):
            self.setting = value

        def __repr__(self):
            return repr(self.setting)

        @property
        def input_device(self):
            return self.setting['input_device']

        @input_device.setter
        def input_device(self, value):
            self.setting['input_device'] = value

        @property
        def output_device(self):
            return self.setting['output_device']

        @output_device.setter
        def output_device(self, value):
            self.setting['output_device'] = value
        
        @property
        def input_language(self):
            return self.setting['input_language']

        @input_language.setter
        def input_language(self, value):
            self.setting['input_language'] = value
            
        @property
        def target_language(self):
            return self.setting['target_language']

        @target_language.setter
        def target_language(self, value):
            self.setting['target_language'] = value
            
        @property
        def voice_quality(self):
            return self.setting['voice_quality']

        @voice_quality.setter
        def voice_quality(self, value):
            self.setting['voice_quality'] = value
    
    class Azure(object):

        def __init__(self, value):
            self.azure = value

        def __repr__(self):
            return repr(self.azure)

        @property
        def speech_key(self):
            return self.azure['speech_key']

        @speech_key.setter
        def speech_key(self, value):
            self.azure['speech_key'] = value

        @property
        def region(self):
            return self.azure['region']

        @region.setter
        def region(self, value):
            self.azure['region'] = value
        
    class Elevenlabs(object):

        def __init__(self, value):
            self.elevenlabs = value

        def __repr__(self):
            return repr(self.elevenlabs)

        @property
        def api_key(self):
            return self.elevenlabs['api_key']

        @api_key.setter
        def api_key(self, value):
            self.elevenlabs['api_key'] = value

        @property
        def voice(self):
            return self.elevenlabs['voice']

        @voice.setter
        def voice(self, value):
            self.elevenlabs['voice'] = value
            
        @property
        def model(self):
            return self.elevenlabs['model']

        @model.setter
        def model(self, value):
            self.elevenlabs['model'] = value
    
    def write(self):
        with open(self.config_file, "w") as outfile:
            outfile.write(json.dumps(self.config, indent=4))
            
    def read(self):
        if os.path.exists(self.config_file) == False or open(self.config_file, "r").read() == "":
            self.write()
        with open(self.config_file, "r") as openfile:
            self.config = json.load(openfile)
        return repr(self.config)

config = Config()