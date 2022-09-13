from restapi.models import Config

class LCD_2inch(object):
    width = 240
    height = 320

    def __init__(self, rst = 27,dc = 25,bl = 18):
        pass

    def Init(self):
        print("Using mock LCD")

    def clear(self):
        pass

    def ShowImage(self, image, Xstart=0, Ystart=0):
        if Config.get('show_mock_screen'):
            image.show()

    def bl_DutyCycle(self, dc):
        print(f"Set back light duty cycle to {dc}")


