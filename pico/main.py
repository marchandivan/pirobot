from machine import Pin, PWM, UART
import utime

STEPS_PER_ROTATION = 230

# Global variables
step_counter = 0
forward = True
target_nb_steps = None

uart = UART(0)                         # init with given baudrate
uart.init(baudrate=9600, bits=8, parity=None , stop=1, tx=Pin(0), rx=Pin(1)) # init with given parameters


# Initialize encoder Pins
def handle_encoder_interrupt(Pin):
    global step_counter, forward
    forward = E2.value() == 1
    step_counter += 1

E1=Pin(14,Pin.IN)
E1.irq(trigger=Pin.IRQ_RISING, handler=handle_encoder_interrupt, hard=True)
E2=Pin(15,Pin.IN)
M1M = PWM(Pin(12, Pin.OUT))
M1M.freq(1000)
M1P = PWM(Pin(13, Pin.OUT))
M1P.freq(1000)
M2M = PWM(Pin(9, Pin.OUT))
M2M.freq(1000)
M2P = PWM(Pin(8, Pin.OUT))
M2P.freq(1000)


# Motor move
def move(left_direction, left_speed, right_direction, right_speed):
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

def stop():
    move('F', 0, 'F', 0)
    target_nb_steps = None

def process_motor_command(args):
    global target_nb_steps, step_counter
    try:
        if args[0] == "S":
            stop()
            return True, "OK"
        else:
            left_direction, left_speed, right_direction, right_speed, nb_rotations = args
            target_nb_steps = step_counter + int(float(nb_rotations) * STEPS_PER_ROTATION)
            move(left_direction, int(left_speed), right_direction, int(right_speed))
            return True, "OK"
            
    except:
        return False, f"[Motor] Unable to decode arguments {args}"


def process_command(cmd):
    command = cmd.split(':')
    sensor = command[0]
    args = command[1:]
    if sensor == "M":
        return process_motor_command(args)
    else:
        return False, f"Unknown sensor {sensor}"
    
#previous_ts = None
#previous_counter = None

try:
    while True:
        ts = utime.ticks_ms()
    
#         if previous_ts is not None :
#             rotation = float(counter - previous_counter) / STEPS_PER_ROTATION
#             speed = 60000.0 * rotation / (ts - previous_ts)
#         previous_counter = counter
#         previous_ts = ts
#         print(f"Moving {'forward' if forward else 'backward'} at {speed} rpm")
#         print(f"Total rotation: {counter / STEPS_PER_ROTATION}")
        if uart.txdone():
            data = uart.read()
            if data is not None and len(data) > 0:
                cmd = data.decode()
                success, data = process_command(cmd)
                print(success, data)

        # Have we reached the target distance?
        if target_nb_steps is not None and step_counter > target_nb_steps:
            stop()
finally:
    stop()
    E1.irq(handler=None)
