from pygame import mixer
import os


class SFX(object):

    @staticmethod
    def setup():
        mixer.init()
        SFX.sfx_path = os.path.join(os.path.dirname(__file__), 'assets/SFX')
        if not os.path.isdir(SFX.sfx_path):
            SFX.sfx_path = "/etc/pirobot/assets/SFX"

    @staticmethod
    def play(name):
        file_path = os.path.join(SFX.sfx_path, f"{name}.wav")
        if os.path.isfile(file_path):
            mixer.Sound(file_path).play()

        else:
            print(f"SFX not found: {name}")