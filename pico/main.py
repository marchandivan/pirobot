from machine import ADC, Pin, PWM, UART, Timer
import utime

# Global variables

uart = UART(0)                         # init with given baudrate
uart.init(baudrate=115200, bits=8, parity=None , stop=1, tx=Pin(0), rx=Pin(1)) # init with given parameters
uart.flush()

class Servo(object):
    def __init__(self, pin, range):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(50)
        self.range = range
    
    def move(self, position):
        self.pwm.freq(50)
        duty = self.range[0] + (self.range[1] - self.range[0]) * position / 100
        self.pwm.duty_u16(int(duty))
        

class ServoHandler(object):
    range = [2500, 6200]

    def __init__(self, pins, enable_pin):
        self.servos = []
        for pin in pins:
            self.servos.append(Servo(pin, ServoHandler.range))

        self.enable = Pin(enable_pin, Pin.OUT)
        self.enable.low()

    def stop(self):
        self.enable.low()

    def start(self):
        self.enable.high()
        
    def move(self, servo, position):
        if servo > 0 and servo <= len(self.servos):
            self.servos[servo - 1].move(position)

    def process_command(self, args):
        try:
            command = args[0]
            if command == "S":
                self.stop()
            elif command == "M":
                servo = int(args[1])
                position = int(args[2])
                self.move(servo, position)
            else:
                return False, f"[Servo] Unknonw command {command}"
        except Exception as e:
            print(e)
            return False, f"[Servo] Unable to decode arguments {args}"
        return True, "OK"


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
    REFRESH_INTERVAL = 50  # ms

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
        self.left_speed = 0 # In rpm
        self.left_ref_speed = 0 # In rpm
        self.previous_left_step_counter = 0
        self.left_previous_error = 0
        self.left_integration_sum = 0
        
        self.right_duty = 0
        self.right_speed = 0 # In rpm
        self.right_ref_speed = 0 # In rpm
        self.previous_right_step_counter = 0
        self.right_previous_error = 0
        self.right_integration_sum = 0

        self.previous_ts = utime.ticks_ms()
        self.auto_stop = False
        self.previous_distances = None

        self.target_nb_of_revolutions = None
        self.target_differential_nb_of_revolutions = None
        self.timeout_ts = None

        self.total_nb_of_revolutions = 0
        self.total_abs_nb_of_revolutions = 0
        self.total_differential_nb_of_revolutions = 0
        self.total_abs_differential_nb_of_revolutions = 0

        self.steps_per_rotation = 230
        self.min_distance = 0.01
        self.max_rpm = 200
        self.kp = 0.5
        self.ki = 1.0
        self.kd = 0.1 * 30 / 1000

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

    def move(
            self,
            left_direction,
            left_speed,
            right_direction,
            right_speed,
            timeout,
            nb_of_revolutions=0.0,
            differential_nb_of_revolutions=0.0,
            auto_stop=True
    ):
        self.auto_stop = auto_stop
        if nb_of_revolutions > 0:
            self.target_nb_of_revolutions = self.total_abs_nb_of_revolutions + nb_of_revolutions
        if differential_nb_of_revolutions > 0:
            self.target_differential_nb_of_revolutions = self.total_abs_differential_nb_of_revolutions + differential_nb_of_revolutions
        self.timeout_ts = utime.ticks_ms() + timeout * 1000

        if left_direction == "F":
            self.left_ref_speed = self.max_rpm * left_speed // 100
        else:
            self.left_ref_speed = -self.max_rpm * left_speed // 100

        if right_direction == "F":
            self.right_ref_speed = self.max_rpm * right_speed // 100
        else:
            self.right_ref_speed = -self.max_rpm * right_speed // 100

        interval = max(utime.ticks_ms() - self.previous_ts, MotorHandler.REFRESH_INTERVAL)
        self.update_speeds(interval=interval,force=True)

    def update_speeds(self, interval, force=False):
        interval_s = interval / 1000
        
        if self.left_ref_speed != 0:
            left_current_error = self.left_ref_speed - self.left_speed
            self.left_integration_sum += (left_current_error * interval_s)
            left_duty = self.kp * left_current_error + self.ki * self.left_integration_sum + self.kd * (left_current_error - self.left_previous_error) / interval_s
            left_duty = int(max(-100, min(100, left_duty)))
            self.left_previous_error = left_current_error
        else:
            left_duty = 0
            self.left_previous_error = 0
            self.left_integration_sum = 0

        if self.right_ref_speed != 0:
            right_current_error = self.right_ref_speed - self.right_speed
            self.right_integration_sum += (right_current_error * interval_s)
            right_duty = self.kp * right_current_error + self.ki * self.right_integration_sum + self.kd * (right_current_error - self.right_previous_error) / interval_s
            right_duty = int(max(-100, min(100, right_duty)))
            self.right_previous_error = right_current_error
        else:
            right_duty = 0
            self.right_previous_error = 0
            self.right_integration_sum = 0
        
        if force or left_duty != self.left_duty or right_duty != self.right_duty:
            self.left_duty = left_duty
            self.right_duty = right_duty

            self.standby.high()
            left_duty = int(min(100, abs(self.left_duty)) * 65535/100)
            self.pwm1.duty_u16(left_duty)
            if self.left_duty > 0:
                self.cw1.high()
                self.ccw1.low()
            else:
                self.cw1.low()
                self.ccw1.high()

            right_duty = int(min(100, abs(self.right_duty)) * 65535/100)
            self.pwm2.duty_u16(right_duty)
            if self.right_duty > 0:
                self.cw2.low()
                self.ccw2.high()
            else:
                self.cw2.high()
                self.ccw2.low()

    def stop(self):
        self.move('F', 0, 'F', 0, 0)
        self.standby.low()
        self.target_nb_of_revolutions = None
        self.target_differential_nb_of_revolutions = None
        self.timeout_ts = None
        self.left_integration_sum = 0
        self.left_previous_error = 0
        self.right_integration_sum = 0
        self.right_previous_error = 0


    def get_status(self):
        left_distance, front_distance, right_distance = ultrasonic_handler.distances()
        return f"M:S:{self.left_duty}:{self.left_speed}:{self.right_duty}:{self.right_speed}:{self.total_nb_of_revolutions}:{self.total_abs_nb_of_revolutions}:{self.total_differential_nb_of_revolutions}:{left_distance}:{front_distance}:{right_distance}"

    def adjust_speed(self, current_speed, new_speed):
        if new_speed < 0.05:  # Speed bellow 20 RPM, stop
            self.stop()
        else:
            self.left_ref_speed = self.left_ref_speed * new_speed / current_speed
            self.right_ref_speed = self.right_ref_speed * new_speed / current_speed
        
    def iterate(self):
        # Update rotation counters
        now = utime.ticks_ms()
        interval = (now - self.previous_ts)
        if interval > MotorHandler.REFRESH_INTERVAL:
            speed = abs(self.left_speed / self.max_rpm + self.right_speed / self.max_rpm) / 2
            ref_speed = abs(self.left_ref_speed / self.max_rpm + self.right_ref_speed / self.max_rpm) / 2
            ref_speed = speed
            ref_differential_speed = abs(self.left_speed / self.max_rpm - self.right_speed / self.max_rpm) / 2
            # Avoid collision ?
            if self.auto_stop:
                distances = ultrasonic_handler.distances()
                if self.previous_distances != distances:
                    min_distance = max(0.5 * speed, self.min_distance)
                    distance_to_closest_object = min(distances)
                    if speed > 0 and distance_to_closest_object < min_distance and self.left_duty > 0 and self.right_duty > 0:
                        self.adjust_speed(speed, distance_to_closest_object / 0.5)
                             
                self.previous_distances = distances

            left_nb_of_steps = self.left_step_counter - self.previous_left_step_counter
            self.previous_left_step_counter = self.left_step_counter
            self.left_speed = int(60000 * left_nb_of_steps / (interval * self.steps_per_rotation))
            right_nb_of_steps = (self.previous_right_step_counter - self.right_step_counter)
            self.previous_right_step_counter = self.right_step_counter
            self.right_speed = int(60000 * right_nb_of_steps / (interval * self.steps_per_rotation))
            avg_nb_of_revolutions = (right_nb_of_steps + left_nb_of_steps) / (2 * self.steps_per_rotation)
            self.total_abs_differential_nb_of_revolutions += abs((left_nb_of_steps - right_nb_of_steps) / self.steps_per_rotation)
            self.total_differential_nb_of_revolutions += (left_nb_of_steps - right_nb_of_steps) / self.steps_per_rotation
            self.total_nb_of_revolutions += avg_nb_of_revolutions
            self.total_abs_nb_of_revolutions += abs(avg_nb_of_revolutions)
            self.previous_ts = now

            # Check any targets was reached
            braking_nb_of_revolutions_at_max_speed = 1.0
            if self.target_nb_of_revolutions is not None:
                if self.total_abs_nb_of_revolutions > self.target_nb_of_revolutions:
                    self.stop()
                elif (self.target_nb_of_revolutions - self.total_abs_nb_of_revolutions) < braking_nb_of_revolutions_at_max_speed * ref_speed:
                    self.adjust_speed(ref_speed, (self.target_nb_of_revolutions - self.total_abs_nb_of_revolutions) / braking_nb_of_revolutions_at_max_speed)
                
            if self.target_differential_nb_of_revolutions is not None:
                if self.total_abs_differential_nb_of_revolutions > self.target_differential_nb_of_revolutions:
                    self.stop()
                elif (self.target_differential_nb_of_revolutions - self.total_abs_differential_nb_of_revolutions) < braking_nb_of_revolutions_at_max_speed * ref_differential_speed:
                    self.adjust_speed(ref_differential_speed, (self.target_differential_nb_of_revolutions - self.total_abs_differential_nb_of_revolutions) / braking_nb_of_revolutions_at_max_speed)
            if self.timeout_ts is not None and utime.ticks_ms() > self.timeout_ts:
                print("Timeout!")
                self.stop()
                
            # Run speed regulation
            self.update_speeds(interval)

    def process_command(self, args):
        try:
            command = args[0]
            if command == "S":
                self.stop()
                return True, "OK"
            elif command == "C":
                self.steps_per_rotation = int(args[1])
                self.min_distance = float(args[2])
                self.max_rpm = int(args[3])
                self.kp = float(args[4])
                self.ki = float(args[5])
                self.kd = float(args[6])
                return True, "OK"
            elif command == "M":
                left_direction = args[1]
                left_speed = int(args[2])
                right_direction = args[3]
                right_speed = int(args[4])
                nb_of_revolutions = float(args[5])
                differential_nb_of_revolutions = float(args[6])
                timeout = float(args[7])
                if len(args) > 8:
                    auto_stop = args[8].lower() in ("y", "true")
                else:
                    auto_stop = False

                self.move(
                    left_direction=left_direction,
                    left_speed=left_speed,
                    right_direction=right_direction,
                    right_speed=right_speed,
                    timeout=timeout,
                    nb_of_revolutions=nb_of_revolutions,
                    differential_nb_of_revolutions=differential_nb_of_revolutions,
                    auto_stop=auto_stop,
                )
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
        self.timeout = 0
        self.move_camera = False
        self.deadline = 0
    
    def process_command(self, args):
        try:
            if len(args) > 0:
                self.speed = int(args[0])
            else:
                self.speed = 50
            
            if len(args) > 1:
                self.timeout = int(args[1]) * 1000
            else:
                self.timeout = 0

            if len(args) > 2:
                self.move_camera = args[2].lower() in ("y", "true")
            else:
                self.move_camera = False
            
            if self.speed == 0:
                self.stop()
            else:
                self.running = True
                
            if self.running and self.timeout > 0:
                self.deadline = utime.ticks_add(utime.ticks_ms(), self.timeout)
            else:
                self.deadline = 0

        except Exception as e:
            print(e)
            return False, f"[Patroller] Unable to decode arguments {args}"
        return True, "OK"
    
    def iterate(self):
        now = utime.ticks_ms()
        if self.deadline > 0 and now > self.deadline:
            self.stop()
        elif self.running and self.motor_handler.left_duty == 0 and self.motor_handler.right_duty == 0:
            distances = self.ultrasonic_handler.distances()
            left_distance, front_distance, right_distance = distances
            min_distance = max(0.5 * self.speed / 100, 0.01)
            if min(distances) > min_distance:
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
                self.motor_handler.move("B", self.speed, "F", self.speed, 10, 0, 0.1)
    
    def stop(self):
        self.running = False
        self.deadline = 0
        self.motor_handler.stop()


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
                uart.flush()

            

