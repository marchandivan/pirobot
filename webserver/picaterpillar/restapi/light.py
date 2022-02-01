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


class Light(object):
    left_on = False
    right_on = False

    @staticmethod
    def setup():
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LEFT_LIGHT_PIN, GPIO.OUT)
        GPIO.setup(LEFT_LIGHT_PIN, GPIO.OUT)
        GPIO.output(LEFT_LIGHT_PIN, GPIO.LOW)
        GPIO.output(RIGHT_LIGHT_PIN, GPIO.LOW)
        Light.left_on = False
        Light.right_on = False

    @staticmethod
    def set(left_on, right_on):
        GPIO.output(LEFT_LIGHT_PIN, GPIO.HIGH if left_on else GPIO.LOW)
        GPIO.output(RIGHT_LIGHT_PIN, GPIO.HIGH if right_on else GPIO.LOW)

    @staticmethod
    def serialize():
        return {
            'left_on': Light.left_on,
            'right_on': Light.right_on
        }
