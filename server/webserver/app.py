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


class WebSocketProtocol(object):

    def __init__(self, ws: web.WebSocketResponse):
        super().__init__()
        self.ws: web.WebSocketResponse = ws

    async def send_message(self, topic, message):
        await self.ws.send_json(dict(topic=topic, message=message))

    async def connection_made(self):
        # Send robot status
        await context.robot_server.send_status(self)

    async def connection_lost(self):
        context.robot_server.connection_lost()


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
    await protocol.connection_made()
    session = RobotSessionManager(sid=sid, protocol=protocol)
    logger.info(f"New connection to robot socket [{sid}]")

    try:
        async for msg in ws:
            await session.process_message(msg.data)
    except Exception:
        await protocol.connection_lost()
        logger.error(f"Connection closed to robot socket [{sid}]", exc_info=True)
    else:
        await protocol.connection_lost()
        logger.info(f"Connection closed to robot socket [{sid}]")
    finally:
        session.close()


@routes.get("/ws/video_stream")
async def video_stream(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    sid = uuid.uuid4()
    session = VideoSessionManager(sid=sid, ws=ws)
    logger.info(f"New connection to video socket [{sid}]")

    async for msg in ws:
        await session.process_message(msg.data)

    session.close()
    logger.info(f"Connection closed to video socket [{sid}]")

app = web.Application()
app.add_routes(routes)
app.add_routes(
    [
        web.static("/static", STATIC_DIR_PATH),
        web.static("/pictures", os.path.join(os.environ["HOME"], "Pictures/PiRobot"), show_index=True),
        web.static("/videos", os.path.join(os.environ["HOME"], "Videos/PiRobot"), show_index=True),
    ]
)


async def run_webserver(server):
    context.robot_server = server
    await web._run_app(app, port=Config.get_webserver_port())
