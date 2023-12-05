from config import config

def save_settings(_config):
    config.save(_config)

def reset_settings():
    pass

def reload_settings():
    return config.load()