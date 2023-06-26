from camera import Camera
from game import Games
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
        # Get capability flags for the robot
        Server.robot_has_speaker = Config.get("robot_has_speaker")
        Server.robot_has_screen = Config.get("robot_has_screen")
        Server.robot_has_light = Config.get("robot_has_light")

        if Server.robot_has_speaker:
            # Voice
            Server.voice_engine = pyttsx3.init()
            Server.voice_engine.setProperty('voice', Config.get("voice_id"))
            Server.voice_engine.setProperty('rate', Config.get("voice_rate"))
            Server.voice_engine.setProperty('volume', Config.get("voice_volume"))

            # SFX
            SFX.setup()
        else:
            Server.voice_engine = None

        if Server.robot_has_screen:
            # LCD & terminal Initialization
            RST = 24
            DC = 25
            BL = 23
            Server.lcd = LCD_2inch(rst=RST, dc=DC, bl=BL)
            Server.lcd.Init()
            Server.lcd.clear()
            Server.terminal = Terminal("Courier", Server.lcd)
            Server.terminal.header("PiRobot v1.0")
            Server.terminal.text("Starting...")
            Server.pics_path = os.path.join(os.path.dirname(__file__), 'assets/Pics')
            if not os.path.isdir(Server.pics_path):
                Server.pics_path = "/etc/pirobot/assets/Pics"
        else:
            Server.lcd = None
            Server.terminal = None

        # Open UART Port
        await UART.open()

        # Motor Initialization
        Motor.setup()
        if Server.robot_has_screen:
            Server.terminal.text(f"Motor setup... {Motor.get_status()}")

        # Light
        if Server.robot_has_light:
            Light.setup()
            if Server.robot_has_screen:
                Server.terminal.text(f"Light setup... {Light.status}")

        # Camera Initialization
        Camera.setup()
        if Server.robot_has_screen:
            Server.terminal.text(f"Camera setup.. {Camera.status}")

        if Server.robot_has_screen:
            Server.terminal.text("Ready!")

    @staticmethod
    def set_lcd_picture(name):
        if Server.robot_has_screen:
            file_path = os.path.join(Server.pics_path, f"{name}.png")
            if os.path.isfile(file_path):
                image = Image.open(file_path)
                image = image.resize((Server.lcd.height, Server.lcd.width)).convert('RGB')
                Server.lcd.ShowImage(image)
            else:
                logger.info(f"Picture not found {name}")

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
        elif message["type"] == "light" and Server.robot_has_light:
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
        elif message["type"] == "sfx" and Server.robot_has_speaker:
            if message["action"] == "play":
                threading.Thread(target=SFX.play, args=(message["args"]["name"], )).start()
        elif message["type"] == "message":
            if message["action"] == "play":
                Server.play_message(message["args"].get("destination", "lcd"), message["args"]["message"])
        elif message["type"] == "lcd" and Server.robot_has_screen:
            if message["action"] == "display_picture":
                Server.set_lcd_picture(message["args"]["name"])

    @staticmethod
    def play_message(destination, message):
        if message.startswith("!"):
            cmd = message[1:].split(' ')
            if len(cmd) > 1:
                command = cmd[0]
                args = cmd[1:]
                if command == "img":
                    Server.set_lcd_picture(args[0])
                    message = None
                elif command == "play":
                    print(args)
                    message = Games.play(args[0], args[1:])
                else:
                    message = None
            else:
                message = None
        if message is not None:
            if destination == "lcd" and Server.robot_has_screen:
                Server.terminal.text(message)
            elif destination == "audio" and Server.robot_has_speaker:

                if Server.voice_engine._inLoop:
                    Server.voice_engine.endLoop()

                Server.voice_engine.say(message)
                Server.voice_engine.runAndWait()

