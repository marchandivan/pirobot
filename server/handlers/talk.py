from handlers.base import BaseHandler, register_handler
from game import Games
from models import Config


@register_handler("talk")
class TalkHandler(BaseHandler):

    def __init__(self):
        super().__init__()
        self.register_for_message("talk")

    def process(self, message, protocol):
        if message["action"] == "play":
            self.play_message(protocol.server, message["args"].get("destination", "lcd"), message["args"]["message"])

    @staticmethod
    def play_message(server, destination, message):
        if message.startswith("!"):
            cmd = message[1:].split(' ')
            if len(cmd) > 1:
                command = cmd[0]
                args = cmd[1:]
                if command == "img" and server.robot_has_screen:
                    server.set_lcd_picture(args[0])
                    message = None
                elif command == "play":
                    message = Games.play(args[0], args[1:])
                else:
                    message = None
            else:
                message = None
        if message is not None:
            if destination == "lcd" and server.robot_has_screen:
                server.terminal.text(message)
            elif destination == "audio" and server.robot_has_speaker:

                if server.voice_engine._inLoop:
                    server.voice_engine.endLoop()

                server.voice_engine.setProperty('voice', Config.get("voice_id"))
                server.voice_engine.setProperty('rate', Config.get("voice_rate"))
                server.voice_engine.setProperty('volume', Config.get("voice_volume"))
                server.voice_engine.say(message)
                server.voice_engine.runAndWait()

