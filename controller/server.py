from camera import Camera
from light import Light
from motor.motor import Motor
from sfx import SFX

import threading


class Server(object):

    @staticmethod
    def process(message):
        # Motor
        if message["type"] == "motor":
            if message["action"] == "move":
                Motor.move(**message["args"])
            elif message["action"] == "stop":
                Motor.stop()
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
        elif message["type"] == "sfx":
            if message["action"] == "play":
                threading.Thread(target=SFX.play, args=(message["args"]["name"], )).start()
