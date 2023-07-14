import cv2
import datetime
import time
import os

from camera import Camera
from handlers.base import BaseHandler, register_handler
from models import Config

@register_handler("drive")
class CameraHandler(BaseHandler):

    def __init__(self):
        super().__init__()
        self.frame_rate = Camera.frame_rate
        self.video_start_ts = None
        self.frame_counter = 0
        self.video_source = "streaming"
        self.register_for_message("camera")
        self.register_for_event("camera", "new_streaming_frame")
        self.video_writer = None
        self.video_dir = os.path.join(os.environ["HOME"], "Videos")
        if not os.path.isdir(self.video_dir):
            os.mkdir(self.video_dir)

    def process(self, message, protocol):
        if message["action"] == "set_position":
            Camera.set_position(message["args"]["position"])
        elif message["action"] == "center_position":
            Camera.center_position()
        elif message["action"] == "start_video":
            if self.video_writer is not None:
                self.video_writer.release()
            self.video_source = message["args"].get("source", "streaming")
            robot_name = Config.get("robot_name")
            creation_time = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
            filename = f"{robot_name}_{self.video_source}_{creation_time}.avi"
            self.frame_rate = Camera.frame_rate
            self.video_writer = cv2.VideoWriter(
                filename=os.path.join(self.video_dir, filename),
                fourcc=cv2.VideoWriter_fourcc(*Config.get("video_codec")),
                fps=self.frame_rate,
                frameSize=(1280, 720),
                isColor=True,
            )
        elif message["action"] == "stop_video":
            self.video_start_ts = None
            self.frame_counter = 0
            if self.video_writer is not None:
                self.video_writer.release()
                self.video_writer = None

    def receive_event(self, topic, event_type, data):
        if topic == "camera" and event_type == "new_streaming_frame":
            if self.video_writer is not None:
                self.video_writer.write(data["frame"])
                self.frame_counter += 1
                if self.video_start_ts is None:
                    self.video_start_ts = time.time()
                else:
                    expect_nb_of_frames = int((time.time() - self.video_start_ts) * self.frame_rate)
                    nb_of_missing_frames = expect_nb_of_frames - self.frame_counter
                    if nb_of_missing_frames > 1:
                        for i in range(nb_of_missing_frames):
                            self.video_writer.write(data["frame"])
                            self.frame_counter += 1
