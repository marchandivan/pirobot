from aiohttp import web
import cv2
from dataclasses import dataclass
import io
import logging
import os
from PIL import Image
import re
import uuid

from models import Config
from webserver.session_manager import RobotSessionManager, VideoSessionManager
from wifi import Wifi

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

ROOT_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
PUBLIC_DIR_PATH = os.path.join(ROOT_DIR_PATH, "react/pirobot/public")
if not os.path.isdir(PUBLIC_DIR_PATH):
    PUBLIC_DIR_PATH = "/var/www/public"
STATIC_DIR_PATH = os.path.join(ROOT_DIR_PATH, "react/pirobot/build/static")
if not os.path.isdir(STATIC_DIR_PATH):
    STATIC_DIR_PATH = "/var/www/static"
INDEX_FILE_PATH = os.path.join(ROOT_DIR_PATH, "react/pirobot/build/index.html")
if not os.path.isfile(INDEX_FILE_PATH):
    INDEX_FILE_PATH = "/var/www/index.html"
PICTURES_DIR = os.path.join(os.environ["HOME"], "Pictures/PiRobot")
VIDEOS_DIR = os.path.join(os.environ["HOME"], "Videos/PiRobot")

MEDIA_FILE_RE = re.compile(r"(?P<robot_name>\w+)_(?P<source>[A-Za-z]+)_(?P<date>\d\d\d\d\d\d)_(?P<time>\d\d\d\d\d\d)\.(?P<format>\w+)")

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


@routes.get(r"/{file_name:(favicon.ico|logo192.png|logo512.png|manifest.jon)}")
async def public(request):
    file_name = request.match_info["file_name"]
    return web.FileResponse(os.path.join(PUBLIC_DIR_PATH, file_name))


def medias(media_dir):
    media_list = []
    if os.path.isdir(media_dir):
        for media_file in os.listdir(media_dir):
            m = re.match(MEDIA_FILE_RE, media_file)
            if m:
                media_list.append(
                    dict(
                        filename=media_file,
                        robot_name=m.group("robot_name"),
                        source=m.group("source"),
                        format=m.group("format"),
                        timestamp=f"{m.group('date')}_{m.group('time')}",
                        date=m.group("date"),
                        time=m.group("time"),
                    )
                )

    return web.json_response(sorted(media_list, key=lambda p: p["timestamp"], reverse=True))


@routes.get("/api/v1/pictures")
async def pictures(request):
    return medias(PICTURES_DIR)


@routes.get("/api/v1/videos")
async def videos(request):
    return medias(VIDEOS_DIR)


@routes.get("/gallery/picture/{file_name}")
async def picture(request):
    file_path = os.path.join(PICTURES_DIR, request.match_info['file_name'])
    if os.path.isfile(file_path):
        if request.rel_url.query.get("full", "n").lower() == "y":
            return web.FileResponse(file_path)
        image = Image.open(file_path)
        width = int(request.rel_url.query.get("w", 0))
        height = int(request.rel_url.query.get("h", 0))
        if width == 0 and height ==0:
            width = image.width
            height = image.height
        elif width == 0:
            width = int(image.width * height / image.height)
        elif height == 0:
            height = int(image.height * width / image.width)

        img_format = request.rel_url.query.get("format", "jpeg")

        image = image.resize([width, height])
        stream = io.BytesIO()
        image.save(stream, img_format)
        return web.Response(body=stream.getvalue(), content_type=f"image/{img_format}")
    else:
        return web.HTTPNotFound()

@routes.get("/api/v1/wifi")
async def get_wifi(request):
    response = dict(
        status=Wifi.get_status(),
        networks=Wifi.get_networks(),
    )
    return web.json_response(response)


@routes.post("/api/v1/wifi")
async def post_wifi(request):
    data = await request.json()
    if data.get("hotspot"):
        Wifi.start_hotspot()
    elif data.get("ssid"):
        Wifi.connect_to_network(data["ssid"], data["password"])
    else:
        Wifi.start_wifi()
    return web.json_response(dict(status="OK"))


@routes.delete("/api/v1/wifi")
async def del_wifi(request):
    data = await request.json()
    Wifi.forget_network(data["ssid"])
    return web.json_response(dict(status="OK"))


@routes.get("/gallery/video/{file_name}")
async def video(request):
    file_path = os.path.join(VIDEOS_DIR, request.match_info['file_name'])
    if os.path.isfile(file_path):
        if request.rel_url.query.get("full", "n").lower() == "y":
            return web.FileResponse(file_path)
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            logger.warning(f"Unable to open video file {file_path}")
            return web.HTTPNotFound()
        else:
            _, frame = cap.read()
        width = int(request.rel_url.query.get("w", 0))
        height = int(request.rel_url.query.get("h", 0))
        video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if width == 0 and height == 0:
            width = video_width
            height = video_height
        elif width == 0 and height != 0:
            width = int(video_width * height / video_height)
        elif height == 0:
            height = int(video_height * width / video_width)
        frame = cv2.resize(frame, (width, height))

        img_format = request.rel_url.query.get("format", "jpeg")

        return web.Response(body=cv2.imencode(f".{img_format}", frame)[1].tobytes(), content_type=f"image/{img_format}")
    else:
        logger.warning(f"Video file not found {file_path}")
        return web.HTTPNotFound()


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
        web.get(r"/pictures", index),
        web.get(r"/videos", index),
        web.get(r"/settings", index),
        web.get(r"/network", index),
    ]
)


async def run_webserver(server):
    context.robot_server = server
    await web._run_app(app, port=Config.get_webserver_port())
