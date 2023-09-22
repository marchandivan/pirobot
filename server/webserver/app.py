from aiohttp import web
import asyncio
import json
import logging
import os
import uuid

from models import Config
from webserver.session_manager import SessionManager

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

ROOT_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
STATIC_DIR_PATH = os.path.join(ROOT_DIR_PATH, "react/pirobot/build/static")
if not os.path.isdir(STATIC_DIR_PATH):
    STATIC_DIR_PATH = "/var/www/static"
INDEX_FILE_PATH = os.path.join(ROOT_DIR_PATH, "react/pirobot/build/index.html")
if not os.path.isfile(INDEX_FILE_PATH):
    INDEX_FILE_PATH = "/var/www/index.html"

@routes.get("/")
async def index(request):
    with open(INDEX_FILE_PATH) as index_file:
        return web.Response(text=index_file.read(), content_type="text/html")


@routes.get("/video/<path:path>")
async def get_video(path):
    return send_from_directory(os.path.join(os.environ["HOME"], "Videos"), path)


@routes.get("/ws")
async def handle_message(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    sid = uuid.uuid4()
    session = SessionManager(ws=ws, sid=sid, loop=asyncio.get_running_loop())
    logger.info(f"New connection [{sid}]")

    async for msg in ws:
        message = json.loads(msg.data)
        session.process_message(message)

    session.close()
    logger.info(f"Connection closed [{sid}]")


@routes.get("/ws/video_stream")
async def video_stream(data):
    sid = request.sid
    session = SessionManager.get_session(sid)
    if session is not None:
        session.process_video_stream_request(data)


app = web.Application()
app.add_routes(routes)
app.add_routes([web.static('/static', STATIC_DIR_PATH)])


async def run_webserver():
    await web._run_app(app, port=Config.get_webserver_port())
