from enum import Enum
import serial
import threading
import traceback

from picaterpillar import settings
from restapi.models import Config

if settings.DEBUG:
    import websocket


class MessageOriginator(Enum):
    motor = "M"
    battery = "B"


class MessageType(Enum):
    status = "S"


class UART:
    class ConsumerConfig(object):
        def __init__(self, name, consumer, originator, message_type):
            self.name = name
            self.consumer = consumer
            self.originator = originator
            self.message_type = message_type

    serial_port = None
    use_websocket = Config.get('use_uart_websocket')
    websocket_client = None
    consumers = {}

    @staticmethod
    def register_consumer(name, consumer, originator=None, message_type=None):
        UART.consumers[name] = UART.ConsumerConfig(name=name, consumer=consumer, originator=originator, message_type=message_type)

    @staticmethod
    def unregister_consumer(name):
        del UART.consumers[name]

    @staticmethod
    def read_uart_forever(port):
        buffer = bytearray()
        while True:
            try:
                if port.in_waiting > 0:
                    buffer += port.read(port.in_waiting)
                i = buffer.find(b"\n")
                if i >= 0:
                    line = buffer[:i + 1]
                    buffer = buffer[i + 1:]
                    message = line[:-1].decode()
                    UART.dispatch_uart_message(message)
            except:
                print("Unable to read UART message")
                # printing stack trace
                traceback.print_exc()

    @staticmethod
    def dispatch_uart_message(message):
        message_parts = message.split(':')
        originator = message_parts[0]
        message_type = message_parts[1]
        for consumer_config in UART.consumers.values():
            if consumer_config.originator is not None and consumer_config.originator.value != originator:
                continue
            if consumer_config.message_type is not None and consumer_config.message_type.value != message_type:
                continue
            consumer_config.consumer.receive_uart_message(message_parts[2:], originator, message_type)

    @staticmethod
    def run_websocket_forever(client):
        client.run_forever()

    @staticmethod
    def open():
        if settings.DEBUG and UART.use_websocket:
            UART.connect_websocket()
        elif UART.serial_port is None:
            UART.open_uart()

    @staticmethod
    def connect_websocket():
        websocket.enableTrace(True)
        UART.websocket_client = websocket.WebSocketApp("ws://raspberrypi.local:8000/ws/uart/",
                                                       on_close=UART.ws_on_close,
                                                       on_message=UART.ws_on_message)
        threading.Thread(target=UART.run_websocket_forever, args=(UART.websocket_client,), daemon=True).start()

    @staticmethod
    def open_uart():
        try:
            UART.serial_port = serial.Serial(
                port=Config.get("uart_port"),
                baudrate=Config.get("uart_baudrate"),
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            threading.Thread(target=UART.read_uart_forever, args=(UART.serial_port,), daemon=True).start()
        except:
            traceback.print_exc()

    @staticmethod
    def ws_on_message(ws, message):
        UART.dispatch_uart_message(message)

    @staticmethod
    def ws_on_close(ws, close_status_code, close_msg):
        UART.connect_websocket()

    @staticmethod
    def write(data):
        try:
            message = data + "\n"
            if settings.DEBUG and UART.use_websocket:
                UART.websocket_client.send(message.encode())
            else:
                if UART.serial_port is not None:
                    UART.serial_port.write(message.encode())
                else:
                    print("Unable to send serial message")
        except:
            print("Unable to send serial message")

