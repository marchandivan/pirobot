from playsound import playsound
import os


class SFX(object):
    sfx_path = os.path.join(os.path.dirname(__file__), 'assets/SFX')

    @staticmethod
    def play(name):
        file_path = os.path.join(SFX.sfx_path, f"{name}.wav")
        if os.path.isfile(file_path):
            playsound(file_path)
        else:
            print(f"SFX not found: {name}")