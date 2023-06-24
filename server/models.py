import configparser
import json
import os

from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from logger import RobotLogger

Base = declarative_base()

DEFAULT_CONFIG = {
    "config_name": "pirobot",
    "log_file": None,
    "message_log_file": None,
    "log_level": "WARNING",
}

# Create your models here.
class Config(Base):
    CONFIG_KEYS = None
    USER_CONFIG_DIR = os.path.join(os.environ["HOME"], ".pirobot")
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
    def setup(config_name):
        if not os.path.isdir(Config.USER_CONFIG_DIR):
            os.makedirs(Config.USER_CONFIG_DIR)

        user_config_file_path = os.path.join(Config.USER_CONFIG_DIR, "pirobot.config")
        user_config = configparser.ConfigParser(defaults=DEFAULT_CONFIG, default_section="pirobot", allow_no_value=True)
        if os.path.isfile(user_config_file_path):
            user_config.read(user_config_file_path)
        else:
            with open(user_config_file_path, "w") as configfile:
                user_config.write(configfile)

        # Setup logger
        RobotLogger.setup_logger(
            app_log_file=user_config.get("pirobot", "log_file"),
            message_log_file=user_config.get("pirobot", "message_log_file"),
            level=user_config.get("pirobot", "log_level")
        )
        if config_name is None:
            config_name = user_config.get("pirobot", "config_name")

        config_file_dir = os.path.join(os.path.dirname(__file__), "config")
        if not os.path.isdir(config_file_dir):
            config_file_dir = "/etc/pirobot/config"
        config_file_path = os.path.join(config_file_dir, f"{config_name}.config.json")
        if os.path.isfile(config_name):
            config_file_path = config_name
        elif not os.path.isfile(config_file_path):
            print(f"Warning: Invalid config file {config_name}, using default instead")
            config_file_path = os.path.join(config_file_dir, "pirobot.config.json")
        with open(config_file_path) as config_file:
            Config.CONFIG_KEYS = json.load(config_file)

        db_file_path = os.path.join(Config.USER_CONFIG_DIR, "db.sqlite3")
        Config.db_engine = create_engine(f"sqlite:///{db_file_path}")

        if not os.path.isfile(db_file_path):
            Base.metadata.create_all(Config.db_engine)

        Config.session_maker = sessionmaker(bind=Config.db_engine)

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
