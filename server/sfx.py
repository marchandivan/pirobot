from pygame import mixer
import os


class SFX(object):
    sfx_path = os.path.join(os.path.dirname(__file__), 'assets/SFX')

    @staticmethod
    def setup():
        mixer.init()

    @staticmethod
    def play(name):
        file_path = os.path.join(SFX.sfx_path, f"{name}.wav")
        if os.path.isfile(file_path):
            mixer.Sound(file_path).play()

        else:
            print(f"SFX not found: {name}")