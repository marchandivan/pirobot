from flask import Flask, request
from flask_socketio import SocketIO
import logging

from webserver.session_manager import SessionManager

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/")
async def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/video/<path:path>")
async def get_video(path):
    return send_from_directory(os.path.join(os.environ["HOME"], "Videos"), path)


@socketio.on("connect")
def connect():
    sid = request.sid
    logger.info(f"New connection [{sid}]")
    SessionManager.new_session(sid, socketio)


@socketio.on("disconnect")
def disconnect():
    sid = request.sid
    logger.info(f"Connection lost [{sid}]")
    SessionManager.remove_session(sid)


@socketio.on("message")
def handle_message(message):
    sid = request.sid
    session = SessionManager.get_session(sid)
    if session is not None:
        session.process_message_request(message)


@socketio.on("video_stream")
def video_stream(data):
    sid = request.sid
    session = SessionManager.get_session(sid)
    if session is not None:
        session.process_video_stream_request(data)


def run_webserver():
    socketio.run(app, debug=True)
