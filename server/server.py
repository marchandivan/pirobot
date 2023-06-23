from camera import Camera
from light import Light
from motor.motor import Motor
from sfx import SFX

import os
from PIL import Image
import threading


class Server(object):

    @staticmethod
    def setup(lcd):
        Server.lcd = lcd
        Server.pics_path = os.path.join(os.path.dirname(__file__), 'assets/Pics')
        if not os.path.isdir(Server.pics_path):
            Server.pics_path = "/etc/pirobot/assets/Pics"

    @staticmethod
    def set_lcd_picture(name):
        file_path = os.path.join(Server.pics_path, f"{name}.png")
        if os.path.isfile(file_path):
            image = Image.open(file_path)
            image = image.resize((Server.lcd.height, Server.lcd.width)).convert('RGB')
            Server.lcd.ShowImage(image)

    @staticmethod
    def connection_lost():
        # Stop the robot in case of lost connection
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
        elif message["type"] == "light":
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
        elif message["type"] == "sfx":
            if message["action"] == "play":
                threading.Thread(target=SFX.play, args=(message["args"]["name"], )).start()
        elif message["type"] == "lcd":
            if message["action"] == "display_picture":
                Server.set_lcd_picture(message["args"]["name"])
