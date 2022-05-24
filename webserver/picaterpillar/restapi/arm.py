import copy
import math
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
        FOREARM: [100, 180],
        SHOULDER: [127, 270]
    },
    {
        FOREARM: [145, 180],
        SHOULDER: [0, 41]
    },
    {
        FOREARM: [145, 180],
        SHOULDER: [43, 180]
    },
    {
        FOREARM: [171, 180],
        SHOULDER: [42, 42]
    },
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
            {"id": FOREARM, "angle": 30},
            {"id": WRIST, "angle": 165},
            {"id": SHOULDER, "angle": 42},
        ]
    },
    "pickup": {
        "name": "Pickup From Floor",
        "moves": [
            {"id": SHOULDER, "angle": 42},
            {"id": WRIST, "angle": 25},
            {"id": FOREARM, "angle": 170},
        ]
    },
    "grab": {
        "name": "Grab From Floor",
        "moves": [
            {"id": SHOULDER, "angle": 42},
            {"id": WRIST, "angle": 170},
            {"id": FOREARM, "angle": 110},
        ]
    },
    "drop": {
        "name": "Drop on platform",
        "moves": [
            {"id": FOREARM, "angle": 30},
            {"id": WRIST, "angle": 165},
            {"id": SHOULDER, "angle": 215},
        ]
    },
}

class Arm(object):
    status = "UK"
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
            Arm.status = "KO"
        else:
            Arm.servo_controller.begin()  # servo control begin
            Arm.status = "OK"
        Arm.move_to_position("backup_camera")
        Arm.move(CLAW, SERVOS_CONFIG[CLAW]['max_angle'])

    @staticmethod
    def _in_exclusion_zone(id, angle, position=None):
        if position is None:
            position = Arm.position
        for exclusion_zone in EXCLUSION_ZONES:
            if id in exclusion_zone:
                if angle < exclusion_zone.get(id)[0] or angle > exclusion_zone.get(id)[1]:
                    continue
                else:
                    for other_id in [i for i in exclusion_zone.keys() if i != id]:
                        all_match = True
                        if position[other_id] < exclusion_zone[other_id][0] or position[other_id] > exclusion_zone[other_id][1]:
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
    def move(id, angle, wait=True, lock_wrist=False):
        servo_config = SERVOS_CONFIG.get(id)
        if servo_config is None:
            return False, f"Unknown servo ID: {id}"

        max_angle = servo_config.get("max_angle")
        if angle < 0 or angle > max_angle:
            return False, f"Invalid angle: {angle}"

        if Arm._in_exclusion_zone(id, angle):
            return False, "Moving to an exclusion zone"

        if id == FOREARM and lock_wrist:
            forearm_angle = Arm.position[FOREARM]
            wrist_angle = Arm.position[WRIST]
            step = int(math.copysign(1, angle - forearm_angle))
            for i in range(abs(angle - forearm_angle)):
                Arm.move(id=FOREARM, angle=forearm_angle + (i + 1) * step, wait=wait, lock_wrist=False)
                Arm.move(id=WRIST, angle=wrist_angle - (i + 1) * step, wait=wait, lock_wrist=False)
        else:
            Arm.servo_controller.move(servo_config.get("id"), angle * 180 / max_angle)

            if wait:
                speed = servo_config.get('speed')
                time.sleep(1.5 * speed * abs(Arm.position[id] - angle) / 60)
            Arm.position[id] = angle
        return  True, "Success"

    @staticmethod
    def move_to_position(position_id, lock_wrist=False):
        position = PRESET_POSITIONS.get(position_id)
        if position is None:
            return False, f"Unknown position ID: {position_id}"

        # Lock wrist?
        move_by_id = {move.get('id'): move.get('angle') for move in position.get('moves')}
        if lock_wrist and WRIST in move_by_id and FOREARM in move_by_id:
            moves = []
            wrist_angle = move_by_id.get(WRIST) + move_by_id.get(FOREARM) - Arm.position.get(FOREARM)
            # First adjust wrist
            moves.append(dict(id=WRIST, angle=wrist_angle))
            moves.append(dict(id=FOREARM, angle=move_by_id.get(FOREARM), lock_wrist=True))
            if SHOULDER in move_by_id:
                moves.append(dict(id=SHOULDER, angle=move_by_id.get(SHOULDER)))
        else:
            moves = copy.deepcopy(position.get("moves"))

        # Try to re-arrange moves to avoid exclusion zones
        servo_position = copy.deepcopy(Arm.position)
        sorted_moves = []
        nb_of_moves = 0
        while len(moves) > 0:
            for i in range(len(moves)):
                move = moves.pop(0)
                if not Arm._in_exclusion_zone(move.get("id"), move.get("angle"), servo_position):
                    servo_position[move.get('id')] = move.get('angle')
                    sorted_moves.append(move)
                else:
                    moves.append(move)
            # No new moves found?
            if len(sorted_moves) == nb_of_moves:
                return False, "Moving to an exclusion zone"
            nb_of_moves = len(sorted_moves)

        for move in sorted_moves:
            success, message = Arm.move(id=move.get("id"), angle=move.get("angle"), lock_wrist=move.get('lock_wrist', False))
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
