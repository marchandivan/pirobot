from threading import Timer

try:
    import RPi.GPIO as GPIO
except:
    import sys
    import fake_rpi
    sys.modules['RPi'] = fake_rpi.RPi
    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO
    import RPi.GPIO as GPIO

LEFT_LIGHT_PIN = 16
RIGHT_LIGHT_PIN = 17
ARM_LIGHT_PIN = 21
BLINK_DURATION = 1
NB_OF_BLINKS = 10


class Light(object):
    status = "UK"
    left_on = False
    right_on = False
    arm_on = False

    Timers = []

    @staticmethod
    def _cancel_event():
        for timer in Light.Timers:
            timer.cancel()
        Light.Timers = []

    @staticmethod
    def _schedule_event(delay, function, args=[], kwargs={}):
        timer = Timer(delay, function, args, kwargs)
        timer.start()
        Light.Timers.append(timer)

    @staticmethod
    def setup():
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LEFT_LIGHT_PIN, GPIO.OUT)
        GPIO.setup(RIGHT_LIGHT_PIN, GPIO.OUT)
        GPIO.setup(ARM_LIGHT_PIN, GPIO.OUT)
        GPIO.output(LEFT_LIGHT_PIN, GPIO.LOW)
        GPIO.output(RIGHT_LIGHT_PIN, GPIO.LOW)
        GPIO.output(ARM_LIGHT_PIN, GPIO.LOW)
        Light.left_on = False
        Light.right_on = False
        Light.arm_on = False
        Light.status = "OK"

    @staticmethod
    def set(left_on, right_on, arm_on):
        Light._cancel_event()
        Light.left_on = left_on
        Light.right_on = right_on
        Light.arm_on = arm_on
        Light._set(left_on, right_on, arm_on)

    @staticmethod
    def _set(left_on, right_on, arm_on):
        GPIO.output(LEFT_LIGHT_PIN, GPIO.HIGH if left_on else GPIO.LOW)
        GPIO.output(RIGHT_LIGHT_PIN, GPIO.HIGH if right_on else GPIO.LOW)
        GPIO.output(ARM_LIGHT_PIN, GPIO.HIGH if arm_on else GPIO.LOW)

    @staticmethod
    def serialize():
        return {
            'status': Light.status,
            'left_on': Light.left_on,
            'right_on': Light.right_on,
            'arm_on': Light.arm_on
        }

    @staticmethod
    def blink(left_on, right_on):
        if left_on or right_on:
            time = 0
            for i in range(NB_OF_BLINKS):
                Light._schedule_event(time, Light._set, kwargs=dict(left_on=left_on, right_on=right_on))
                time += BLINK_DURATION
                Light._schedule_event(time, Light._set, kwargs=dict(left_on=False, right_on=False))
                time += BLINK_DURATION
        Light.set(Light.left_on, Light.right_on)
