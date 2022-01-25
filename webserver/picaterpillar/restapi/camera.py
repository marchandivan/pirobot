import io
import sys
import time
import traceback

# from restapi.models import Config

import cv2
if sys.platform != "darwin":  # Mac OS
    import picamera


class CaptureDevice(object):

    def __init__(self, resolution, framerate, capturing_device):
        self.capturing_device = capturing_device
        self.framerate = framerate
        if self.capturing_device == "usb":  # USB Camera?
            self.device = cv2.VideoCapture(0)
            self.res_x, self.res_y = resolution.split('x')
            self.res_x, self.res_y = int(self.res_x), int(self.res_y)
            self.device.set(3, self.res_x)
            self.device.set(4, self.res_y)
        else:
            self.device = picamera.PiCamera(resolution=resolution, framerate=framerate)

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

    def capture_continuous(self, stream, format='jpeg'):
        if self.capturing_device == "usb":
            while True:
                ret, frame = self.device.read()
                self._add_lines(frame)

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

                yield cv2.imencode('.jpg', rgb)[1].tostring()
                time.sleep(1.0 // self.framerate)
        else:
            for frame in self.device.capture_continuous(stream,
                                                        format=format,
                                                        use_video_port=True):
                yield frame.getvalue()

    def close(self):
        if self.capturing_device == "usb":
            self.device.release()
        else:
            self.device.close()


class Camera(object):
    streaming = False

    @staticmethod
    def stream():
        config = {} # Config.get_config()
        if sys.platform == "darwin":
            capturing_device = "usb"
            resolution = '1280x720'
        else:
            capturing_device = config.get('capturing_device', 'usb')
            resolution = config.get('capturing_resolution', '1280x720')
        capture_device = CaptureDevice(resolution=resolution,
                                       framerate=int(config.get('capturing_framerate', 5)),
                                       capturing_device=capturing_device)
        stream = io.BytesIO()
        try:
            Camera.streaming = True
            for frame in capture_device.capture_continuous(stream, format='jpeg'):
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
            capture_device.close()
            Camera.streaming = False

    @staticmethod
    def serialize():
        return {
            'streaming': Camera.streaming
        }
