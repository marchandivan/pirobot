import threading

from handlers.base import BaseHandler, register_handler
from sfx import SFX


@register_handler(name="sfx", needs=["speaker"])
class SfxHandler(BaseHandler):

    def __init__(self):
        super().__init__()
        self.register_for_message("sfx")

    def process(self, message, protocol):
        if message["action"] == "play":
            threading.Thread(target=SFX.play, args=(message["args"]["name"],)).start()
