from handlers.base import BaseHandler, register_handler
from models import Config


@register_handler("configuration")
class ConfigurationHandler(BaseHandler):

    def __init__(self):
        super().__init__()
        self.register_for_message("configuration")

    def process(self, message, protocol):
        success, need_setup = Config.process(message, protocol)
        if success:
            print("Hey")
            if need_setup:
                print("Hey update")
                protocol.server._setup()
            # Update status
            protocol.server.send_status(protocol)
