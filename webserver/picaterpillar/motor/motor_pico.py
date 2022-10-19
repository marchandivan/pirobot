import math

from restapi.models import Config
from restapi.uart import UART, MessageOriginator, MessageType


class PicoMotor(object):
    status = "UK"

    distance = 0.0
    abs_distance = 0.0
    rotation = 0.0
    original_rotation = None
    left_us_distance = 0.0
    front_us_distance = 0.0
    right_us_distance = 0.0
    pos_x = 0
    pos_y = 0

    left_speed = 0
    left_duty = 0
    right_speed = 0
    right_duty = 0

    target_distance = None
    target_rotation = None

    max_rpm = None
    wheel_d = None
    robot_width = None

    obstacles = []

    @staticmethod
    def setup():
        # Open UART Port
        UART.open()
        # Motor Initialization
        PicoMotor.max_rpm = Config.get("max_rpm")
        PicoMotor.wheel_d = Config.get("wheel_d")
        PicoMotor.robot_width = Config.get("robot_width")
        PicoMotor.status = "OK"
        UART.register_consumer("motor_controller", PicoMotor, MessageOriginator.motor, MessageType.status)

    @staticmethod
    def receive_uart_message(message, originator, message_type):
        PicoMotor.left_duty = int(message[0])
        PicoMotor.left_speed = int(message[1])
        PicoMotor.right_duty = int(message[2])
        PicoMotor.right_speed = int(message[3])
        PicoMotor.distance = float(message[4]) * math.pi * PicoMotor.wheel_d / 1000
        PicoMotor.abs_distance = float(message[5]) * math.pi * PicoMotor.wheel_d
        PicoMotor.rotation = float(message[6]) * 180 * PicoMotor.wheel_d / PicoMotor.robot_width
        PicoMotor.left_us_distance = float(message[7])
        PicoMotor.front_us_distance = float(message[8])
        PicoMotor.right_us_distance = float(message[9])

    @staticmethod
    def stop():
        UART.write("M:S")

    @staticmethod
    def move(left_orientation, left_speed, right_orientation, right_speed, duration, distance, rotation):
        nb_of_revolutions = 0
        if distance is not None:
            nb_of_revolutions = 1000 * distance / (math.pi * PicoMotor.wheel_d)
        differential_nb_of_revolutions = 0
        if rotation is not None:
            differential_nb_of_revolutions = rotation * PicoMotor.robot_width / (180.0 * PicoMotor.wheel_d)
        UART.write(
            f"M:M:{left_orientation}:{int(left_speed)}:{right_orientation}:{int(right_speed)}:{nb_of_revolutions:.2f}:{differential_nb_of_revolutions:.2f}:{duration}"
        )

    @staticmethod
    def get_motor_status():
        return {"speed_rpm": PicoMotor.left_speed, "duty": PicoMotor.left_duty}, {"speed_rpm": PicoMotor.right_speed, "duty": PicoMotor.right_duty}

    @staticmethod
    def get_distance():
        return PicoMotor.distance, PicoMotor.abs_distance

    @staticmethod
    def get_us_distances():
        return PicoMotor.left_us_distance, PicoMotor.front_us_distance, PicoMotor.right_us_distance

    @staticmethod
    def get_position():
        return PicoMotor.pos_x, PicoMotor.pos_y, PicoMotor.rotation

    @staticmethod
    def get_obstacles():
        return PicoMotor.obstacles
