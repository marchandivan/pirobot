import json
from asgiref.sync import sync_to_async
import traceback

from django.contrib import admin
from django.db import models

with open('config.json') as config_file:
    CONFIG_KEYS = json.load(config_file)

# Create your models here.
class Config(models.Model):
    key = models.CharField(max_length=30, primary_key=True)
    value = models.CharField(max_length=2048)

    @staticmethod
    def _convert_to_type(value, type):
        if type == "int":
            return int(value)
        elif type == "str":
            return str(value)
        elif type == "float":
            return float(value)
        elif type == "bool":
            return bool(value)
        elif type == json:
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
        try:
            for o in sync_to_async(Config.objects.all)():
                config[o.key] = o.value
        except:
            traceback.print_exc()
        return config

    def __str__(self):
        return self.key


admin.site.register(Config)
