import os
import sys
from threading import Timer

from PIL import Image
from eye_generator import EyeGenerator
from restapi.camera import Camera
from restapi.light import Light
from restapi.motor import Motor
from terminal import Terminal

if sys.platform != "darwin":  # Mac OS
    from lcd.LCD_2inch import LCD_2inch
else:
    from lcd.LCD_Mock import LCD_2inch

# LCD & terminal Initialization
RST = 24
DC = 25
BL = 23
lcd = LCD_2inch(rst=RST, dc=DC, bl=BL)
lcd.Init()
lcd.clear()
terminal = Terminal("Courier", lcd)
terminal.header("Buddy Bot v1.0")
terminal.text("Starting...")

# Motor Initialization
terminal.text("Motor setup...")
Motor.setup()

# Light
terminal.text("Light setup...")
Light.setup()

terminal.text("Ready!")


class Controller(object):
    Timers = []

    @staticmethod
    def _cancel_event():
        for timer in Controller.Timers:
            timer.cancel()
        Controller.Timers = []

    @staticmethod
    def _schedule_event(delay, function, args=[], kwargs={}):
        timer = Timer(delay, function, args, kwargs)
        timer.start()
        Controller.Timers.append(timer)

    @staticmethod
    def stop():
        Motor.stop ()

    @staticmethod
    def move(left_orientation, left_speed, right_orientation, right_speed, duration, distance):
        Motor.move(left_orientation, left_speed, right_orientation, right_speed, duration, distance)

    @staticmethod
    def move_to_target(x, y, speed, timeout):
        Motor.move_to_target(x, y, speed, timeout)

    @staticmethod
    def set_light(left_on, right_on):
        Light.set(left_on, right_on)

    @staticmethod
    def blink_light(left_on, right_on):
        Light.blink(left_on, right_on)

    @staticmethod
    def select_target(x, y):
        Camera.select_target(x, y)

    @staticmethod
    def capture_image(destination):
        if destination == "lcd":
            img = Image.fromarray(Camera.capture_image())
            img = img.resize((lcd.height, lcd.width))
            lcd.ShowImage(img)

    @staticmethod
    def set_lcd_brightness(brightness):
        lcd.bl_DutyCycle(brightness)

    @staticmethod
    def reset_lcd():
        terminal.reset()

    @staticmethod
    def say(destination, text):
        if destination == "lcd":
            terminal.text(text)

    @staticmethod
    def set_mood(mood):
        lcd.ShowImage(EyeGenerator.generate_eyes(mood))

    @staticmethod
    def get_moods():
        return EyeGenerator.get_moods()

    @staticmethod
    def set_lcd_picture(name):
        file_path = os.path.join('assets/Pics/', f"{name}.png")
        if os.path.isfile(file_path):
            image = Image.open(file_path)
            image = image.resize((lcd.height, lcd.width))
            lcd.ShowImage(image)

    @staticmethod
    def serialize():
        return {
            'light': Light.serialize(),
            'moods': EyeGenerator.get_moods(),
            'motor': Motor.serialize()
        }
