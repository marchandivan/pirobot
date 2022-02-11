import sys
from threading import Timer
if sys.platform == "darwin":  # Mac OS
    import unittest.mock as mock

    # Mock smbus (i2c) on Mac OS
    mock_smbus_smbus = mock.Mock()
    mock_smbus_smbus.write_i2c_block_data = lambda *args: print("SMBus.write_i2c_block_data{}".format(args))
    def __mock_read_i2c_block_data(*args):
        print("SMBus.read_i2c_block_data{}".format(args))
        return bytes(0xffffffff)
    mock_smbus_smbus.read_i2c_block_data = __mock_read_i2c_block_data
    mock_smbus = mock.Mock()
    mock_smbus.SMBus = mock.Mock(return_value=mock_smbus_smbus)

    sys.modules['smbus'] = mock_smbus
from restapi.DFRobot_RaspberryPi_DC_Motor import DFRobot_DC_Motor_IIC

SPEED_REFRESH_INTERVAL = 0.5 # in seconds

class Motor:
    Timers = []
    _iic_motor = None

    left_speed_rpm = 0
    right_speed_rpm = 0
    left_dc = 0
    right_dc = 0

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
        Motor.left_speed_rpm = 0
        Motor.right_speed_rpm = 0
        Motor.left_dc = 0
        Motor.right_dc = 0

    @staticmethod
    def get_speed():
        return dict(right=Motor.right_speed_rpm, left=Motor.left_speed_rpm)

    @staticmethod
    def _get_speed(refresh=False):
        Motor.left_speed_rpm, Motor.right_speed_rpm = Motor._iic_motor.get_encoder_speed(DFRobot_DC_Motor_IIC.ALL)
        if refresh:
            Motor._schedule_event(SPEED_REFRESH_INTERVAL, Motor._get_speed, dict(refresh=True))

    @staticmethod
    def move(left_orientation, left_speed, right_orientation, right_speed, duration):
        Motor.right_dc = right_speed if right_orientation == "F" else -right_speed
        Motor.left_dc = left_speed if left_orientation == "F" else -left_speed

        Motor._iic_motor.motor_movement([DFRobot_DC_Motor_IIC.M2], DFRobot_DC_Motor_IIC.CW if right_orientation == "F" else DFRobot_DC_Motor_IIC.CCW, right_speed)
        Motor._iic_motor.motor_movement([DFRobot_DC_Motor_IIC.M1], DFRobot_DC_Motor_IIC.CW if left_orientation == "F" else DFRobot_DC_Motor_IIC.CCW, left_speed)
        Motor._cancel_event() # Cancel any previously running events
        Motor._get_speed(refresh=True)
        Motor._schedule_event(duration, Motor.stop)

    @staticmethod
    def serialize():
        return dict(
            right_dc=Motor.right_dc,
            left_dc=Motor.left_dc,
            left_speed_rpm=Motor.left_speed_rpm,
            right_speed_rpm=Motor.right_speed_rpm
        )
