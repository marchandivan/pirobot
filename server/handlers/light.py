from handlers.base import BaseHandler, register_handler
from light import Light


@register_handler(name="light", needs=["light"])
class LightHandler(BaseHandler):

    def __init__(self):
        super().__init__()
        self.register_for_message("light")

    def process(self, message, protocol):
        if message["action"] == "toggle":
            Light.toggle_front_light()
        elif message["action"] == "blink":
            args = message.get("args", {})
            Light.blink(left_on=args.get('left_on', True), right_on=args.get('right_on', True))
