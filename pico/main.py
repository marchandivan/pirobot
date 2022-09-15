from machine import Pin, PWM, UART, Timer
import utime

STEPS_PER_ROTATION = 230

# Global variables

uart = UART(0)                         # init with given baudrate
uart.init(baudrate=9600, bits=8, parity=None , stop=1, tx=Pin(0), rx=Pin(1)) # init with given parameters

class UltraSonicSensor(object):
    def __init__(self, pin_trigger, pin_echo):
        self.start = None
        self.stop = 0
        self.distance = 0.0
        self.trigger = Pin(pin_trigger, Pin.OUT)
        self.echo = Pin(pin_echo, Pin.IN)

    def pulse(self):
        if self.start is not None and self.stop > 0:
            self.distance = 0.000343 * (self.stop - self.start) / 2
        self.trigger.off()
        Timer(period=1, mode=Timer.ONE_SHOT, callback=lambda t: self.trigger.on())
        Timer(period=2, mode=Timer.ONE_SHOT, callback=lambda t: self.trigger.off())

        def handle_echo_fall(pin):
            self.stop = utime.ticks_us()
            pin.irq(handler=None)

        def handle_echo_rise(pin):
            self.stop = 0
            self.start = utime.ticks_us()
            pin.irq(handler=handle_echo_fall, trigger=Pin.IRQ_FALLING, hard=True)


        self.echo.irq(handler=handle_echo_rise, trigger=Pin.IRQ_RISING, hard=True)
    
class UltraSonicHandler(object):
    MAX_DISTANCE = 2 # In meter

    def __init__(self, sensors):
        self.sensors = sensors
        self.timers = dict()
        # Time to wait between sensors
        self.wait_time = int(2 * 1000 * UltraSonicHandler.MAX_DISTANCE / 343)

    def run(self):
        for i, (name, sensor) in enumerate(self.sensors.items()):
            if i == 0:
                sensor.pulse()
            else:
                self.timers[name] = Timer(period=self.wait_time * i, mode=Timer.ONE_SHOT, callback=lambda t: sensor.pulse())

    def start(self):
        polling_period = int(self.wait_time * 1.1 * len(self.sensors))
        if len(self.sensors) > 0:
            self.timers["loop"] = Timer(period=polling_period, mode=Timer.PERIODIC, callback=lambda t: self.run())

    def distances(self):
        result = {}
        for name, sensor in self.sensors.items():
            result[name] = sensor.distance
        return result
        
    def stop(self):
        if "loop" in self.timers:
            self.timers["loop"].deinit()
            del self.timers["loop"]

        for timer in self.timers.values():
            timer.deinit()
        self.timers = dict()
        
