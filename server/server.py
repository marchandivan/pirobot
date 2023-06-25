from camera import Camera
from light import Light
from models import Config
from motor.motor import Motor
from sfx import SFX
from terminal import Terminal
from uart import UART

import logging
import os
import platform
import pyttsx3
from PIL import Image
import threading

if platform.machine() == "aarch64":  # Mac OS
    from lcd.LCD_2inch import LCD_2inch
else:
    from lcd.LCD_Mock import LCD_2inch


logger = logging.getLogger(__name__)


class Server(object):

    @staticmethod
    async def setup():
        if Config.get("robot_has_speaker"):
            # Voice
            Server.voice_engine = pyttsx3.init()
            # SFX
            SFX.setup()
        else:
            Server.voice_engine = None

        if Config.get("robot_has_screen"):
            # LCD & terminal Initialization
            RST = 24
            DC = 25
            BL = 23
            Server.lcd = LCD_2inch(rst=RST, dc=DC, bl=BL)
            Server.lcd.Init()
            Server.lcd.clear()
            terminal = Terminal("Courier", Server.lcd)
            terminal.header("PiRobot v1.0")
            terminal.text("Starting...")
            Server.pics_path = os.path.join(os.path.dirname(__file__), 'assets/Pics')
            if not os.path.isdir(Server.pics_path):
                Server.pics_path = "/etc/pirobot/assets/Pics"
        else:
            Server.lcd = None

        # Open UART Port
        await UART.open()

        # Motor Initialization
        Motor.setup()
        if Config.get("robot_has_screen"):
            terminal.text(f"Motor setup... {Motor.get_status()}")

        # Light
        if Config.get('robot_has_light'):
            Light.setup()
            if Config.get("robot_has_screen"):
                terminal.text(f"Light setup... {Light.status}")

        # Camera Initialization
        Camera.setup()
        if Config.get("robot_has_screen"):
            terminal.text(f"Camera setup.. {Camera.status}")

        if Config.get("robot_has_screen"):
            terminal.text("Ready!")

    @staticmethod
    def set_lcd_picture(name):
        if Server.lcd is not None:
            file_path = os.path.join(Server.pics_path, f"{name}.png")
            if os.path.isfile(file_path):
                image = Image.open(file_path)
                image = image.resize((Server.lcd.height, Server.lcd.width)).convert('RGB')
                Server.lcd.ShowImage(image)

    @staticmethod
    def connection_lost():
        # Stop the robot in case of lost connection
        logger.warning("Client connection lost, stopping robot")
        Motor.stop()

    @staticmethod
    def process(message):
        # Motor
        if message["type"] == "motor":
            if message["action"] == "move":
                Motor.move(**message["args"])
            elif message["action"] == "stop":
                Motor.stop()
            elif message["action"] == "patrol":
                Motor.patrol()
        elif message["type"] == "light" and Config.get('robot_has_light'):
            if message["action"] == "toggle":
                Light.toggle_front_light()
            elif message["action"] == "blink":
                args = message.get("args", {})
                Light.blink(left_on=args.get('left_on', True), right_on=args.get('right_on', True))
        elif message["type"] == "camera":
            if message["action"] == "set_position":
                Camera.set_position(message["args"]["position"])
            elif message["action"] == "center_position":
                Camera.center_position()
            elif message["action"] == "toggle_face_detection":
                Camera.toggle_face_detection()
            elif message["action"] == "start_face_detection":
                Camera.start_face_detection()
            elif message["action"] == "stop_face_detection":
                Camera.stop_face_detection()
        elif message["type"] == "sfx" and Config.get("robot_has_speaker"):
            if message["action"] == "play":
                threading.Thread(target=SFX.play, args=(message["args"]["name"], )).start()
        elif message["type"] == "lcd" and Server.lcd is not None:
            if message["action"] == "display_picture":
                Server.set_lcd_picture(message["args"]["name"])
