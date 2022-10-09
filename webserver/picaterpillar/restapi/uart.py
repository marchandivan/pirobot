import serial
import threading

from picaterpillar import settings
from restapi.models import Config

if settings.DEBUG:
    import rel
    import websocket


class UART:
    serial_port = None
    use_websocket = Config.get('use_uart_websocket')
    websocket_client = None
    consumers = {}

    @staticmethod
    def register_consumer(name, consumer):
        UART.consumers[name] = consumer

    @staticmethod
    def read_forever(port):
        while True:
            line = port.readline()
            if settings.DEBUG and UartConsumer.socket is not None:
                if "websocket" in UART.consumers:
                    UART.consumers["websocket"].socket.send(line.decode()[:-1])

    @staticmethod
    def open():
        if settings.DEBUG and UART.use_websocket:
            websocket.enableTrace(True)
            UART.websocket_client = websocket.WebSocketApp("ws://raspberrypi.local:8000/ws/uart/",
                                                           on_message=UART.ws_on_message)
            UART.websocket_client.run_forever(dispatcher=rel)

        elif UART.serial_port is None:
            UART.serial_port = serial.Serial(
                port=Config.get("uart_port"),
                baudrate=Config.get("uart_baudrate"),
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            t = threading.Thread(target=UART.read_forever, args=(UART.serial_port,))
            t.start()

    @staticmethod
    def ws_on_message(ws, message):
        print(message)

    @staticmethod
    def write(data):
        print(data)
        if settings.DEBUG and UART.use_websocket:
            UART.websocket_client.send(data.encode())
        else:
            if UART.serial_port is not None:
                UART.serial_port.write(data.encode())
            else:
                print("Unable to send serial message")