class MotorHandler(object):
    def __init__(self,
                 pin_e1a,
                 pin_e1b,
                 pin_e2a,
                 pin_e2b,
                 pin_standby,
                 pin_pwm1,
                 pin_cw1,
                 pin_ccw1,
                 pin_pwm2,
                 pin_cw2,
                 pin_ccw2
                 ):
        # Encoder Pins
        self.e1a=Pin(pin_e1a, Pin.IN)
        self.e1b=Pin(pin_e1b, Pin.IN)
        self.e2a=Pin(pin_e2a,Pin.IN)
        self.e2b=Pin(pin_e2b,Pin.IN)

        # Standby
        self.standby = Pin(pin_standby, Pin.OUT)

        # Motor 1 Pins
        self.pwm1 = PWM(Pin(pin_pwm1, Pin.OUT))
        self.pwm1.freq(1000)
        self.cw1 = Pin(pin_cw1, Pin.OUT)
        self.ccw1 = Pin(pin_ccw1, Pin.OUT)

        # Motor 2 Pins
        self.pwm2 = PWM(Pin(pin_pwm2, Pin.OUT))
        self.pwm2.freq(1000)
        self.cw2 = Pin(pin_cw2, Pin.OUT)
        self.ccw2 = Pin(pin_ccw2, Pin.OUT)

        self.left_step_counter = 0
        self.right_step_counter = 0
        self.left_direction = "F"
        self.right_direction = "F"

        self.target_nb_of_revolutions = None
        self.target_differential_nb_of_revolutions = None
        self.timeout_ts = None

        self.previous_left_step_counter = 0
        self.previous_right_step_counter =  0

        self.total_nb_of_revolutions = 0
        self.total_abs_nb_of_revolutions = 0
        self.total_differential_nb_of_revolutions = 0

        # Setup interupts
        def handle_left_encoder_interrupt(pin):
            if self.e1b.value() == 1:
                self.left_direction = "F"
                self.left_step_counter += 1
            else:
                self.left_direction = "B"
                self.left_step_counter -= 1

        def handle_right_encoder_interrupt(pin):
            if self.e2b.value() == 1:
                self.right_direction = "F"
                self.right_step_counter += 1
            else:
                self.right_direction = "B"
                self.right_step_counter -= 1
        self.e1a.irq(trigger=Pin.IRQ_RISING, handler=handle_left_encoder_interrupt, hard=True)
        self.e2a.irq(trigger=Pin.IRQ_RISING, handler=handle_right_encoder_interrupt, hard=True)

    def move(self, left_direction, left_speed, right_direction, right_speed):
        self.standby.high()
        left_duty = int(min(100, abs(left_speed)) * 65535/100)
        self.pwm1.duty_u16(left_duty)
        if left_direction == "F":
            self.cw1.high()
            self.ccw1.low()
        else:
            self.cw1.low()
            self.ccw1.high()

        right_duty = int(min(100, abs(right_speed)) * 65535/100)
        self.pwm2.duty_u16(right_duty)
        if right_direction == "F":
            self.cw2.high()
            self.ccw2.low()
        else:
            self.cw2.low()
            self.ccw2.high()

    def stop(self):
        self.move('F', 0, 'F', 0)
        self.standby.low()
        self.target_nb_of_revolutions = None
        self.target_differential_nb_of_revolutions = None
        self.timeout_ts = None

    def update_counters(self):
        left_nb_of_steps = self.left_step_counter - self.previous_left_step_counter
        self.previous_left_step_counter = self.left_step_counter
        right_nb_of_steps = self.right_step_counter - self.previous_right_step_counter
        self.previous_right_step_counter = self.right_step_counter
        avg_nb_of_revolutions = (right_nb_of_steps + left_nb_of_steps) / (2 * STEPS_PER_ROTATION)
        self.total_differential_nb_of_revolutions += abs((right_nb_of_steps - left_nb_of_steps) / STEPS_PER_ROTATION)
        self.total_nb_of_revolutions += avg_nb_of_revolutions
        self.total_abs_nb_of_revolutions += abs(avg_nb_of_revolutions)
        if self.target_nb_of_revolutions is not None and self.total_abs_nb_of_revolutions > self.target_nb_of_revolutions:
            self.stop()
        if self.target_differential_nb_of_revolutions is not None and self.total_differential_nb_of_revolutions > self.target_differential_nb_of_revolutions:
            self.stop()
        if self.timeout_ts is not None and utime.ticks_ms() > self.timeout_ts:
            self.stop()

    def process_command(self, args):
        try:
            if args[0] == "S":
                self.stop()
                return True, "OK"
            else:
                left_direction = args[0]
                left_speed = int(args[1])
                right_direction = args[2]
                right_speed = int(args[3])
                nb_of_revolutions = float(args[4])
                differential_nb_of_revolutions = float(args[5])
                timeout = float(args[6])

                if nb_of_revolutions > 0:
                    self.target_nb_of_revolutions = self.total_abs_nb_of_revolutions + nb_of_revolutions
                if differential_nb_of_revolutions > 0:
                    self.target_differential_nb_of_revolutions = self.total_differential_nb_of_revolutions + differential_nb_of_revolutions
                self.timeout_ts = utime.ticks_ms() + timeout * 1000
                self.move(left_direction, left_speed, right_direction, right_speed)
                return True, "OK"
        except Exception as e:
            print(e)
            return False, f"[Motor] Unable to decode arguments {args}"



motor_handler = MotorHandler(
                 pin_e1a=15,
                 pin_e1b=14,
                 pin_e2a=13,
                 pin_e2b=12,
                 pin_standby=8,
                 pin_pwm1=7,
                 pin_cw1=6,
                 pin_ccw1=5,
                 pin_pwm2=11,
                 pin_cw2=10,
                 pin_ccw2=9
    )

ultrasonic_handler = UltraSonicHandler(
    sensors={
        "front": UltraSonicSensor(pin_trigger=16, pin_echo=17),
        "back": UltraSonicSensor(pin_trigger=3, pin_echo=4),
        }
    )
ultrasonic_handler.start()
distance = ultrasonic_handler.distances()

def process_command(cmd):
    command = cmd.split(':')
    sensor = command[0]
    args = command[1:]
    if sensor == "M":
        return motor_handler.process_command(args)
    else:
        return False, f"Unknown sensor {sensor}"
    
try:
    while True:
        if uart.txdone():
            data = uart.read()
            if data is not None and len(data) > 0:
                cmd = data.decode()
                success, data = process_command(cmd)
                print(success, data)

        motor_handler.update_counters()

        # Have we reached the target distance?
        if distance != ultrasonic_handler.distances():
            distance = ultrasonic_handler.distances()
            if distance["front"] < 0.05 and motor_handler.left_direction == "F" and motor_handler.right_direction == "F":
                motor_handler.stop()
                pass
finally:
    motor_handler.stop()
    motor_handler.e1a.irq(handler=None)
    motor_handler.e2a.irq(handler=None)
    ultrasonic_handler.stop()

print("Done!")