motor_handler = MotorHandler(
                 pin_e1a=15,
                 pin_e1b=14,
                 pin_e2a=13,
                 pin_e2b=12,
                 pin_standby=5,
                 pin_pwm1=8,
                 pin_cw1=6,
                 pin_ccw1=7,
                 pin_pwm2=9,
                 pin_cw2=11,
                 pin_ccw2=10
    )

servo_handler = ServoHandler(pins=[20, 21, 22, 26, 27], enable_pin=2)
servo_handler.start()
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
status_handler.add_handler(motor_handler, 200)
status_handler.add_handler(battery_handler, 60000)


def process_command(cmd):
    command = cmd.split(':')
    sensor = command[0]
    args = command[1:]
    if sensor == "M":
        return motor_handler.process_command(args)
    elif sensor == "P":
        return patroller_handler.process_command(args)
    elif sensor == "S":
        return servo_handler.process_command(args)
    else:
        return False, f"Unknown sensor {sensor}"

try:
    while True:
        if uart.txdone():
            data = uart.read()
            if data is not None and len(data) > 0:
                commands = data.decode()
                for cmd in [c for c in commands.split('\n') if c]:
                    success, data = process_command(cmd)
                    print(success, data)

        motor_handler.iterate()
        patroller_handler.iterate()
        status_handler.iterate()

finally:
    patroller_handler.stop()
    motor_handler.stop()
    motor_handler.e1a.irq(handler=None)
    motor_handler.e2a.irq(handler=None)
    ultrasonic_handler.stop()

print("Done!")
