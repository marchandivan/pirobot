import json
import socket
import os

from PyQt5.QtGui import QKeySequence


class Client(object):

    def __init__(self, app):
        self.app = app
        self.socket = None
        self.motor_slow_mode = False
        self.host_ip = None
        self.config_path = "config"
        self.actions = {}
        self.controller_mapping = {}
        self.axis_mapping = {}
        if not os.path.isdir(self.config_path):
            self.config_path = "/etc/piremote/config"

        self.load_config()

    def load_config(self):
        with open(os.path.join(self.config_path, "actions.json")) as action_file:
            self.actions = json.load(action_file)

        with open(os.path.join(self.config_path, "controller.json")) as controller_file:
            self.controller_mapping = json.load(controller_file)
            gamepad_absolute_mapping = self.controller_mapping.get("gamepad", {}).get("absolute_axis", {})
            self.axis_mapping = {}
            for code, config in gamepad_absolute_mapping.items():
                action, axis = config["action"], config["axis"]
                if action not in self.axis_mapping:
                    self.axis_mapping[action] = {}
                self.axis_mapping[action][axis] = config
                self.axis_mapping[action][axis]["code"] = code

    def run_action(self, action_id):
        if action_id == "app_close":
            self.app.close()
        elif action_id == "select_host":
            self.app.open_select_host_window()
        elif action_id == "motor_slow_mode":
            self.motor_slow_mode = not self.motor_slow_mode
        elif action_id in self.actions:
            commands = self.actions[action_id]
            for command in commands:
                if "type" in command:
                    self.send_message(command)
        else:
            print(f"Action not found {action_id}")

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

    def gamepad_absolute_axis_callback(self, code, positions):
        gamepad_absolute_mapping = self.controller_mapping.get("gamepad", {}).get("absolute_axis", {})
        code_str = str(code)
        if code_str in gamepad_absolute_mapping:
            action = gamepad_absolute_mapping[code_str]["action"]
            if action in self.axis_mapping:
                x_pos = self.get_normalized_position(action, "x", positions)
                y_pos = self.get_normalized_position(action, "y", positions)
                if action == "motor":
                    self.move_motor(x_pos, y_pos)
                elif action == "camera":
                    self.move_camera(x_pos, y_pos)

    def get_normalized_position(self, action, axis, positions):
        if axis not in self.axis_mapping[action]:
            return 0
        code = self.axis_mapping[action][axis]["code"]
        positions = {str(code): value for code, value in positions.items()}
        if code not in positions:
            return 0
        absolute_position = positions[code]["value"]
        max_pos = self.axis_mapping[action][axis].get("max", positions[code]["max"])
        min_pos = self.axis_mapping[action][axis].get("min", positions[code]["min"])
        value_normalized = float(absolute_position - min_pos) / float(max_pos - min_pos)
        value_normalized = int(-100 + (value_normalized * 200))
        value_normalized = min(100, value_normalized)
        value_normalized = max(-100, value_normalized)
        return value_normalized

    def move_camera(self, x_pos, y_pos):
        if abs(y_pos) < 2:
            self.send_message(dict(type="camera", action="center_position"))
        else:
            position = int(min(max(100 - (100 + y_pos) / 2, 0), 100))
            self.send_message(dict(type="camera", action="set_position", args=dict(position=position)))

    def move_motor(self, x_pos, y_pos):
        if abs(x_pos) == 0 and abs(y_pos) == 0:
            self.send_message(dict(type="motor", action="stop"))
        else:

            right_speed = min(max(-y_pos - x_pos, -100), 100)
            left_speed = min(max(-y_pos + x_pos, -100), 100)

            if self.motor_slow_mode:
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

    def gamepad_key_callback(self, code):
        gamepad_key_mapping = self.controller_mapping.get("gamepad", {}).get("key", {})
        code_str = str(code)
        if code_str in gamepad_key_mapping:
            self.run_action(gamepad_key_mapping[code_str]["action"])
        else:
            print(f"Key not mapped {code}")

    def send_message(self, message):
        try:
            self.socket.sendall(json.dumps(message).encode() + b"\n")
        except:
            # In case of failure try to reconnect
            if self.host_ip is not None:
                print("Unable to send message, reconnect")
                self.connect(self.host_ip)
                self.socket.sendall(json.dumps(message).encode() + b"\n")

    def button_callback(self, action_id):
        self.run_action(action_id)

    def key_press_callback(self, e):
        keyboard_mapping = self.controller_mapping.get("keyboard")
        key_str = QKeySequence(e.key()).toString().upper()
        if key_str in keyboard_mapping:
            self.run_action(keyboard_mapping[key_str]["action"])
        else:
            print(f"Key not found {key_str}")