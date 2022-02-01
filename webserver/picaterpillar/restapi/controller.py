import sys
from threading import Timer
from restapi.light import Light

if sys.platform != "darwin":  # Mac OS
    from restapi.DFRobot_RaspberryPi_DC_Motor import DFRobot_DC_Motor_IIC as Motor
    motor = Motor(1, 0x10)
else:
    from unittest.mock import Mock
    motor = Mock()

# Initialization
motor.set_addr(0x10)
motor.set_encoder_enable(motor.ALL)
motor.set_encoder_reduction_ratio(motor.ALL, 43)
motor.set_moter_pwm_frequency(1000)
Light.setup()


class Controller:
    Timers = []

    @staticmethod
    def _cancel_event():
        for timer in Controller.Timers:
            timer.cancel()
        Motor.Timers = []

    @staticmethod
    def _schedule_event(delay, function, args=[], kwargs={}):
        timer = Timer(delay, function, args, kwargs)
        timer.start()
        Controller.Timers.append(timer)

    @staticmethod
    def stop():
        motor.motor_stop(motor.ALL)
        Controller._cancel_event()

    @staticmethod
    def emergency_stop():
        Motor.emergency_stop()
        Controller._cancel_event()

    @staticmethod
    def move(left_orientation, left_speed, right_orientation, right_speed, duration):
        motor.motor_movement([motor.M1], motor.CW if right_orientation == "F" else motor.CCW, right_speed)
        motor.motor_movement([motor.M2], motor.CW if left_orientation == "F" else motor.CCW, left_speed)
        Controller._cancel_event() # Cancel any previously running events
        Controller._schedule_event(duration, Controller.stop)

    @staticmethod
    def set_light(left_on, right_on):
        Light.set(left_on, right_on)

    @staticmethod
    def blink_light(left_on, right_on):
        Light.blink(left_on, right_on)

    @staticmethod
    def serialize():
        return {
            'light': Light.serialize()
        }
