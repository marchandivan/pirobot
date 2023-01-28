import json
import socket

from PyQt5.QtCore import Qt


class Client(object):

    def __init__(self, host_ip):
        # Connect to server
        self.host_ip = host_ip
        self.socket = None
        self.connect()

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET)
            self.socket.connect((self.host_ip, 8000))
        except:
            print(f"Unable to connect to {self.host_ip}")

    def gamepad_right_joystick_callback(self, x_pos, y_pos):
        if abs(y_pos) < 2:
            self.send_message(dict(type="camera", action="center_position"))
        else:
            position = int(min(max(100 - (100 + y_pos) / 2, 0), 100))
            self.send_message(dict(type="camera", action="set_position", args=dict(position=position)))

    def gamepad_joystick_callback(self, x_pos, y_pos):
        if abs(x_pos) == 0 and abs(y_pos) == 0:
            self.send_message(dict(type="motor", action="stop"))
        else:

            right_speed = min(max(-y_pos - x_pos, -100), 100)
            left_speed = min(max(-y_pos + x_pos, -100), 100)

            if left_speed < 0:
                left_orientation = 'B'
            else:
                left_orientation = 'F'

            if right_speed < 0:
                right_orientation = 'B'
            else:
                right_orientation = 'F'

            self.send_message(dict(type="motor", action="move", args=dict(left_orientation=left_orientation,
                                                                          left_speed=abs(left_speed),
                                                                          right_orientation=right_orientation,
                                                                          right_speed=abs(right_speed),
                                                                          duration=10,
                                                                          distance=None,
                                                                          rotation=None,
                                                                          auto_stop=False,
                                                                          )))

    def gamepad_key_callback(self, key):
        if key == 305:
            self.send_message(dict(type="light", action="toggle"))
        elif key == 312:
            self.send_message(dict(type="light", action="blink", args=dict(left_on=False, right_on=True)))
        elif key == 313:
            self.send_message(dict(type="light", action="blink", args=dict(left_on=True, right_on=False)))
        elif key == 311:
            self.send_message(dict(type="sfx", action="play", args=dict(name="bike_horn")))
        elif key == 310:
            self.send_message(dict(type="sfx", action="play", args=dict(name="car_double_horn")))
        else:
            print(key)

    def send_message(self, message):
        try:
            self.socket.sendall(json.dumps(message).encode() + b"\n")
        except:
            # In case of failure try to reconnect
            self.connect()
            self.socket.sendall(json.dumps(message).encode() + b"\n")

    def key_press_callback(self, e):
        if e.key() == Qt.Key_Up:
            self.send_message(dict(type="motor", action="move", args=dict(left_orientation='F',
                                                                          left_speed=100,
                                                                          right_orientation='F',
                                                                          right_speed=100,
                                                                          duration=0.5,
                                                                          distance=None,
                                                                          rotation=None,
                                                                          auto_stop=False,
                                                                          )))
        elif e.key() == Qt.Key_Down:
            self.send_message(dict(type="motor", action="move", args=dict(left_orientation='B',
                                                                          left_speed=100,
                                                                          right_orientation='B',
                                                                          right_speed=100,
                                                                          duration=0.5,
                                                                          distance=None,
                                                                          rotation=None,
                                                                          auto_stop=False,
                                                                          )))
        elif e.key() == Qt.Key_Right:
            self.send_message(dict(type="motor", action="move", args=dict(left_orientation='F',
                                                                          left_speed=100,
                                                                          right_orientation='B',
                                                                          right_speed=100,
                                                                          duration=0.5,
                                                                          distance=None,
                                                                          rotation=None,
                                                                          auto_stop=False,
                                                                          )))
        elif e.key() == Qt.Key_Left:
            self.send_message(dict(type="motor", action="move", args=dict(left_orientation='B',
                                                                          left_speed=100,
                                                                          right_orientation='F',
                                                                          right_speed=100,
                                                                          duration=0.5,
                                                                          distance=None,
                                                                          rotation=None,
                                                                          auto_stop=False,
                                                                          )))
