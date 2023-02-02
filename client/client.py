import json
import socket

from PyQt5.QtCore import Qt


class Client(object):

    def __init__(self, app):
        self.app = app
        self.socket = None
        self.trimmer_mode = False
        self.host_ip = None

    def __del__(self):
        if self.socket is not None:
            self.socket.close()

    def connect(self, host_ip):
        try:
            if self.socket is not None:
                self.socket.close()
            self.socket = socket.socket(socket.AF_INET)
            self.socket.settimeout(1)
            self.socket.connect((host_ip, 8000))
            self.host_ip = host_ip
        except:
            print(f"Unable to connect to {host_ip}")
            raise

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

            if self.trimmer_mode:
                right_speed = int(0.3 * right_speed)
                left_speed = int(0.3 * left_speed)

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
            self.send_message(dict(type="sfx", action="play", args=dict(name="blinker")))
        elif key == 313:
            self.send_message(dict(type="light", action="blink", args=dict(left_on=True, right_on=False)))
            self.send_message(dict(type="sfx", action="play", args=dict(name="blinker")))
        elif key == 311:
            self.send_message(dict(type="sfx", action="play", args=dict(name="bike_horn")))
        elif key == 310:
            self.send_message(dict(type="sfx", action="play", args=dict(name="car_double_horn")))
        elif key == 317:
            self.trimmer_mode = not self.trimmer_mode
        else:
            print(key)

    def send_message(self, message):
        try:
            self.socket.sendall(json.dumps(message).encode() + b"\n")
        except:
            # In case of failure try to reconnect
            if self.host_ip is not None:
                print("Unable to send message, reconnect")
                self.connect(self.host_ip)
                self.socket.sendall(json.dumps(message).encode() + b"\n")

    def button_callback(self, id):
        if id == "light_toggle":
            self.send_message(dict(type="light", action="toggle"))
        elif id == "light_blink_right":
            self.send_message(dict(type="light", action="blink", args=dict(left_on=False, right_on=True)))
            self.send_message(dict(type="sfx", action="play", args=dict(name="blinker")))
        elif id == "light_blink_right":
            self.send_message(dict(type="light", action="blink", args=dict(left_on=True, right_on=False)))
            self.send_message(dict(type="sfx", action="play", args=dict(name="blinker")))
        elif id == "sfx_bike_horn":
            self.send_message(dict(type="sfx", action="play", args=dict(name="bike_horn")))
        elif id == "sfx_car_double_horn":
            self.send_message(dict(type="sfx", action="play", args=dict(name="car_double_horn")))
        else:
            print(id)

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
        elif e.key() == Qt.Key_Q:
            self.app.close()
        elif e.key() == Qt.Key_C:
            self.app.open_select_host_window()
        elif e.key() == Qt.Key_Space:
            self.send_message(dict(type="sfx", action="play", args=dict(name="bike_horn")))
