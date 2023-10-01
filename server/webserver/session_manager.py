from abc import ABC, abstractmethod
import asyncio
import json
import logging
import threading
import time

from camera import Camera
from server import Server

logger = logging.getLogger(__name__)


class SessionManager(ABC):

    def __init__(self, sid):
        self.sid = sid
        self.last_frame_ts = 0

    def __del__(self):
        self.close()

    def close(self):
        pass

    @abstractmethod
    async def process_message(self, message):
        pass


class RobotSessionManager(SessionManager):

    def __init__(self, sid, protocol):
        super().__init__(sid)
        self.protocol = protocol

    async def process_message(self, message):
        message_dict = json.loads(message)
        topic = message_dict.get("topic")
        if topic == "robot":
            await Server.process(message_dict.get("message"), self.protocol)
        else:
            logger.warning(f"Unknown topic {topic}")


class VideoSessionManager(SessionManager):
    # Used for video streaming
    NEW_FRAME_TIMEOUT = 2

    def __init__(self, sid, ws):
        super().__init__(sid)
        self.ws = ws
        self.client_ready = threading.Event()
        self.connection_opened = True

    def __del__(self):
        if self.connection_opened:
            self.close()

    def close(self):
        if self.connection_opened:
            Camera.remove_new_streaming_frame_callback(f"session_{self.sid}")
            self.connection_opened = False

    async def process_message(self, message):
        if message == "start":
            Camera.add_new_streaming_frame_callback(f"session_{self.sid}", self.send_new_frame)
            Camera.start_streaming()
        elif message == "ready":
            self.client_ready.set()

    def send_new_frame(self, frame):
        if self.connection_opened:
            now = time.time()
            if self.client_ready.is_set() or (now - self.last_frame_ts) > VideoSessionManager.NEW_FRAME_TIMEOUT:
                self.last_frame_ts = now
                asyncio.run(self.ws.send_bytes(frame))
                self.client_ready.clear()

