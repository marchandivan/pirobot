from models import Config


class BaseHandler(object):
    handlers = dict()
    message_listener = dict()
    event_listener = dict()
    state = None

    @staticmethod
    def get_handler_for_message_type(message_type):
        return [h for h in BaseHandler.message_listener.get(message_type, []) if h.is_eligible()]

    @staticmethod
    def get_handler_for_event(topic, event_type):
        handlers = BaseHandler.event_listener.get(f"{topic}-*", [])
        handlers += BaseHandler.event_listener.get(f"{topic}-{event_type}", [])
        return [h for h in handlers if h.is_eligible()]

    @staticmethod
    def emit_event(topic, event_type, data):
        for handler in BaseHandler.get_handler_for_event(topic, event_type):
            handler.receive_event(topic, event_type, data)

    @staticmethod
    def set_state(state):
        BaseHandler.state = state

    @staticmethod
    def reset_state():
        BaseHandler.state = None

    def __init__(self):
        self.needs = []
        self.name = None

    def register_for_event(self, topic, event_type):
        key = topic
        if event_type is None:
            key += "-*"
        else:
            key += f"-{event_type}"
        if key not in BaseHandler.event_listener:
            BaseHandler.event_listener[key] = []
        BaseHandler.event_listener[key].append(self)

    def register_for_message(self, message_type):
        if message_type not in BaseHandler.message_listener:
            BaseHandler.message_listener[message_type] = []
        BaseHandler.message_listener[message_type].append(self)

    def is_eligible(self):
        is_eligible = True
        for need in self.needs:
            if not Config.get(f"robot_has_{need}"):
                is_eligible = False
                break
        return is_eligible


def register_handler(name, needs=[]):

    def wrapper(cls):
        o = cls()
        o.name = name
        o.needs = needs
        BaseHandler.handlers[name] = o
    return wrapper
