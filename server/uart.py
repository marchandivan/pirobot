from enum import Enum
import asyncio
import logging
import serial
import serial_asyncio

from models import Config
from logger import RobotLogger

logger = logging.getLogger(__name__)


class OutputProtocol(asyncio.Protocol):
    def __init__(self):
        self.buffer = ""

    def connection_made(self, transport):
        self.transport = transport
        logger.info(f"UART port opened {transport}")
        transport.serial.rts = False  # You can manipulate Serial object via transport

    def data_received(self, data):
        self.buffer += data.decode()
        while len(self.buffer) > 0:
            i = self.buffer.find("\n")
            if i >= 0:
                line = self.buffer[:i + 1]
                self.buffer = self.buffer[i + 1:]
                message = line[:-1]
                UART.dispatch_uart_message(message)
                RobotLogger.log_message("UART", "R", message)
            else:
                break

    def connection_lost(self, exc):
        logger.info("UART port closed")
        self.transport.loop.stop()

    def pause_writing(self):
        logger.info("UART pause writing")
        logger.info(self.transport.get_write_buffer_size())

    def resume_writing(self):
        logger.info(self.transport.get_write_buffer_size())
        logger.info("UART resume writing")


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
    def dispatch_uart_message(message):
        message_parts = message.split(':')
        originator = message_parts[0]
        message_type = message_parts[1]
        # Received keepalive message?
        if originator == "K":
            UART.write("K:OK")
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
                loop=loop,
                protocol_factory=OutputProtocol,
                url=Config.get("uart_port"),
                baudrate=Config.get("uart_baudrate"),
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
        except:
            logger.error(f"Unable to open serial port {Config.get('uart_port')}", exc_info=True)

    @staticmethod
    def write(data):
        try:
            message = data + "\n"
            if UART.serial_port is not None:
                UART.serial_port.flush()
                UART.serial_port.write(message.encode())
                RobotLogger.log_message("UART", "S", data)
            else:
                logger.warning("Unable to send serial message")
        except:
            logger.error("Unable to send serial message", exc_info=True)

