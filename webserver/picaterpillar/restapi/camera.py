import io
import math
import sys
import threading
import time
import traceback

import cv2
import numpy as np
from restapi.motor import Motor

# from restapi.models import Config
if sys.platform != "darwin":  # Mac OS
    import picamera


# Calculate model to covert the position of a pixel to the physical position on the floor,
# using measurements (distances & y_pos) & polynomial regression
H = 70
reference = dict(
    distances=[d / 100 for d in [15, 20, 30, 40, 50, 60, 68, 80, 90, 120, 150, 180]],
    y_pos=[100 - n for n in [100, 91.3, 79.2, 73.4, 69.9, 67.15, 65.6, 64.23, 62.86, 61.1, 59.9, 58.96]]
)
# Angle of the target
alpha = np.arctan([d / H for d in reference['distances']])
poly_coefficients = np.polyfit(reference['y_pos'], alpha, 3)
max_y_pos = 42

target = None
camera_semaphore = threading.Semaphore()


class CaptureDevice(object):
    target = None
    target_img = None
    catpures = []

    def __init__(self, resolution, framerate, capturing_device):
        self.capturing_device = capturing_device
        self.framerate = framerate
        self.frame_counter = 0
        if self.capturing_device == "usb":  # USB Camera?
            self.device = cv2.VideoCapture(0)
            self.res_x, self.res_y = resolution.split('x')
            self.res_x, self.res_y = int(self.res_x), int(self.res_y)
            self.device.set(3, self.res_x)
            self.device.set(4, self.res_y)
        else:
            self.device = picamera.PiCamera(resolution=resolution, framerate=framerate)

    def _add_target(self, frame):
        rect_size = 70
        center = [int((CaptureDevice.target[0] * self.res_x) / 100), int((CaptureDevice.target[1] * self.res_y) / 100)]
        if CaptureDevice.target_img is not None and self.frame_counter % 10 == 0:

            result = cv2.matchTemplate(frame, CaptureDevice.target_img, cv2.TM_CCORR_NORMED)
            # We want the minimum squared difference
            mn, mx, mnLoc, mxLoc = cv2.minMaxLoc(result)

            # Draw the rectangle:
            # Extract the coordinates of our best match
            if mx > 0.95:
                center = [mxLoc[0] + rect_size, mxLoc[1] + rect_size]
                CaptureDevice.target_img = frame[center[1] - rect_size:center[1] + rect_size, center[0] - rect_size:center[0] + rect_size]
        else:
            CaptureDevice.target_img = frame[center[1] - rect_size:center[1] + rect_size, center[0] - rect_size:center[0] + rect_size]



        CaptureDevice.target = [100 * center[0] / self.res_x, 100 * center[1] / self.res_y]


        cv2.rectangle(frame, [center[0] - 10, center[1] - 10], [center[0] + 10, center[1] + 10], (0, 0, 255), 2)

    def _add_lines(self, frame):
        color = (0, 255, 0)
        thickness = 2

        # Visor
        radius = 30
        y_offest = 30
        center_x = self.res_x // 2
        center_y = self.res_y // 2 + y_offest
        cv2.line(frame, (center_x, center_y + (radius + 10)), (center_x, center_y - (radius + 10)), color, thickness)
        cv2.line(frame, (center_x + (radius + 10), center_y), (center_x - (radius + 10), center_y), color, thickness)
        cv2.circle(frame, (center_x, center_y), radius, color, thickness)

        # Path
        path_bottom = 100
        cv2.line(frame, (center_x, center_y), (path_bottom, self.res_y), color, thickness)
        cv2.line(frame, (center_x, center_y), (self.res_x - path_bottom, self.res_y), color, thickness)

    def _add_speed(self, frame):
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        color = (0, 255, 0)
        thickness = 2

        motor_status = Motor.serialize()

        # ODO
        _, text_h = cv2.getTextSize(text="ODO", fontFace=font, fontScale=fontScale, thickness=thickness)[0]
        cv2.putText(frame, f"ODO: {motor_status['abs_distance'] / 1000:.2f} m", (5, 5 + text_h), font, fontScale, color, thickness)

        # Left
        cv2.putText(frame, f"{motor_status['left']['speed_rpm']} RPM", (5, self.res_y - 15), font, fontScale, color, thickness)
        cv2.rectangle(frame, (5, self.res_y - 50), (5 + 40, self.res_y - 50 - 400), color, thickness)
        cv2.rectangle(frame, (5, self.res_y - 50 - 200), (5 + 40, self.res_y - 50 - 200 - int(motor_status['left']['duty'] * 2)), color, -1)

        # Right
        right_speed_str = f"{motor_status['right']['speed_rpm']} RPM"
        text_w, text_h = cv2.getTextSize(text=right_speed_str, fontFace=font, fontScale=fontScale, thickness=thickness)[0]
        cv2.putText(frame, right_speed_str, (self.res_x - text_w - 5, self.res_y - 15), font, fontScale, color, thickness)
        cv2.rectangle(frame, (self.res_x - 5, self.res_y - 50), (self.res_x - 5 - 40, self.res_y - 50 - 400), color, thickness)
        cv2.rectangle(frame, (self.res_x - 5, self.res_y - 50 - 200), (self.res_x - 5 - 40, self.res_y - 50 - 200 - int(motor_status['right']['duty'] * 2)), color, -1)

    def capture(self):
        if self.capturing_device == "usb":
            camera_semaphore.acquire()
            ret, frame = self.device.read()
            camera_semaphore.release()
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def capture_continuous(self, stream, format='jpeg'):
        if self.capturing_device == "usb":
            while True:
                camera_semaphore.acquire()
                ret, frame = self.device.read()
                camera_semaphore.release()
                self.frame_counter += 1

                #if CaptureDevice.target is not None:
                #    self._add_target(frame)

                self._add_lines(frame)
                self._add_speed(frame)

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

                yield cv2.imencode('.jpg', rgb)[1].tostring()
                time.sleep(1.0 // self.framerate)
        else:
            for frame in self.device.capture_continuous(stream,
                                                        format=format,
                                                        use_video_port=True):
                self.frame_counter += 1
                yield frame.getvalue()

    def close(self):
        if self.capturing_device == "usb":
            self.device.release()
        else:
            self.device.close()


class Camera(object):
    streaming = False
    capture_device = None

    @staticmethod
    def stream():
        config = {} # Config.get_config()
        if sys.platform == "darwin":
            capturing_device = "usb"
            resolution = '1280x720'
        else:
            capturing_device = config.get('capturing_device', 'usb')
            resolution = config.get('capturing_resolution', '1280x720')
        Camera.capture_device = CaptureDevice(resolution=resolution,
                                              framerate=int(config.get('capturing_framerate', 5)),
                                              capturing_device=capturing_device)
        stream = io.BytesIO()
        try:
            Camera.streaming = True
            for frame in Camera.capture_device.capture_continuous(stream, format='jpeg'):
                stream.truncate()
                stream.seek(0)
                yield "--FRAME\r\n"
                yield "Content-Type: image/jpeg\r\n"
                yield "Content-Length: %i\r\n" % len(frame)
                yield "\r\n"
                yield frame
                yield "\r\n"
        except Exception as e:
            traceback.print_exc()
        finally:
            Camera.capture_device.close()
            Camera.streaming = False
            Camera.capture_device = None

    @staticmethod
    def select_target(x, y):
        CaptureDevice.target = [x, y]

    @staticmethod
    def get_target_position(x, y):
        # Distance on y axis
        a = 0
        for n, p in enumerate(reversed(poly_coefficients)):
            a += p * math.pow(min(max_y_pos, (100 - y)), n)
        y_pos = H * math.tan(a)

        return 0, y_pos

    @staticmethod
    def capture_image(resolution="1280x720"):
        if Camera.capture_device is not None:
            return Camera.capture_device.capture()
        else:
            capture_device = CaptureDevice(resolution=resolution,
                                           framerate=5,
                                           capturing_device="usb")
            image = capture_device.capture()
            capture_device.close()
            return image



    @staticmethod
    def serialize():
        return {
            'streaming': Camera.streaming
        }
