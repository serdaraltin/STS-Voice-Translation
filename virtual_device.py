
import subprocess
from config import config, preset
from copy import copy

class VirtualMic():
   
    DEVICE_ID = None
    
    def __init__(self) -> None:
        pass
    
    def __repr__(self) -> str:
        return repr(self.DEVICE_ID)
    
    def load_device(self):
        pactl_load_module = [
            'pactl',
            'load-module',
            'module-pipe-source',
            'source_name={}'.format(config.setting.output_device),
            'source_properties=device.description={}'.format(config.setting.output_device),
            'file={}'.format(preset.file.virtual_input),
            'format=s16le',
            'rate=16000',
            'channels=1'
        ]
        
        try:
            pactl_output = subprocess.check_output(pactl_load_module, stderr=subprocess.STDOUT, text=True)
            self.DEVICE_ID = pactl_output.strip().split()[-1]
            print("Virtual Device Id: ", self.DEVICE_ID)
            return True, self.DEVICE_ID
        except subprocess.CalledProcessError as e:
            error_message = e.output
            return False, error_message
        
    def unload_device(self):
        pactl_unload_module = [
            'pactl',
            'unload-module',
            '{}'.format(self.DEVICE_ID)
        ]
        
        try:
            subprocess.run(pactl_unload_module)
            return True
        except subprocess.CalledProcessError as e:
            error_message = e.output
            print(error_message)
            return False, error_message
    
    async def stream_audio_binary(_data):
        with open("/tmp/stream_audio.mp3", "wb") as audio_file:
            audio_file.write(_data)
        ffmpeg_stream = [
            'ffmpeg',
            '-re',
            '-i',
            '{}'.format("/tmp/stream_audio.mp3"),
            '-f', 's16le',
            '-ar', '16000',
            '-ac', '1',
            '-'
        ]
        with subprocess.Popen(ffmpeg_stream, stdout=subprocess.PIPE) as ffmpeg_process:
            while True:
                audio_data = ffmpeg_process.stdout.read(1024)
                if not audio_data:
                    break
                with open(preset.file.virtual_output, 'wb') as virtmic:
                    virtmic.write(audio_data)
    def stream_audio(self, _input_audio):
        ffmpeg_stream = [
            'ffmpeg',
            '-re',
            '-i',
            '{}'.format(_input_audio),
            '-f', 's16le',
            '-ar', '16000',
            '-ac', '1',
            '-'
        ]
        with subprocess.Popen(ffmpeg_stream, stdout=subprocess.PIPE) as ffmpeg_process:
            while True:
                audio_data = ffmpeg_process.stdout.read(1024)
                if not audio_data:
                    break
                with open(preset.file.virtual_input, 'wb') as virtmic:
                    virtmic.write(audio_data)

virtualmic = VirtualMic()