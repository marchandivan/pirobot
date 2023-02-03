import traceback

from evdev import InputDevice, categorize, ecodes, list_devices


class GamePad(object):
    gamepad = None
    running = False

    @staticmethod
    def get_available_devices():
        return [InputDevice(path) for path in list_devices()]

    @staticmethod
    def get_device(name=None):
        for device in GamePad.get_available_devices():
            if name is None or name == device.name:
                return device

        return None

    @staticmethod
    def start_loop(device_name=None, callback=dict()):
        GamePad.running = True
        while GamePad.running:
            try:
                device = GamePad.get_device(name=device_name)
                if device is not None:
                    print(f"Connected to {device.name}")
                    GamePad.gamepad = GamePad(device)
                    GamePad.gamepad.loop(callback=callback)
            except KeyboardInterrupt:
                raise
            except:
                traceback.print_exc()
                continue

    @staticmethod
    def stop_loop():
        GamePad.running = False

    def __init__(self, device):
        self.device = device
        self.absolute_axis_positions = {}

    def get_position(self, event):
        absinfo = self.device.absinfo(event.code)
        return dict(value=event.value, min=absinfo.min, max=absinfo.max)

    def loop(self, callback):
        for event in self.device.read_loop():
            if not GamePad.running:
                break
            if event.type == ecodes.EV_ABS:
                self.absolute_axis_positions[event.code] = self.get_position(event)
                callback["absolute_axis"](event.code, self.absolute_axis_positions)
            elif event.type == ecodes.EV_KEY:
                if event.value == 1:
                    callback["key"](event.code)
