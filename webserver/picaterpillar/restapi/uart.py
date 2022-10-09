import asyncio
import serial
import serial_asyncio

from picaterpillar import settings
from restapi.models import Config

if settings.DEBUG:
    import rel
    import websocket


class OutputProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        print('port opened', transport)
        transport.serial.rts = False  # You can manipulate Serial object via transport
        transport.write(b'Hello, World!\n')  # Write serial data via transport

    def data_received(self, data):
        if settings.DEBUG:
            from restapi.consumers import UartConsumer
        print('data received', repr(data))
        if UartConsumer.socket is not None:
            UartConsumer.socket.send(data)

    def connection_lost(self, exc):
        print('port closed')
        self.transport.loop.stop()

    def pause_writing(self):
        print('pause writing')
        print(self.transport.get_write_buffer_size())

    def resume_writing(self):
        print(self.transport.get_write_buffer_size())
        print('resume writing')

class UART:
    serial_writer = None
    use_websocket = Config.get('use_uart_websocket')
    websocket_client = None

    @staticmethod
    def open():
        if settings.DEBUG and UART.use_websocket:
            websocket.enableTrace(True)
            UART.websocket_client = websocket.WebSocketApp("ws://raspberrypi.local:8000/ws/uart/",
                                                           on_message=UART.ws_on_message)
            UART.websocket_client.run_forever(dispatcher=rel)

        else:
            loop = asyncio.new_event_loop()
            coro = serial_asyncio.create_serial_connection(loop, OutputProtocol, Config.get("uart_port"), baudrate=Config.get("uart_baudrate"))
            UART.serial_writer, _ = loop.run_until_complete(coro)
            #loop.run_forever()
            #loop.close()

    @staticmethod
    def ws_on_message(ws, message):
        print(message)

    @staticmethod
    def write(data):
        print(data)
        if settings.DEBUG and UART.use_websocket:
            UART.websocket_client.send(data.encode())
        else:
            if UART.serial_writer is not None:
                UART.serial_writer.write(data.encode())
            else:
                print("Unable to send serial message")