import json

with open('config.json') as config_file:
    CONFIG_KEYS = json.load(config_file)


# Create your models here.
class Config(object):
    #key = models.CharField(max_length=30, primary_key=True)
    #value = models.CharField(max_length=2048)

    @staticmethod
    def _convert_to_type(value, config_type):
        if config_type == "int":
            return int(value)
        elif config_type == "str":
            return str(value)
        elif config_type == "float":
            return float(value)
        elif config_type == "bool":
            if type(value) == str:
                return value.lower() in ('y', 'true')
            else:
                return bool(value)
        elif config_type == json:
            return json.loads(value)
        else:
            return value

    @staticmethod
    def get(key):
        config = CONFIG_KEYS.get(key)
        if config is None:
            raise KeyError(key)
        try:
            o = Config.objects.get(key=key)
            return Config._convert_to_type(o.value, config.get("type"))
        except:
            return config.get("default")

    @staticmethod
    def get_config():
        config = {}
        for key, key_config in CONFIG_KEYS.items():
            if key_config.get('export', False):
                config[key] = Config.get(key)
        return config

    def __str__(self):
        return self.key
