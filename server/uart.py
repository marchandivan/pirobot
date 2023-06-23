from enum import Enum
import asyncio
import serial
import serial_asyncio
import traceback

from models import Config


class OutputProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        print('port opened', transport)
        transport.serial.rts = False  # You can manipulate Serial object via transport
        transport.write(b'Hello, World!\n')  # Write serial data via transport

    def data_received(self, data):
        buffer = data
        while len(buffer) > 0:
            i = buffer.find(b"\n")
            if i >= 0:
                line = buffer[:i + 1]
                buffer = buffer[i + 1:]
                message = line[:-1].decode()
                UART.dispatch_uart_message(message)
            else:
                break

    def connection_lost(self, exc):
        print('port closed')
        self.transport.loop.stop()

    def pause_writing(self):
        print('pause writing')
        print(self.transport.get_write_buffer_size())

    def resume_writing(self):
        print(self.transport.get_write_buffer_size())
        print('resume writing')


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
    async def open():
        if UART.serial_port is None:
            await UART.open_serial_port()

    @staticmethod
    async def open_serial_port():
        try:
            loop = asyncio.get_event_loop()
            UART.serial_port, protocol = await serial_asyncio.create_serial_connection(
                loop=loop, protocol_factory=OutputProtocol,
                url=Config.get("uart_port"),
                baudrate=Config.get("uart_baudrate"),
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            #UART.serial_port = serial.Serial(
            #    port=Config.get("uart_port"),
            #    baudrate=Config.get("uart_baudrate"),
            #    bytesize=serial.EIGHTBITS,
            #    parity=serial.PARITY_NONE,
            #    stopbits=serial.STOPBITS_ONE
            #)
            #UART.serial_port.reset_input_buffer()
            #threading.Thread(target=UART.read_uart_forever, args=(UART.serial_port,), daemon=True).start()
            #threading.Thread(target=UART.read_uart_forever, args=(UART.serial_port,), daemon=True).start()
        except:
            traceback.print_exc()

    @staticmethod
    def write(data):
        try:
            message = data + "\n"
            if UART.serial_port is not None:
                UART.serial_port.write(message.encode())
            else:
                print("Unable to send serial message")
        except:
            print("Unable to send serial message")

