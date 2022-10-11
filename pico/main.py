from machine import ADC, Pin, PWM, UART, Timer
import utime

STEPS_PER_ROTATION = 230

# Global variables

uart = UART(0)                         # init with given baudrate
uart.init(baudrate=9600, bits=8, parity=None , stop=1, tx=Pin(0), rx=Pin(1)) # init with given parameters
uart.flush()

class ServoHandler(object):
    def __init__(self, s1_pin, s2_pin, s3_pin, s4_pin, s5_pin, enable_pin):
        self.s1 = PWM(Pin(s1_pin))
        self.s1.freq(50)
        self.s2 = PWM(Pin(s2_pin))
        self.s2.freq(50)
        self.s3 = PWM(Pin(s3_pin))
        self.s3.freq(50)
        self.s4 = PWM(Pin(s4_pin))
        self.s4.freq(50)
        self.s5 = PWM(Pin(s5_pin))
        self.s5.freq(50)
        
        self.enable = Pin(enable_pin, Pin.OUT)
        self.enable.low()

    def stop(self):
        self.enable.low()

    def start(self):
        self.enable.high()

servo_handler = ServoHandler(s1_pin=20, s2_pin=21, s3_pin=22, s4_pin=26, s5_pin=27, enable_pin=2)
servo_handler.start()
servo_handler.s1.duty_u16(3400)
utime.sleep(1)
servo_handler.stop()

class BatteryHandler(object):
    MAX_BATTERY = 65536
    MIN_BATTERY = 40000
    def __init__(self, pin_adc):
        self.converter = ADC(pin_adc)
        
    def get_battery_level(self):
        value = self.converter.read_u16()
        return int(value * 100 / BatteryHandler.MAX_BATTERY)
    
    def get_status(self):
        return f"B:S:{self.get_battery_level()}"
    
class UltraSonicSensor(object):
    def __init__(self, name, pin_trigger, pin_echo):
        self.name = name
        self.start = None
        self.stop = 0
        self.distance = 0.0
        self.trigger = Pin(pin_trigger, Pin.OUT)
        self.echo = Pin(pin_echo, Pin.IN)
        self.timer = None

    def pulse(self, t=None):
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
        self.timer = None
        # Time to wait between sensors
        self.wait_time = 2 + int(2 * 1000 * UltraSonicHandler.MAX_DISTANCE / 343)

    def run(self):
        for i, sensor in enumerate(self.sensors):
            if i == 0:
                sensor.pulse()
            else:
                sensor.timer = Timer(period=self.wait_time * i, mode=Timer.ONE_SHOT, callback=sensor.pulse)

    def start(self):
        polling_period = int(self.wait_time * 1.1 * len(self.sensors))
        if len(self.sensors) > 0:
            self.timer = Timer(period=polling_period, mode=Timer.PERIODIC, callback=lambda t: self.run())

    def distances(self):
        left, front, right = 0.0, 0.0, 0.0
        for sensor in self.sensors:
            if sensor.name == "left":
                left = sensor.distance
            elif sensor.name == "front":
                front = sensor.distance
            elif sensor.name == "right":
                right = sensor.distance
        return left, front, right
        
    def stop(self):
        if self.timer is not None:
            self.timer.deinit()
            self.timer = None

        for sensor in self.sensors:
            if sensor.timer is not None:
                sensor.timer.deinit()
                sensor.timer = None
        
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

        self.left_duty = 0
        self.right_duty = 0
        self.auto_stop = False
        self.previous_distances = None

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

    def move(self, left_direction, left_speed, right_direction, right_speed, timeout, nb_of_revolutions=0, differential_nb_of_revolutions=0):
        if nb_of_revolutions > 0:
            self.target_nb_of_revolutions = self.total_abs_nb_of_revolutions + nb_of_revolutions
        if differential_nb_of_revolutions > 0:
            self.target_differential_nb_of_revolutions = self.total_differential_nb_of_revolutions + differential_nb_of_revolutions
        self.timeout_ts = utime.ticks_ms() + timeout * 1000

        self.standby.high()
        left_duty = int(min(100, abs(left_speed)) * 65535/100)
        self.pwm1.duty_u16(left_duty)
        if left_direction == "F":
            self.left_duty = left_speed
            self.cw1.high()
            self.ccw1.low()
        else:
            self.left_duty = -left_speed
            self.cw1.low()
            self.ccw1.high()

        right_duty = int(min(100, abs(right_speed)) * 65535/100)
        self.pwm2.duty_u16(right_duty)
        if right_direction == "F":
            self.right_duty = right_speed
            self.cw2.low()
            self.ccw2.high()
        else:
            self.right_duty = -right_speed
            self.cw2.high()
            self.ccw2.low()

    def stop(self):
        self.move('F', 0, 'F', 0, 0)
        self.standby.low()
        self.target_nb_of_revolutions = None
        self.target_differential_nb_of_revolutions = None
        self.timeout_ts = None

    def get_status(self):
        return f"M:S:{self.left_duty}:{self.left_duty}:{self.right_duty}:{self.right_duty}"

    def iterate(self):
        # Avoid collision ?
        if self.auto_stop:
            distances = ultrasonic_handler.distances()
            if self.previous_distances != distances:
                speed = abs(motor_handler.left_duty + motor_handler.right_duty) / 200
                if speed > 0 and min(distances) < 0.5 * speed and motor_handler.left_duty > 0 and motor_handler.right_duty > 0:
                    motor_handler.stop()
            self.previous_distances = distances

        # Update rotation counters
        left_nb_of_steps = self.left_step_counter - self.previous_left_step_counter
        self.previous_left_step_counter = self.left_step_counter
        right_nb_of_steps = self.right_step_counter - self.previous_right_step_counter
        self.previous_right_step_counter = self.right_step_counter
        avg_nb_of_revolutions = (right_nb_of_steps + left_nb_of_steps) / (2 * STEPS_PER_ROTATION)
        self.total_differential_nb_of_revolutions += abs((right_nb_of_steps - left_nb_of_steps) / STEPS_PER_ROTATION)
        self.total_nb_of_revolutions += avg_nb_of_revolutions
        self.total_abs_nb_of_revolutions += abs(avg_nb_of_revolutions)
        
        # Check any targets was reached
        if self.target_nb_of_revolutions is not None and self.total_abs_nb_of_revolutions > self.target_nb_of_revolutions:
            self.stop()
        if self.target_differential_nb_of_revolutions is not None and self.total_differential_nb_of_revolutions > self.target_differential_nb_of_revolutions:
            self.stop()
        if self.timeout_ts is not None and utime.ticks_ms() > self.timeout_ts:
            self.stop()

    def process_command(self, args):
        try:
            command = args[0]
            if command == "S":
                self.stop()
                return True, "OK"
            elif command == "M":
                left_direction = args[1]
                left_speed = int(args[2])
                right_direction = args[3]
                right_speed = int(args[4])
                nb_of_revolutions = float(args[5])
                differential_nb_of_revolutions = float(args[6])
                timeout = float(args[7])

                self.move(left_direction, left_speed, right_direction, right_speed, timeout, nb_of_revolutions, differential_nb_of_revolutions)
                return True, "OK"
            else:
                return False, f"Unknown command: {command}"
        except Exception as e:
            print(e)
            return False, f"[Motor] Unable to decode arguments {args}"

