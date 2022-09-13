import math
import time
from threading import Semaphore, Timer

from restapi.DFRobot_RaspberryPi_DC_Motor import DFRobot_DC_Motor_IIC
from restapi.models import Config

SPEED_REFRESH_INTERVAL = 0.1  # in seconds

class SpeedController(object):
    """
    Inspired by
    https://www.instructables.com/Speed-Control-of-DC-Motor-Using-PID-Algorithm-STM3/
    """
    KP = 1.0
    KI = 100 / Config.get('max_rpm')
    KD = 0.1 * SPEED_REFRESH_INTERVAL

    def __init__(self, interval):
        self.interval = interval
        self.speed_rpm = 0
        self.ref_speed = 0
        self.duty = 0
        self.integration_sum = 0
        self.previous_error = 0
        self.previous_ts = 0
        self.nb_of_turns = 0
        self.use_speed_control = False
        self.clear()

    def clear(self):
        self.speed_rpm = 0
        self.ref_speed = 0
        self.duty = 0
        self.integration_sum = 0
        self.previous_error = 0
        self.previous_ts = 0
        self.nb_of_turns = 0
        self.use_speed_control = False

    def start(self, ref_speed, use_speed_control):
        self.clear()
        self.previous_ts = time.time()
        self.ref_speed = ref_speed
        self.use_speed_control = use_speed_control

    def update_dc(self, current_speed):
        self.speed_rpm = current_speed

        # Update ODO
        now = time.time()
        duration = now - self.previous_ts
        self.nb_of_turns = current_speed * duration / 60
        self.previous_ts = now

        if not self.use_speed_control or self.ref_speed == 0:
            self.duty = self.ref_speed
        else:
            current_error = self.ref_speed - current_speed
            self.integration_sum += (current_error * self.interval)
            self.duty = self.KP * current_error + self.KI * self.integration_sum + self.KD * (current_error - self.previous_error) / self.interval
            self.duty = max(-100, min(100, self.duty))
            self.previous_error = current_error

    def serialize(self):
        return dict(
            duty=self.duty,
            ref_speed=self.ref_speed,
            speed_rpm=self.speed_rpm,
        )


