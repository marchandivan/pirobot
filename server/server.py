from camera import Camera
from handlers.base import BaseHandler
from light import Light
from models import Config
from motor.motor import Motor
from sfx import SFX
from terminal import Terminal
from uart import UART

import logging
import platform
import pyttsx3

if platform.machine() == "aarch64":  # Raspberry Pi
    from lcd.LCD_2inch import LCD_2inch
else:
    from lcd.LCD_Mock import LCD_2inch


logger = logging.getLogger(__name__)


class Server(object):

    def __init__(self):
        # Get capability flags for the robot
        self.robot_has_speaker = Config.get("robot_has_speaker")
        self.robot_has_screen = Config.get("robot_has_screen")
        self.robot_has_light = Config.get("robot_has_light")

        # Load handlers
        BaseHandler.load_handlers()

    async def setup(self):
        # Open UART Port
        await UART.open()
        self._setup()

    def _setup(self):
        if self.robot_has_speaker:
            # Voice
            self.voice_engine = pyttsx3.init()

            # SFX
            SFX.setup()
        else:
            self.voice_engine = None

        if self.robot_has_screen:
            # LCD & terminal Initialization
            RST = 24
            DC = 25
            BL = 23
            self.lcd = LCD_2inch(rst=RST, dc=DC, bl=BL)
            self.lcd.Init()
            self.lcd.clear()
            self.terminal = Terminal("Courier", self.lcd)
            self.terminal.header("PiRobot v1.0")
            self.terminal.text("Starting...")
        else:
            self.lcd = None
            self.terminal = None

        # Motor Initialization
        Motor.setup()
        if self.robot_has_screen:
            self.terminal.text(f"Motor setup... {Motor.get_status()}")

        # Light
        if self.robot_has_light:
            Light.setup()
            if self.robot_has_screen:
                self.terminal.text(f"Light setup... {Light.status}")

        # Camera Initialization
        Camera.setup()
        if self.robot_has_screen:
            self.terminal.text(f"Camera setup.. {Camera.status}")

        if self.robot_has_screen:
            self.terminal.text("Ready!")

    @staticmethod
    def process(message, protocol):
        for handler in BaseHandler.get_handler_for_message_type(message["type"]):
            handler.process(message, protocol)

    def connection_lost(self):
        # Stop the robot in case of lost connection
        logger.warning("Client connection lost, stopping robot")
        Motor.stop()

    def send_status(self, protocol):
        status = {
            "type": "status",
            "robot_name": Config.get("robot_name"),
            "config": Config.export_config(),
        }
        protocol.send_message(status)

