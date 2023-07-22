import cv2

from camera import Camera
from handlers.base import BaseHandler, register_handler


@register_handler("qr_code")
class QRCodeHandler(BaseHandler):

    def __init__(self):
        super().__init__()
        self.frame_counter = 0
        self.running = False
        self.register_for_message("qr_code")
        self.register_for_event("camera", "new_front_camera_frame")
        self.detector = cv2.QRCodeDetector()

    def process(self, message, protocol):
        if message["action"] == "toggle":
            self.running = not self.running
        elif message["action"] == "start":
            self.running = True
        elif message["action"] == "stop":
            self.running = False

    def receive_event(self, topic, event_type, data):
        if self.running and topic == "camera" and event_type == "new_front_camera_frame" and len(data["frame"]) > 0:
            if self.frame_counter % Camera.frame_rate == 0:
                decoded_info, points, _ = self.detector.detectAndDecode(data["frame"])
                if points is not None:
                    print(decoded_info)
            self.frame_counter += 1

