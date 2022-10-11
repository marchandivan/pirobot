from channels.generic.websocket import WebsocketConsumer

from picaterpillar import settings
from restapi.uart import UART


class UartConsumer(WebsocketConsumer):
    socket = None

    def receive_uart_message(self, message, originator, message_type):
        raw_message = ":".join([originator, message_type] + message)
        self.socket.send(raw_message)

    def connect(self):
        UartConsumer.socket = self
        if settings.DEBUG:
            UART.register_consumer("websocket", self)
        self.accept()

    def disconnect(self, close_code):
        UartConsumer.socket = None

    def receive(self, text_data):
        UART.write(text_data)
