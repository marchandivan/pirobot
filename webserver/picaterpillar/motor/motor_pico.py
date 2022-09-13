import math

from restapi.models import Config
from restapi.uart import UART

SPEED_REFRESH_INTERVAL = 0.1  # in seconds

class PicoMotor(object):
    status = "UK"

    distance = 0
    abs_distance = 0
    rotation = 0

    target_distance = None
    target_rotation = None

    max_rpm = None
    wheel_d = None
    robot_width = None

    @staticmethod
    def setup():
        # Open UART Port
        UART.open()
        # Motor Initialization
        PicoMotor.max_rpm = Config.get("max_rpm")
        PicoMotor.wheel_d = Config.get("wheel_d")
        PicoMotor.robot_width = Config.get("robot_width")
        PicoMotor.status = "OK"

    @staticmethod
    def stop():
        UART.write("M:S")

    @staticmethod
    def move(left_orientation, left_speed, right_orientation, right_speed, duration, distance, rotation):
        nb_of_turns = 0
        if distance is not None:
            nb_of_turns = 1000 * distance / (math.pi * PicoMotor.wheel_d)
        elif rotation is not None:
            nb_of_turns = rotation
        UART.write(f"M:{left_orientation}:{int(left_speed)}:{right_orientation}:{int(right_speed)}:{nb_of_turns:.2f}")

    @staticmethod
    def get_motor_status():
        return {}, {}

    @staticmethod
    def get_distance():
        return PicoMotor.distance, PicoMotor.abs_distance
