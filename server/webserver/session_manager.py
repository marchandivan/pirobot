import threading
import time

from camera import Camera
from server import Server


class SessionManager(object):
    sessions = {}
    # Used for video streaming
    NEW_FRAME_TIMEOUT = 2

    @staticmethod
    def new_session(sid, socketio):
        session = SessionManager(sid, socketio)
        SessionManager.sessions[sid] = session
        return session

    @staticmethod
    def remove_session(sid):
        if sid in SessionManager.sessions:
            del SessionManager.sessions[sid]

    @staticmethod
    def get_session(sid):
        return SessionManager.sessions.get(sid)

    def __init__(self, sid, socketio):
        self.sid = sid
        self.socketio = socketio
        self.last_frame_ts = 0
        self.client_ready = threading.Event()

    def __del__(self):
        Camera.remove_new_streaming_frame_callback(f"session_{self.sid}")

    def emit(self, event, args):
        self.socketio.emit(event, args, to=self.sid)

    def process_video_stream_request(self, data):
        if data == "start":
            Camera.add_new_streaming_frame_callback(f"session_{self.sid}", self.send_new_frame)
            Camera.start_streaming()
        elif data == "ready":
            self.client_ready.set()

    def send_new_frame(self, frame):
        now = time.time()
        if self.client_ready.is_set() or (now - self.last_frame_ts) > SessionManager.NEW_FRAME_TIMEOUT:
            self.emit("video_frame", frame)
            self.client_ready.clear()
            self.last_frame_ts = now

    def process_message_request(self, message):
        Server.process(message, self.socketio)

