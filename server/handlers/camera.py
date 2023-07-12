from handlers.base import BaseHandler, register_handler
from camera import Camera


@register_handler("drive")
class CameraHandler(BaseHandler):

    def __init__(self):
        super().__init__()
        self.register_for_message("camera")

    def process(self, message, protocol):
        if message["action"] == "set_position":
            Camera.set_position(message["args"]["position"])
        elif message["action"] == "center_position":
            Camera.center_position()
