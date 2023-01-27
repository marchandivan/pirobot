from restapi.uart import UART


class ServoHandler():

    @staticmethod
    def move(servo_id, position):
        position = int(max(0, min(100, position)))
        UART.write(f"S:M:{servo_id}:{int(position)}")

    @staticmethod
    def stop():
        UART.write("S:S")