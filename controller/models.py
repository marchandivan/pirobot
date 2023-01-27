import json
import os


# Create your models here.
class Config(object):
    CONFIG_KEYS = None

    @staticmethod
    def setup(config):
        config_file_path = os.path.join(os.path.dirname(__file__), f"config/{config}.config.json")
        if os.path.isfile(config):
            config_file_path = config
        elif not os.path.isfile(config_file_path):
            print(f"Warning: Invalid config file {config}, using default instead")
            config_file_path = os.path.join(os.path.dirname(__file__), "config/default.config.json")

        with open(config_file_path) as config_file:
            Config.CONFIG_KEYS = json.load(config_file)

    @staticmethod
    def get(key):
        config = Config.CONFIG_KEYS.get(key)
        if config is None:
            raise KeyError(key)
        return config.get("default")

    @staticmethod
    def get_config():
        config = {}
        for key, key_config in Config.CONFIG_KEYS.items():
            if key_config.get('export', False):
                config[key] = Config.get(key)
        return config

    def __str__(self):
        return self.key
