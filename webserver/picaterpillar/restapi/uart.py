import serial

from restapi.models import Config

class UART(object):
    serial_port = None

    @staticmethod
    def open():
        if UART.serial_port is None:
            UART.serial_port = serial.Serial(
                port=Config.get("uart_port"),
                baudrate=Config.get("uart_baudrate"),
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )

    @staticmethod
    def write(data):
        print(data)
        UART.serial_port.write(data.encode())