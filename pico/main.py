from machine import Pin, PWM, UART
import utime

STEPS_PER_ROTATION = 230

# Global variables

uart = UART(0)                         # init with given baudrate
uart.init(baudrate=9600, bits=8, parity=None , stop=1, tx=Pin(0), rx=Pin(1)) # init with given parameters


class MotorHandler(object):
    def __init__(self):
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

    def move(self, left_direction, left_speed, right_direction, right_speed):
        left_duty = int(min(100, abs(left_speed)) * 65535/100)
        if left_direction == "F":
            M1M.duty_u16(0)
            M1P.duty_u16(left_duty)
        else:
            M1M.duty_u16(left_duty)
            M1P.duty_u16(0)

        right_duty = int(min(100, abs(right_speed)) * 65535/100)
        if right_direction == "F":
            M2M.duty_u16(0)
            M2P.duty_u16(right_duty)
        else:
            M2M.duty_u16(right_duty)
            M2P.duty_u16(0)

    def stop(self):
        self.move('F', 0, 'F', 0)
        self.target_nb_of_revolutions = None
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
                    self.target_differential_nb_of_revolutions = self.total_differential_nb_of_revolutionstarget_nb_of_revolutions + differential_nb_of_revolutions
                self.timeout_ts = utime.ticks_ms() + timeout * 1000
                self.move(left_direction, left_speed, right_direction, right_speed)
                return True, "OK"
        except Exception as e:
            print(e)
            return False, f"[Motor] Unable to decode arguments {args}"



motor_handler = MotorHandler()

# Initialize encoder Pins
def handle_left_encoder_interrupt(Pin):
    global motor_handler
    if E1B.value() == 1:
        motor_handler.left_direction = "F"
        motor_handler.left_step_counter += 1
    else:
        motor_handler.left_direction = "B"
        motor_handler.left_step_counter -= 1

def handle_right_encoder_interrupt(Pin):
    global motor_handler
    if E2B.value() == 1:
        motor_handler.right_direction = "F"
        motor_handler.right_step_counter += 1
    else:
        motor_handler.right_direction = "B"
        motor_handler.right_step_counter -= 1

E1A=Pin(14,Pin.IN)
E1A.irq(trigger=Pin.IRQ_RISING, handler=handle_left_encoder_interrupt, hard=True)
E1B=Pin(15,Pin.IN)
E2A=Pin(10,Pin.IN)
E2A.irq(trigger=Pin.IRQ_RISING, handler=handle_right_encoder_interrupt, hard=True)
E2B=Pin(11,Pin.IN)
M1M = PWM(Pin(12, Pin.OUT))
M1M.freq(1000)
M1P = PWM(Pin(13, Pin.OUT))
M1P.freq(1000)
M2M = PWM(Pin(9, Pin.OUT))
M2M.freq(1000)
M2P = PWM(Pin(8, Pin.OUT))
M2P.freq(1000)


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

        # Have we reached the target distance?
        motor_handler.update_counters()
except Exception as e:
    print(e)
    raise
finally:
    motor_handler.stop()
    E1A.irq(handler=None)
    E2A.irq(handler=None)

