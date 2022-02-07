
class LCD_2inch(object):
    width = 240
    height = 320

    def __init__(self, rst = 27,dc = 25,bl = 18):
        pass

    def ShowImage(self, image, Xstart=0, Ystart=0):
        image.save('capture.png')


