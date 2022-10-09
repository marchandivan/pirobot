from restapi.uart import UART
from channels.generic.websocket import WebsocketConsumer


class UartConsumer(WebsocketConsumer):
    socket = None

    def connect(self):
        UartConsumer.socket = self
        self.accept()

    def disconnect(self, close_code):
        UartConsumer.socket = None

    def receive(self, text_data):
        UART.write(text_data)
