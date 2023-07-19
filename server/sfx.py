import logging
import os
from pygame import mixer

logger = logging.getLogger(__name__)


class SFX(object):
    sfx_path = os.path.join(os.path.dirname(__file__), 'assets/SFX')

    @staticmethod
    def setup():
        mixer.init()
        if not os.path.isdir(SFX.sfx_path):
            SFX.sfx_path = "/etc/pirobot/assets/SFX"

    @staticmethod
    def play(name):
        file_path = os.path.join(SFX.sfx_path, f"{name}.wav")
        if os.path.isfile(file_path):
            mixer.Sound(file_path).play()

        else:
            logger.warning(f"SFX not found: {name}")
