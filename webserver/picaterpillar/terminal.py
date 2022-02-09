import os
from PIL import Image, ImageFont, ImageDraw

class Terminal(object):

    def __init__(self, font, lcd, background="BLACK", color=(0, 255, 0), font_size=30, interline=6):
        font_filepath = os.path.join("assets/Fonts", f"{font}.ttf")
        self._lcd = lcd
        if not os.path.isfile(font_filepath):
            font_filepath = "assets/Fonts/Courier.ttf"
        self._font = ImageFont.truetype(font_filepath, font_size)
        _, font_h = self._font.getsize("A")
        self._line_h = font_h + interline
        self._nb_line = (self._lcd.width // self._line_h) - 1
        self._background = background
        self._color = color
        self._header = ""
        self._buffer = []

    def header(self, text, stdout=False):
        self._header = text
        if stdout:
            self.stdout()

    def text(self, text, stdout=True):
        w, _ = self._font.getsize(text)
        overflow = ""
        while w > self._lcd.height:
            overflow = text[-1] + overflow
            text = text[:-1]
            w, _ = self._font.getsize(text)
        self._buffer.append(text)
        if len(overflow) > 0:
            self.text(overflow, stdout=False)
        while len(self._buffer) > self._nb_line:
            self._buffer.pop(0)
        if stdout:
            self.stdout()

    def stdout(self):
        image = Image.new("RGB", (self._lcd.height, self._lcd.width), self._background)
        draw = ImageDraw.Draw(image)
        draw.text((5, 5), self._header, fill=self._color, font=self._font)
        for i, line in enumerate(self._buffer):
            draw.text((5, 5 + self._line_h + i * self._line_h), line, fill=self._color, font=self._font)
        self._lcd.ShowImage(image)

    def reset(self):
        self._buffer = []
        self.stdout()
