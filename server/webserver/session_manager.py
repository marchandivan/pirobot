import asyncio
import base64
import logging
import threading
import time

from camera import Camera
from server import Server

logger = logging.getLogger(__name__)


class SessionManager(object):
    sessions = {}
    # Used for video streaming
    NEW_FRAME_TIMEOUT = 2

    def __init__(self, ws, sid, loop):
        self.ws = ws
        self.sid = sid
        self.last_frame_ts = 0
        self.client_ready = threading.Event()
        self.loop = loop

    def __del__(self):
        self.close()

    def close(self):
        Camera.remove_new_streaming_frame_callback(f"session_{self.sid}")

    async def send(self, topic, message):
        data = dict(topic=topic, message=message)
        await self.ws.send_json(data)

    def process_video_stream_request(self, message):
        if message == "start":
            Camera.add_new_streaming_frame_callback(f"session_{self.sid}", self.send_new_frame)
            Camera.start_streaming()
        elif message == "ready":
            self.client_ready.set()

    def send_new_frame(self, frame):
        now = time.time()
        if self.client_ready.is_set() or (now - self.last_frame_ts) > SessionManager.NEW_FRAME_TIMEOUT:
            self.last_frame_ts = now
            asyncio.run(self.ws.send_bytes(frame))
            self.client_ready.clear()

    def process_message(self, message):
        topic = message.get("topic")
        if topic == "robot":
            Server.process(message.get("message"), self.ws)
        elif topic == "video_stream":
            self.process_video_stream_request(message.get("message"))
        else:
            logger.warning(f"Unknown topic {topic}")

