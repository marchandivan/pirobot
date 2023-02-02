import json
import os

from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


# Create your models here.
class Config(Base):
    CONFIG_KEYS = None
    db_engine = None

    __tablename__ = 'server_config'

    key = Column(String(30), primary_key=True)
    value = Column(String(2048), nullable=False)

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
    def setup(config):
        config_file_path = os.path.join(os.path.dirname(__file__), f"config/{config}.config.json")
        if os.path.isfile(config):
            config_file_path = config
        elif not os.path.isfile(config_file_path):
            print(f"Warning: Invalid config file {config}, using default instead")
            config_file_path = os.path.join(os.path.dirname(__file__), "config/default.config.json")
        with open(config_file_path) as config_file:
            Config.CONFIG_KEYS = json.load(config_file)

        Config.db_engine = create_engine('sqlite:///db.sqlite3')
        Config.session_maker = sessionmaker(bind=Config.db_engine)

    @staticmethod
    def create_db():
        if Config.db_engine is not None:
            Base.metadata.create_all(Config.db_engine)
        else:
            print("DB Engine not found, run setup() first")

    @staticmethod
    def get_session():
        if Config.db_engine is not None:
            return Config.session_maker()
        else:
            print("DB Engine not found, run setup() first")

    @staticmethod
    def get(key):
        config = Config.CONFIG_KEYS.get(key)
        if config is None:
            raise KeyError(key)
        else:
            session = Config.get_session()
            c = Config.get_from_db(session, key)
            if c is not None:
                return Config._convert_to_type(c.value, config.get("type"))
        return config.get("default")

    @staticmethod
    def get_from_db(session, key):
        for c in session.query(Config).filter(Config.key == key):
            return c
        return None

    @staticmethod
    def save(key, value):
        if Config.is_valid(key, value):
            session = Config.get_session()
            c = Config.get_from_db(session, key)
            if c is not None:
                c.value = value
            else:
                c = Config(key=key, value=value)

            session.add(c)
            session.commit()
            return True
        else:
            return False

    @staticmethod
    def delete(key):
        session = Config.get_session()
        c = Config.get_from_db(session, key)
        if c is not None:
            session.delete(c)
            session.commit()
            return True

        return False

    @staticmethod
    def is_valid(key, value):
        config = Config.CONFIG_KEYS.get(key)
        if config is not None:
            try:
                Config._convert_to_type(value, config.get("type"))
                return True
            except:
                print(f"Unable to parse value as {config.get('type')}")
                return False
        else:
            print(f"Unknown key {key}")
            return False

    @staticmethod
    def get_config():
        config = {}
        for key, key_config in Config.CONFIG_KEYS.items():
            config[key] = dict(value=Config.get(key), type=key_config.get("type"), default=key_config.get("default"))
        return config

    @staticmethod
    def export_config():
        config = {}
        for key, key_config in Config.CONFIG_KEYS.items():
            if  key_config.get('export', False):
                config[key] = Config.get(key)
        return config

    def __str__(self):
        return self.key
