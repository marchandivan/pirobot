import cv2

from camera import Camera
from handlers.base import BaseHandler, register_handler
from models import Config
from motor.motor import Motor

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')


@register_handler("face_detection")
class FaceDetectionHandler(BaseHandler):

    def __init__(self):
        super().__init__()
        self.follow_face_speed = Config.get("follow_face_speed")
        self.register_for_message("face_detection")
        self.register_for_event("camera", "new_frame")
        self.face_position = None
        self.running = False

    def process(self, message, protocol):
        if message["action"] == "toggle":
            self.toggle()
        elif message["action"] == "start":
            self.start()
        elif message["action"] == "stop":
            self.stop()

    def start(self):
        if BaseHandler.state is None:
            BaseHandler.set_state("face_detection")
            self.running = True

    def stop(self):
        if BaseHandler.state == "face_detection":
            BaseHandler.reset_state()
        self.running = False
        self.face_position = None

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def receive_event(self, topic, event_type, data):
        if self.running and topic == "camera" and event_type == "new_frame":
            self.detect_face(
                frame=data["frame"],
                frame_counter=data["frame_counter"],
                frame_rate=data["frame_rate"],
                res_x=data["res_x"],
                res_y=data["res_y"],
            )

    def detect_face(self, frame, frame_counter, frame_rate, res_x, res_y):
        # Run face detection every second
        if frame_counter % frame_rate == 0:
            self.face_position = None
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            # Look for faces with 2 eyes or more
            for (x, y, w, h) in faces:
                size_percent = 100 * w / res_x
                if size_percent < 5 or size_percent > 40:
                    continue
                if self.face_position is None:
                    self.face_position = (x, y, w, h)
                roi_gray = gray[y:y + h, x:x + w]
                eyes = eye_cascade.detectMultiScale(roi_gray)
                if len(eyes) >= 2:  # At least 2 eyes :-) Third one could be the mouth
                    self.face_position = (x, y, w, h)
                    break

            if self.face_position is not None:
                x, y, w, h = self.face_position
                timeout = 3
                x_pos = (x + w//2) * 100 / res_x
                y_pos = (y + h // 2) * 100 / res_y
                Camera.set_position(y)
                x_pos, y_pos = Camera.get_target_position(x_pos, y_pos)
                Motor.move_to_target(x_pos, y_pos, self.follow_face_speed, timeout)

        if self.running and self.face_position is not None:
            x, y, w, h = self.face_position
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)

