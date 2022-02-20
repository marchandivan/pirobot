import time

from restapi.DFRobot_RaspberryPi_Expansion_Board import DFRobot_Expansion_Board_IIC as Board
from restapi.DFRobot_RaspberryPi_Expansion_Board import DFRobot_Expansion_Board_Servo as Servo
from restapi.models import Config

CLAW = "claw"
WRIST = "wrist"
FOREARM = "forearm"
SHOULDER = "shoulder"

SERVOS_CONFIG = {
    CLAW: {
        "id": 0,
        "max_angle": 180,
        "speed": 0.11 # Sec / 60 deg
    },
    WRIST: {
        "id": 1,
        "max_angle": 180,
        "speed": 0.15 # Sec / 60 deg
    },
    FOREARM: {
        "id": 2,
        "max_angle": 180,
        "speed": 0.15 # Sec / 60 deg
    },
    SHOULDER: {
        "id": 3,
        "max_angle": 270,
        "speed": 0.11 # Sec / 60 deg
    },
}

DEFAULT_EXCLUSION_ZONES = [
    {
        FOREARM: [0, 15],
        SHOULDER: [90, 180]
    }
]
EXCLUSION_ZONES = Config.get("exclusion_zones", DEFAULT_EXCLUSION_ZONES)

PRESET_POSITIONS = {
    "zero": {
        "name": "Zero",
        "moves": [
            {"id": FOREARM, "angle": 60},
            {"id": WRIST, "angle": 60},
            {"id": SHOULDER, "angle": 42},
        ]
    },
    "backup_camera": {
        "name": "Back up Camera",
        "moves": [
            {"id": FOREARM, "angle": 15},
            {"id": WRIST, "angle": 180},
            {"id": SHOULDER, "angle": 42},
        ]
    },
    "pickup": {
        "name": "Pickup From Floor",
        "moves": [
            {"id": SHOULDER, "angle": 42},
            {"id": WRIST, "angle": 15},
            {"id": FOREARM, "angle": 180},
        ]
    },
    "grab": {
        "name": "Grab From Floor",
        "moves": [
            {"id": SHOULDER, "angle": 42},
            {"id": WRIST, "angle": 160},
            {"id": FOREARM, "angle": 120},
        ]
    },
    "drop": {
        "name": "Drop on platform",
        "moves": [
            {"id": FOREARM, "angle": 85},
            {"id": WRIST, "angle": 120},
            {"id": SHOULDER, "angle": 215},
        ]
    },
}

class Arm(object):
    io_board = None
    servo_controller = None
    position = {
        CLAW: 0,
        WRIST: 0,
        FOREARM: 0,
        SHOULDER: 0,
    }

    @staticmethod
    def setup():
        Arm.io_board = Board(1, 0x12)  # Select i2c bus 1, set address to 0x10
        Arm.servo_controller = Servo(Arm.io_board)
        if Arm.io_board.begin() != Arm.io_board.STA_OK:    # Board begin and check board status
            print("Unable to connect to IO board")
        else:
            Arm.servo_controller.begin()  # servo control begin
        Arm.move_to_position("zero")
        Arm.move_to_position("backup_camera")

    @staticmethod
    def _in_exclusion_zone(id, angle):
        for exclusion_zone in EXCLUSION_ZONES:
            if id in exclusion_zone:
                if angle < exclusion_zone.get(id)[0] or angle > exclusion_zone.get(id)[1]:
                    continue
                else:
                    for other_id in [i for i in exclusion_zone.keys() if i != id]:
                        all_match = True
                        if Arm.position[other_id] < exclusion_zone[other_id][0] or Arm.position[other_id] > exclusion_zone[other_id][1]:
                            all_match = False
                    if all_match:
                        return True
        return False

    @staticmethod
    def get_ids():
        return list(SERVOS_CONFIG.keys())

    @staticmethod
    def get_position_ids():
        return list(PRESET_POSITIONS.keys())

    @staticmethod
    def move(id, angle, wait=True):
        servo_config = SERVOS_CONFIG.get(id)
        if servo_config is None:
            return False, f"Unknown servo ID: {id}"

        max_angle = servo_config.get("max_angle")
        if angle < 0 or angle > max_angle:
            return False, f"Invalid angle: {angle}"

        if Arm._in_exclusion_zone(id, angle):
            return False, "Moving to an exclusion zone"

        Arm.servo_controller.move(servo_config.get("id"), angle * 180 / max_angle)
        Arm.position[id] = angle

        if wait:
            speed = servo_config.get('speed')
            time.sleep(speed * angle / 60)
        return  True, "Success"

    @staticmethod
    def move_to_position(position_id):
        position = PRESET_POSITIONS.get(position_id)
        if position is None:
            return False, f"Unknown position ID: {position_id}"

        for move in position.get("moves"):
            success, message = Arm.move(move.get("id"), move.get("angle"))
            if not success:
                return False, message

        return  True, "Success"

    @staticmethod
    def serialize():
        return {
            "position": Arm.position,
            "ids": Arm.get_ids(),
            "position_ids": Arm.get_position_ids(),
            "config": SERVOS_CONFIG
        }