class DFRobotMotor(object):
    status = "UK"

    Timers = []
    _iic_motor = None
    _iic_semaphore = Semaphore()

    left_speed_controller = SpeedController(interval=SPEED_REFRESH_INTERVAL)
    right_speed_controller = SpeedController(interval=SPEED_REFRESH_INTERVAL)

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
        # Motor Initialization
        DFRobotMotor.max_rpm = Config.get("max_rpm")
        DFRobotMotor.wheel_d = Config.get("wheel_d")
        DFRobotMotor.robot_width = Config.get("robot_width")
        DFRobotMotor.status = "OK"
        DFRobotMotor._iic_motor = DFRobot_DC_Motor_IIC(1, 0x11)
        max_retry = 10
        while max_retry > 0:  # Board begin and check board status
            DFRobotMotor._iic_motor.begin()
            time.sleep(0.1)
            DFRobotMotor._iic_motor.set_encoder_enable(DFRobot_DC_Motor_IIC.ALL)
            time.sleep(0.1)
            DFRobotMotor._iic_motor.set_encoder_reduction_ratio(DFRobot_DC_Motor_IIC.ALL, 190)
            time.sleep(0.1)
            DFRobotMotor._iic_motor.set_moter_pwm_frequency(1000)
            if DFRobotMotor._iic_motor.last_operate_status == DFRobot_DC_Motor_IIC.STA_OK:
                break
            time.sleep(1)
            max_retry -= 1
        if max_retry == 0:
            print(f"Board begin failed: {DFRobotMotor._iic_motor.last_operate_status}")
            DFRobotMotor.status = "KO"
        return DFRobotMotor.status

    @staticmethod
    def _cancel_event():
        for timer in DFRobotMotor.Timers:
            timer.cancel()
        DFRobotMotor.Timers = []

    @staticmethod
    def _schedule_event(delay, function, args=[], kwargs={}):
        timer = Timer(delay, function, args, kwargs)
        timer.start()
        DFRobotMotor.Timers.append(timer)

    @staticmethod
    def stop():
        DFRobotMotor._cancel_event()
        try:
            DFRobotMotor.target_distance = None
            DFRobotMotor.target_rotation = None
            DFRobotMotor._iic_semaphore.acquire()
            DFRobotMotor._iic_motor.motor_stop(DFRobot_DC_Motor_IIC.ALL)
            DFRobotMotor.left_speed_controller.clear()
            DFRobotMotor.right_speed_controller.clear()
        finally:
            DFRobotMotor._iic_semaphore.release()

    @staticmethod
    def _speed_control():
        # Were motors stopped?
        if DFRobotMotor.right_speed_controller.previous_ts == 0:
            return
        try:
            DFRobotMotor._iic_semaphore.acquire()
            left_speed_rpm, right_speed_rpm = DFRobotMotor._iic_motor.get_encoder_speed(DFRobot_DC_Motor_IIC.ALL)
            DFRobotMotor.right_speed_controller.update_dc(right_speed_rpm)
            DFRobotMotor.left_speed_controller.update_dc(left_speed_rpm)
            # Update ODO
            avg_nb_of_turns = (DFRobotMotor.right_speed_controller.nb_of_turns + DFRobotMotor.left_speed_controller.nb_of_turns) / 2
            diff_nb_of_turns = abs(DFRobotMotor.right_speed_controller.nb_of_turns - DFRobotMotor.left_speed_controller.nb_of_turns)
            DFRobotMotor.distance += avg_nb_of_turns * math.pi * DFRobotMotor.wheel_d
            DFRobotMotor.abs_distance += abs(avg_nb_of_turns) * math.pi * DFRobotMotor.wheel_d
            DFRobotMotor.rotation += 2 * 180.0 / math.pi * (diff_nb_of_turns * math.pi * DFRobotMotor.wheel_d) / (DFRobotMotor.robot_width)
            # Reached target distance, if any?
            if DFRobotMotor.target_distance is not None and DFRobotMotor.abs_distance >= DFRobotMotor.target_distance:
                DFRobotMotor._iic_motor.motor_stop(DFRobot_DC_Motor_IIC.ALL)
                DFRobotMotor.left_speed_controller.clear()
                DFRobotMotor.right_speed_controller.clear()
                DFRobotMotor.target_distance = None
            elif DFRobotMotor.target_rotation is not None and DFRobotMotor.rotation >= DFRobotMotor.target_rotation:
                DFRobotMotor._iic_motor.motor_stop(DFRobot_DC_Motor_IIC.ALL)
                DFRobotMotor.left_speed_controller.clear()
                DFRobotMotor.right_speed_controller.clear()
                DFRobotMotor.target_rotation = None
            else:
                right_direction = DFRobot_DC_Motor_IIC.CW if DFRobotMotor.right_speed_controller.duty >= 0 else DFRobot_DC_Motor_IIC.CCW
                left_direction = DFRobot_DC_Motor_IIC.CW if DFRobotMotor.left_speed_controller.duty >= 0 else DFRobot_DC_Motor_IIC.CCW
                DFRobotMotor._iic_motor.motor_movement([DFRobot_DC_Motor_IIC.M2], right_direction, abs(DFRobotMotor.right_speed_controller.duty))
                DFRobotMotor._iic_motor.motor_movement([DFRobot_DC_Motor_IIC.M1], left_direction, abs(DFRobotMotor.left_speed_controller.duty))

                DFRobotMotor._schedule_event(SPEED_REFRESH_INTERVAL, DFRobotMotor._speed_control)
        finally:
            DFRobotMotor._iic_semaphore.release()

    @staticmethod
    def move(left_orientation, left_speed, right_orientation, right_speed, duration, distance, rotation):
        use_speed_control = Config.get("use_speed_control")
        right_ref_duty = (right_speed if right_orientation == "F" else -right_speed)
        right_ref_speed = right_ref_duty * (DFRobotMotor.max_rpm/100)
        left_ref_duty = (left_speed if left_orientation == "F" else -left_speed)
        left_ref_speed = left_ref_duty * (DFRobotMotor.max_rpm/100)
        DFRobotMotor._cancel_event()  # Cancel any previously running events

        DFRobotMotor.right_speed_controller.start(
            ref_speed=right_ref_speed if use_speed_control else right_ref_duty,
            use_speed_control=use_speed_control
        )
        DFRobotMotor.left_speed_controller.start(
            ref_speed=left_ref_speed if use_speed_control else left_ref_duty,
            use_speed_control=use_speed_control)
        DFRobotMotor._speed_control()

        DFRobotMotor.target_distance = DFRobotMotor.abs_distance + distance * 1000 if distance is not None else None
        DFRobotMotor.target_rotation = DFRobotMotor.rotation + rotation if rotation is not None else None
        DFRobotMotor._schedule_event(duration, DFRobotMotor.stop)

    @staticmethod
    def get_motor_status():
        return DFRobotMotor.left_speed_controller.serialize(), DFRobotMotor.left_speed_controller.serialize()

    @staticmethod
    def get_distance():
        return DFRobotMotor.distance, DFRobotMotor.abs_distance
