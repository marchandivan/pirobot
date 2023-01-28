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
                continue

    @staticmethod
    def stop_loop():
        GamePad.running = False

    def __init__(self, device):
        self.device = device
        self.x_pos = 0
        self.y_pos = 0
        self.rx_pos = 0
        self.ry_pos = 0

    def _update_position(self, event, axis):
        absinfo = self.device.absinfo(event.code)
        value_normalized = float(event.value - absinfo.min) / float(absinfo.max - absinfo.min)
        position = int(-100 + (value_normalized * 200))
        position = min(100, position)
        position = max(-100, position)

        if axis == "y":
            self.y_pos = position
        elif axis == "x":
            self.x_pos = position
        elif axis == "ry":
            self.ry_pos = position
        elif axis == "rx":
            self.rx_pos = position

    def loop(self, callback):
        for event in self.device.read_loop():
            if not GamePad.running:
                break
            if event.type == ecodes.EV_ABS:
                if event.code == ecodes.ABS_Y:
                    self._update_position(event, "y")
                    callback["joystick"](self.x_pos, self.y_pos)
                if event.code == ecodes.ABS_X:
                    self._update_position(event, "x")
                    callback["joystick"](self.x_pos, self.y_pos)
                if event.code == ecodes.ABS_RY:
                    self._update_position(event, "ry")
                    callback["right_joystick"](self.rx_pos, self.ry_pos)
                if event.code == ecodes.ABS_RX:
                    self._update_position(event, "rx")
                    callback["right_joystick"](self.rx_pos, self.ry_pos)
            elif event.type == ecodes.EV_KEY:
                if event.value == 1:
                    callback["key"](event.code)
