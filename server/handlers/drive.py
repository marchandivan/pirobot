from handlers.base import BaseHandler, register_handler
from motor.motor import Motor


@register_handler("drive")
class DriveHandler(BaseHandler):

    def __init__(self):
        super().__init__()
        self.register_for_message("drive")

    async def process(self, message, protocol):
        if message["action"] == "move":
            Motor.move(**message["args"])
        elif message["action"] == "stop":
            if BaseHandler.state == "patrolling":
                BaseHandler.reset_state()
            Motor.stop()
        elif message["action"] == "patrol" and BaseHandler.state is None:
            BaseHandler.set_state("patrolling")
            Motor.patrol()