class PatrollerHandler(object):
    
    def __init__(self, motor_handler, ultrasonic_handler, servo_handler):
        self.motor_handler = motor_handler
        self.ultrasonic_handler = ultrasonic_handler
        self.servo_handler = servo_handler
        self.running = False
        self.speed = 0
        self.move_camera = False
    
    def process_command(self, args):
        try:
            if len(args) > 0:
                self.speed = int(args[0])
            else:
                self.speed = 30
            
            if len(args) > 1:
                self.move_camera = bool(args[0])
            else:
                self.move_camera = False
            
            if self.speed == 0:
                self.stop()
            else:
                self.running = True

        except Exception as e:
            print(e)
            return False, f"[Patroller] Unable to decode arguments {args}"
    
    def iterate(self):
        if self.running and self.motor_handler.right_duty == 0 and self.motor_handler.left_duty == 0:
            distances = self.ultrasonic_handler.distances()
            left_distance, front_distance, right_distance = distances
            min_distance = 0.5 * 0.3
            if min(distances) > min_distance * 1.5:
                if self.move_camera:
                    self.servo_handler.s1.duty_u16(4000)
                    utime.sleep(1.0)
                    self.servo_handler.s1.duty_u16(3000)
                    utime.sleep(1.0)
                    self.servo_handler.s1.duty_u16(3400)
                self.motor_handler.move("F", self.speed, "F", self.speed, 10)
            elif right_distance > left_distance:
                self.motor_handler.move("F", self.speed, "B", self.speed, 10, 0, 0.1)
            else:
                self.motor_handler.move("B", self.speed, "F", 30, self.speed, 0, 0.1)
    
    def stop(self):
        self.running = False
        self.motor_controller.stop()

class StatusHandler(object):
    class HandlerConfig(object):
        def __init__(self, handler, refresh_interval, deadline):
            self.handler = handler
            self.refresh_interval = refresh_interval
            self.deadline = deadline
    
    def __init__(self):
        self.handlers = []
        
    def add_handler(self, handler, refresh_interval):
        self.handlers.append(self.HandlerConfig(handler, refresh_interval, utime.ticks_ms()))
    
    def iterate(self):
        for handler_config in self.handlers:
            now = utime.ticks_ms()
            if now > handler_config.deadline:
                handler_config.deadline = utime.ticks_add(now, handler_config.refresh_interval)
                status = handler_config.handler.get_status() + "\n"
                uart.write(status)

            

motor_handler = MotorHandler(
                 pin_e1a=15,
                 pin_e1b=14,
                 pin_e2a=13,
                 pin_e2b=12,
                 pin_standby=8,
                 pin_pwm1=5,
                 pin_cw1=6,
                 pin_ccw1=7,
                 pin_pwm2=11,
                 pin_cw2=10,
                 pin_ccw2=9
    )


ultrasonic_handler = UltraSonicHandler(
    sensors=[
        UltraSonicSensor("right", pin_trigger=17, pin_echo=16),
        UltraSonicSensor("left", pin_trigger=19, pin_echo=18),
        UltraSonicSensor("front", pin_trigger=3, pin_echo=4),
        ]
    )
ultrasonic_handler.start()
previous_distances = ultrasonic_handler.distances()

battery_handler = BatteryHandler(28)

patroller_handler = PatrollerHandler(motor_handler, ultrasonic_handler, servo_handler)

status_handler = StatusHandler()
status_handler.add_handler(motor_handler, 100)
status_handler.add_handler(battery_handler, 60000)

def process_command(cmd):
    command = cmd.split(':')
    sensor = command[0]
    args = command[1:]
    if sensor == "M":
        return motor_handler.process_command(args)
    elif sensor == "P":
        return patroller_handler.process_command(args)
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

        motor_handler.iterate()
        patroller_handler.iterate()
        status_handler.iterate()

finally:
    motor_handler.stop()
    motor_handler.e1a.irq(handler=None)
    motor_handler.e2a.irq(handler=None)
    ultrasonic_handler.stop()

print("Done!")
