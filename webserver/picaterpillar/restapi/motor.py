import math
import time
from threading import Timer, Semaphore
from restapi.DFRobot_RaspberryPi_DC_Motor import DFRobot_DC_Motor_IIC

SPEED_REFRESH_INTERVAL = 0.1 # in seconds
MAX_RPM = 42
WHEEL_D = 75  # in mm
ROBOT_WIDTH = 560 # in mm
TIMEOUT = 30 # in seconds

class SpeedController(object):
    """
    Inspired by
    https://www.instructables.com/Speed-Control-of-DC-Motor-Using-PID-Algorithm-STM3/
    """
    KP = 0.4 * SPEED_REFRESH_INTERVAL
    KI = 100/MAX_RPM
    KD = 0.06 * SPEED_REFRESH_INTERVAL

    def __init__(self, interval):
        self.interval = interval
        self.speed_rpm = 0
        self.ref_speed = 0
        self.duty = 0
        self.integration_sum = 0
        self.previous_error = 0
        self.previous_ts = 0
        self.nb_of_turns = 0
        self.clear()

    def clear(self):
        self.speed_rpm = 0
        self.ref_speed = 0
        self.duty = 0
        self.integration_sum = 0
        self.previous_error = 0
        self.previous_ts = 0
        self.nb_of_turns = 0

    def start(self, ref_speed):
        self.clear()
        self.previous_ts = time.time()
        self.ref_speed = ref_speed

    def update_dc(self, current_speed):
        self.speed_rpm = current_speed

        # Update ODO
        now = time.time()
        duration = now - self.previous_ts
        self.nb_of_turns = current_speed * duration / 60
        self.previous_ts = now

        if self.ref_speed == 0:
            self.duty = 0
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


class Motor(object):
    Timers = []
    _iic_motor = None
    _iic_semaphore = Semaphore()

    left_speed_controller = SpeedController(interval=SPEED_REFRESH_INTERVAL)
    right_speed_controller = SpeedController(interval=SPEED_REFRESH_INTERVAL)

    distance = 0
    abs_distance = 0

    target_distance = None

    @staticmethod
    def setup():
        # Motor Initialization
        Motor._iic_motor = DFRobot_DC_Motor_IIC(1, 0x11)
        Motor._iic_motor.set_encoder_enable(DFRobot_DC_Motor_IIC.ALL)
        Motor._iic_motor.set_encoder_reduction_ratio(DFRobot_DC_Motor_IIC.ALL, 190)
        Motor._iic_motor.set_moter_pwm_frequency(1000)

    @staticmethod
    def _cancel_event():
        for timer in Motor.Timers:
            timer.cancel()
        Motor.Timers = []

    @staticmethod
    def _schedule_event(delay, function, args=[], kwargs={}):
        timer = Timer(delay, function, args, kwargs)
        timer.start()
        Motor.Timers.append(timer)

    @staticmethod
    def stop():
        Motor._cancel_event()
        try:
            Motor._iic_semaphore.acquire()
            Motor._iic_motor.motor_stop(DFRobot_DC_Motor_IIC.ALL)
            Motor.left_speed_controller.clear()
            Motor.right_speed_controller.clear()
        finally:
            Motor._iic_semaphore.release()

    @staticmethod
    def _speed_control():
        # Were motors stopped?
        if Motor.right_speed_controller.previous_ts == 0:
            return
        try:
            Motor._iic_semaphore.acquire()
            left_speed_rpm, right_speed_rpm = Motor._iic_motor.get_encoder_speed(DFRobot_DC_Motor_IIC.ALL)
            Motor.right_speed_controller.update_dc(right_speed_rpm)
            Motor.left_speed_controller.update_dc(left_speed_rpm)
            # Update ODO
            avg_nb_of_turns = (Motor.right_speed_controller.nb_of_turns + Motor.left_speed_controller.nb_of_turns) / 2
            Motor.distance += avg_nb_of_turns * math.pi * WHEEL_D
            Motor.abs_distance += abs(avg_nb_of_turns) * math.pi * WHEEL_D

            # Reached target distance, if any?
            if Motor.target_distance is not None and Motor.abs_distance > Motor.target_distance:
                Motor.stop()
                Motor.target_distance = None
            else:
                right_direction = DFRobot_DC_Motor_IIC.CW if Motor.right_speed_controller.duty >= 0 else DFRobot_DC_Motor_IIC.CCW
                left_direction = DFRobot_DC_Motor_IIC.CW if Motor.left_speed_controller.duty >= 0 else DFRobot_DC_Motor_IIC.CCW
                Motor._iic_motor.motor_movement([DFRobot_DC_Motor_IIC.M2], right_direction, abs(Motor.right_speed_controller.duty))
                Motor._iic_motor.motor_movement([DFRobot_DC_Motor_IIC.M1], left_direction, abs(Motor.left_speed_controller.duty))

                Motor._schedule_event(SPEED_REFRESH_INTERVAL, Motor._speed_control)
        finally:
            Motor._iic_semaphore.release()

    @staticmethod
    def move(left_orientation, left_speed, right_orientation, right_speed, duration, distance):
        right_ref_speed = (right_speed if right_orientation == "F" else -right_speed) * (MAX_RPM/100)
        left_ref_speed = (left_speed if left_orientation == "F" else -left_speed) * (MAX_RPM/100)
        Motor._cancel_event()  # Cancel any previously running events

        Motor.right_speed_controller.start(ref_speed=right_ref_speed)
        Motor.left_speed_controller.start(ref_speed=left_ref_speed)
        Motor._speed_control()

        Motor.target_distance = Motor.abs_distance + distance * 1000 if distance is not None else None
        Motor._schedule_event(duration, Motor.stop)

    @staticmethod
    def move_to_target(x, y, speed, timeout):
        orientation = 'F' if y >= 0 else 'B'
        if x == 0:
            Motor.move(left_orientation=orientation,
                       left_speed=speed,
                       right_orientation=orientation,
                       right_speed=speed,
                       duration=timeout,
                       distance=y)
        else:
            R = (y*y + x*x) / (2 * x)
            alpha = math.asin(y / R)
            target_distance = abs(R * alpha)
            if x > 0:
                left_speed = speed
                right_speed = speed * (R / (R + ROBOT_WIDTH / 1000))
            else:
                right_speed = speed
                left_speed = speed * (R / (R + ROBOT_WIDTH / 1000))
            Motor.move(left_orientation=orientation,
                       left_speed=left_speed,
                       right_orientation=orientation,
                       right_speed=right_speed,
                       duration=timeout,
                       distance=target_distance)

    @staticmethod
    def serialize():
        return dict(
            left=Motor.left_speed_controller.serialize(),
            right=Motor.right_speed_controller.serialize(),
            distance=Motor.distance,
            abs_distance=Motor.abs_distance,
        )
