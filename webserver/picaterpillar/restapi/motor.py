import sys
from threading import Timer
if sys.platform == "darwin":  # Mac OS
    import unittest.mock as mock

    # Mock smbus (i2c) on Mac OS
    mock_smbus_smbus = mock.Mock()
    mock_smbus_smbus.write_i2c_block_data = lambda *args: print("SMBus.write_i2c_block_data{}".format(args))
    def __mock_read_i2c_block_data(*args):
        print("SMBus.read_i2c_block_data{}".format(args))
        return bytes([0, 40])
    mock_smbus_smbus.read_i2c_block_data = __mock_read_i2c_block_data
    mock_smbus = mock.Mock()
    mock_smbus.SMBus = mock.Mock(return_value=mock_smbus_smbus)

    sys.modules['smbus'] = mock_smbus
from restapi.DFRobot_RaspberryPi_DC_Motor import DFRobot_DC_Motor_IIC

SPEED_REFRESH_INTERVAL = 0.5 # in seconds
MAX_RPM = 52

class SpeedController(object):
    """
    Inspired by
    https://www.instructables.com/Speed-Control-of-DC-Motor-Using-PID-Algorithm-STM3/
    """
    KP = 0.1
    KI = 10
    KD = 1

    def __init__(self):
        self.clear()

    def clear(self):
        self.speed_rpm = 0
        self.ref_speed = 0
        self.duty = 0
        self.integration_sum = 0
        self.previous_error = 0
        self.interval = 0

    def start(self, ref_speed, interval):
        self.ref_speed = ref_speed
        self.interval = interval

    def update_dc(self, current_speed):
        current_error = self.ref_speed - current_speed
        self.integration_sum += (current_error * self.interval)
        self.duty = self.KP * current_error + self.KI * self.integration_sum + self.KD * 1000 * (current_error - self.previous_error) / self.interval
        self.duty = max(-100, min(100, self.duty))
        self.previous_error = current_error

    def serialize(self):
        return dict(duty=self.duty, ref_speed=self.ref_speed, speed_rpm=self.speed_rpm)

class Motor(object):
    Timers = []
    _iic_motor = None

    left_speed_controller = SpeedController()
    right_speed_controller = SpeedController()

    @staticmethod
    def setup():
        # Motor Initialization
        Motor._iic_motor = DFRobot_DC_Motor_IIC(1, 0x11)
        Motor._iic_motor.set_encoder_enable(DFRobot_DC_Motor_IIC.ALL)
        Motor._iic_motor.set_encoder_reduction_ratio(DFRobot_DC_Motor_IIC.ALL, 150)
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
        Motor._iic_motor.motor_stop(DFRobot_DC_Motor_IIC.ALL)
        Motor._cancel_event()
        Motor.left_speed_controller.clear()
        Motor.right_speed_controller.clear()

    @staticmethod
    def _speed_control():
        left_speed_rpm, right_speed_rpm = Motor._iic_motor.get_encoder_speed(DFRobot_DC_Motor_IIC.ALL)
        Motor.right_speed_controller.update_dc(right_speed_rpm)
        Motor.left_speed_controller.update_dc(left_speed_rpm)

        right_direction = DFRobot_DC_Motor_IIC.CW if Motor.right_speed_controller.duty > 0 else DFRobot_DC_Motor_IIC.CCW
        left_direction = DFRobot_DC_Motor_IIC.CW if Motor.left_speed_controller.duty > 0 else DFRobot_DC_Motor_IIC.CCW
        Motor._iic_motor.motor_movement([DFRobot_DC_Motor_IIC.M2], right_direction, abs(Motor.right_speed_controller.duty))
        Motor._iic_motor.motor_movement([DFRobot_DC_Motor_IIC.M1], left_direction, abs(Motor.left_speed_controller.duty))

        Motor._schedule_event(SPEED_REFRESH_INTERVAL, Motor._speed_control)

    @staticmethod
    def move(left_orientation, left_speed, right_orientation, right_speed, duration):
        right_ref_speed = (right_speed if right_orientation == "F" else -right_speed) * (MAX_RPM/100)
        left_ref_speed = (left_speed if left_orientation == "F" else -left_speed) * (MAX_RPM/100)
        Motor._cancel_event() # Cancel any previously running events

        Motor.right_speed_controller.start(ref_speed=right_ref_speed, interval=SPEED_REFRESH_INTERVAL)
        Motor.left_speed_controller.start(ref_speed=left_ref_speed, interval=SPEED_REFRESH_INTERVAL)
        Motor._speed_control()

        Motor._schedule_event(duration, Motor.stop)

    @staticmethod
    def serialize():
        return dict(
            left=Motor.left_speed_controller.serialize(),
            right=Motor.right_speed_controller.serialize(),
        )
