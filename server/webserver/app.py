from aiohttp import web
import asyncio
from dataclasses import dataclass
import logging
import os
import uuid

from models import Config
from webserver.session_manager import RobotSessionManager, VideoSessionManager

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

ROOT_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
STATIC_DIR_PATH = os.path.join(ROOT_DIR_PATH, "react/pirobot/build/static")
if not os.path.isdir(STATIC_DIR_PATH):
    STATIC_DIR_PATH = "/var/www/static"
INDEX_FILE_PATH = os.path.join(ROOT_DIR_PATH, "react/pirobot/build/index.html")
if not os.path.isfile(INDEX_FILE_PATH):
    INDEX_FILE_PATH = "/var/www/index.html"


@dataclass
class Context:
    robot_server = None


context = Context()


class WebSocketProtocol(asyncio.BaseTransport):

    def __init__(self, ws: web.WebSocketResponse):
        super().__init__()
        self.ws: web.WebSocketResponse = ws

    async def send_message(self, topic, message):
        await self.ws.send_json(dict(topic=topic, message=message))


@routes.get("/")
async def index(request):
    with open(INDEX_FILE_PATH) as index_file:
        return web.Response(text=index_file.read(), content_type="text/html")


@routes.get("/video/<path:path>")
async def get_video(path):
    return send_from_directory(os.path.join(os.environ["HOME"], "Videos"), path)


@routes.get("/ws/robot")
async def handle_message(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    sid = uuid.uuid4()
    protocol = WebSocketProtocol(ws=ws)
    session = RobotSessionManager(sid=sid, protocol=protocol)
    logger.info(f"New connection to robot socket [{sid}]")

    # Send robot status
    await context.robot_server.send_status(protocol)

    async for msg in ws:
        await session.process_message(msg.data)

    session.close()
    logger.info(f"Connection closed to robot socket [{sid}]")


@routes.get("/ws/video_stream")
async def video_stream(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    sid = uuid.uuid4()
    session = VideoSessionManager(sid=sid, ws=ws)
    logger.info(f"New connection to video socket [{sid}]")

    async for msg in ws:
        session.process_message(msg.data)

    session.close()
    logger.info(f"Connection closed to video socket [{sid}]")

app = web.Application()
app.add_routes(routes)
app.add_routes([web.static('/static', STATIC_DIR_PATH)])


async def run_webserver(server):
    context.robot_server = server
    await web._run_app(app, port=Config.get_webserver_port())
