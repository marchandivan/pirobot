import logging
import os
from PIL import Image

from handlers.base import BaseHandler, register_handler

logger = logging.getLogger(__name__)


@register_handler("lcd")
class DriveHandler(BaseHandler):

    def __init__(self):
        super().__init__()
        self.register_for_message("lcd")
        self.pics_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets/Pics'))

    def process(self, message, protocol):
        if message["action"] == "display_picture":
            self.set_lcd_picture(protocol.server, message["args"]["name"])

    def set_lcd_picture(self, server, name):
        file_path = os.path.join(self.pics_path, f"{name}.png")
        if os.path.isfile(file_path):
            image = Image.open(file_path)
            image = image.resize((server.lcd.height, server.lcd.width)).convert('RGB')
            server.lcd.ShowImage(image)
        else:
            logger.info(f"Picture not found {name}")

