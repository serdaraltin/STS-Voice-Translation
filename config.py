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
        self.load()
        self.setting = self.Setting(self.config['setting'])
        self.aws = self.Aws(self.config['aws'])
        self.azure = self.Azure(self.config['azure'])
        self.elevenlabs = self.Elevenlabs(self.config['elevenlabs'])
        self.deepgram = self.Deepgram(self.config['deepgram'])
        
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
        def record_quality(self):
            return self.setting['record_quality']

        @record_quality.setter
        def record_quality(self, value):
            self.setting['record_quality'] = value
        
        @property
        def source_language(self):
            return self.setting['source_language']

        @source_language.setter
        def source_language(self, value):
            self.setting['source_language'] = value
            
        @property
        def source_language_code(self):
            return self.setting['source_language_code']

        @source_language_code.setter
        def source_language_code(self, value):
            self.setting['source_language_code'] = value
            
        @property
        def target_language(self):
            return self.setting['target_language']

        @target_language.setter
        def target_language(self, value):
            self.setting['target_language'] = value
        
        @property
        def target_language_code(self):
            return self.setting['target_language_code']

        @target_language_code.setter
        def target_language_code(self, value):
            self.setting['target_language_code'] = value
        
        @property
        def voice(self):
            return self.setting['voice']

        @voice.setter
        def voice(self, value):
            self.setting['voice'] = value
            
        @property
        def voice_quality(self):
            return self.setting['voice_quality']

        @voice_quality.setter
        def voice_quality(self, value):
            self.setting['voice_quality'] = value
            
        @property
        def device_id(self):
            return self.setting['device_id']

        @device_id.setter
        def device_id(self, value):
            self.setting['device_id'] = value     
            
    class Aws(object):

        def __init__(self, value):
            self.aws = value

        def __repr__(self):
            return repr(self.aws)

        @property
        def access_key_id(self):
            return self.aws['access_key_id']

        @access_key_id.setter
        def access_key_id(self, value):
            self.aws['access_key_id'] = value

        @property
        def secret_access_key(self):
            return self.aws['secret_access_key']

        @secret_access_key.setter
        def secret_access_key(self, value):
            self.aws['secret_access_key'] = value
            
        @property
        def region_name(self):
            return self.aws['region_name']

        @region_name.setter
        def model(self, value):
            self.aws['region_name'] = value
        
        @property
        def region_name(self):
            return self.aws['region_name']

        @region_name.setter
        def model(self, value):
            self.aws['region_name'] = value
            
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
        def voice_id(self):
            return self.elevenlabs['voice_id']

        @voice_id.setter
        def voice_id(self, value):
            self.elevenlabs['voice_id'] = value
            
        @property
        def model(self):
            return self.elevenlabs['model']

        @model.setter
        def model(self, value):
            self.elevenlabs['model'] = value
    
    class Deepgram(object):
        def __init__(self, value) -> None:
            self.deepgram = value
        
        def __repr__(self) -> str:
            return repr(self.deepgram)
        
        @property
        def api_key(self):
            return self.deepgram['api_key']
        
        @api_key.setter
        def apit_key(self, value):
            self.deepgram['api_key'] = value
            
        @property
        def language(self):
            return self.deepgram['language']
        
        @language.setter
        def language(self, value):
            self.deepgram['language'] = value
            
        @property
        def model(self):
            return self.deepgram['model']
        
        @model.setter
        def model(self, value):
            self.deepgram['model'] = value
            
        @property
        def host(self):
            return self.deepgram['host']
        
        @host.setter
        def host(self, value):
            self.deepgram['host'] = value
            
        @property
        def tier(self):
            return self.deepgram['tier']
        
        @tier.setter
        def tier(self, value):
            self.deepgram['tier'] = value
            
        @property
        def version(self):
            return self.deepgram['version']
        
        @version.setter
        def version(self, value):
            self.deepgram['version'] = value
            
        @property
        def panctuate(self):
            return self.deepgram['panctuate']
        
        @panctuate.setter
        def panctuate(self, value):
            self.deepgram['panctuate'] = value
            
        @property
        def encoding(self):
            return self.deepgram['encoding']
        
        @encoding.setter
        def encoding(self, value):
            self.deepgram['encoding'] = value
        
        @property
        def sample_rate(self):
            return self.deepgram['sample_rate']
        
        @sample_rate.setter
        def sample_rate(self, value):
            self.deepgram['sample_rate'] = value
            
    def save(self):
        with open(self.config_file, "w") as outfile:
            outfile.write(json.dumps(self.config, indent=4))
            
    def load(self):
        if os.path.exists(self.config_file) == False or open(self.config_file, "r").read() == "":
            pass
        with open(self.config_file, "r") as openfile:
            self.config = json.load(openfile)
        return repr(self.config)

config = Config()