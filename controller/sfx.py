import pygame
import os


class SFX(object):
    sfx_path = os.path.join(os.path.dirname(__file__), 'assets/SFX')

    @staticmethod
    def play(name):
        file_path = os.path.join(SFX.sfx_path, f"{name}.wav")
        if os.path.isfile(file_path):
            pygame.mixer.pre_init(44100, 16, 2, 4096)  # frequency, size, channels, buffersize
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() == True:
                continue
        else:
            print(f"SFX not found: {name}")