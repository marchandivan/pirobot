import math
import platform
import threading
import time
import traceback

import cv2
import numpy as np
from motor.motor import Motor
from servo.servo_handler import ServoHandler

from restapi.models import Config
if platform.machine() == "aarch":  # Mac OS
    import picamera
    from picamera.array import PiRGBArray
elif platform.machine() == "aarch64":
    import picamera2

# Calculate model to covert the position of a pixel to the physical position on the floor,
# using measurements (distances & y_pos) & polynomial regression
H = 70
MAX_DISTANCE = 1.8
ROBOT_WIDTH = 0.56  # in m

reference = dict(
    distances=[d / 100 for d in [15, 20, 30, 40, 50, 60, 68, 80, 90, 120, 150, 180]],
    y_pos=[100 - n for n in [100, 91.3, 79.2, 73.4, 69.9, 67.15, 65.6, 64.23, 62.86, 61.1, 59.9, 58.96]]
)
# Angle of the target
alpha = np.arctan([d / H for d in reference['distances']])
poly_coefficients = np.polyfit(reference['y_pos'], alpha, 3)
max_y_pos = 42

camera_lock = threading.Lock()

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
lower_body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_lowerbody.xml')


def get_camera_index():
    # checks the first 10 indexes.
    for index in [1, 0]:
        cap = cv2.VideoCapture(index)
        if cap.read()[0]:
            cap.release()
            return index
    return None


class CaptureDevice(object):
    target = None
    available_device = None

    def __init__(self, resolution, capturing_device, angle):
        self.capturing_device = capturing_device
        self.frame_counter = 0
        self.face = None
        self.res_x, self.res_y = resolution.split('x')
        self.res_x, self.res_y = int(self.res_x), int(self.res_y)
        self.angle = angle
        if self.capturing_device == "usb":  # USB Camera?
            self.device = cv2.VideoCapture(Camera.available_device)
            self.device.set(cv2.CAP_PROP_BUFFERSIZE, 2)
            self.device.set(3, self.res_x)
            self.device.set(4, self.res_y)
        else:
            if platform.machine() == "aarch64":
                self.device = picamera2.Picamera2()
                config = self.device.create_preview_configuration({"size": (self.res_x, self.res_y), "format": "RGB888"})
                print(config)
                self.device.configure(config)
                self.device.start()
            else:
                self.device = picamera.PiCamera(resolution=resolution)

    def add_overlay(self, frame, overlay_frame, pos, size):
        resized = cv2.resize(overlay_frame,
                             [int((size[0] * self.res_x) / 100), int((size[1] * self.res_y) / 100)],
                             interpolation=cv2.INTER_AREA)
        x_offset, y_offset = [int((pos[0] * self.res_x) / 100), int((pos[1] * self.res_y) / 100)]

        frame[y_offset:y_offset + resized.shape[0], x_offset:x_offset + resized.shape[1]] = resized

    def add_radar(self, frame, pos, size):
        motor_status = Motor.serialize()
        left_us_distance, front_us_distance, right_us_distance = motor_status.get('us_distances')
        radius = 0.15 * self.res_x

        color = (0, 255, 0)
        thickness = 2

        def add_circle(distance, angle):
            normalized_distance = radius * distance / 0.5
            if normalized_distance <= radius:
                cx = normalized_distance * math.sin(angle * math.pi / 180)
                cy = normalized_distance * math.cos(angle * math.pi / 180)
                x = int(cx + self.res_x // 2)
                y = int(self.res_y - cy)
                cv2.circle(frame, (x, y), radius=4, color=(0, 0, 255), thickness=2)

        cv2.circle(frame, (self.res_x // 2, self.res_y), radius=int(radius), color=(0, 255, 0), thickness=2)
        cv2.line(frame,
                 (self.res_x // 2, self.res_y),
                 (int(self.res_x // 2 - radius * math.sin(math.pi / 4)), int(self.res_y - radius * math.sin(math.pi / 4))),
                 color,
                 thickness)
        cv2.circle(frame, (self.res_x // 2, self.res_y), radius=int(2 * radius / 3), color=(0, 255, 0), thickness=2)
        cv2.line(frame,
                 (self.res_x // 2, self.res_y),
                 (self.res_x // 2, int(self.res_y - radius)),
                 color,
                 thickness)
        cv2.circle(frame, (self.res_x // 2, self.res_y), radius=int(radius / 3), color=(0, 255, 0), thickness=2)
        cv2.line(frame,
                 (self.res_x // 2, self.res_y),
                 (int(self.res_x // 2 + radius * math.sin(math.pi / 4)), int(self.res_y - radius * math.sin(math.pi / 4))),
                 color,
                 thickness)

        add_circle(left_us_distance, -45)
        add_circle(front_us_distance, 0)
        add_circle(right_us_distance, 45)

    def detect_face(self, frame):
        if self.frame_counter % 2 == 0:
            self.face = None
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            # Look for faces with 2 eyes or more
            for (x, y, w, h) in faces:
                size_percent = 100 * w / self.res_x
                if size_percent < 5 or size_percent > 40:
                    continue
                if self.face is None:
                    self.face = (x, y, w, h)
                roi_gray = gray[y:y + h, x:x + w]
                eyes = eye_cascade.detectMultiScale(roi_gray)
                if len(eyes) >= 2:  # At least 2 eyes :-) Third one could be the mouth
                    self.face = (x, y, w, h)
                    break

            if self.face is not None:
                x, y, w, h = self.face
                speed = 20
                timeout = 3
                x_pos = (x + w//2) * 100 / self.res_x
                y_pos = (y + h // 2) * 100 / self.res_y
                #Camera.set_position(y_pos)
                x_pos, y_pos = Camera.get_target_position(x_pos, y_pos)
                Motor.move_to_target(x_pos, y_pos, speed, timeout)

        if self.face is not None:
            x, y, w, h = self.face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)

    def add_navigation_lines(self, frame):
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

        # Speed and distance
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.8
        color = (0, 255, 0)

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

    def grab(self):
        if self.capturing_device == "usb":
            self.device.grab()

    def retrieve(self):
        self.frame_counter += 1
        if self.capturing_device == "usb":
            ret, frame = self.device.retrieve()
            return cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        else:  # picamera
            if platform.machine() == "aarch64":
                frame = self.device.capture_array()
                return cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
            else:
                output = PiRGBArray(self.device)
                self.device.capture(output, format="bgr", use_video_port=True)
                return cv2.cvtColor(output.array, cv2.COLOR_BGR2BGRA)
 
    def capture(self):
        max_retries = 3
        while max_retries > 0:
            max_retries -= 1
            try:
                if self.capturing_device == "usb":
                    camera_lock.acquire()
                    ret, frame = self.device.read()
                    camera_lock.release()
                    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                else:  # picamera
                    output = PiRGBArray(self.device)
                    self.device.capture(output, format="rgb")
                    return cv2.cvtColor(output.array, cv2.COLOR_BGRA2BGR)
            except:
                print ("Failed to capture image, retrying")
                traceback.print_exc()
                time.sleep(0.1)

    def capture_continuous(self, stream, format='jpeg'):
        if self.capturing_device == "usb":
            while True:
                camera_lock.acquire()
                ret, frame = self.device.read()
                camera_lock.release()
                self.frame_counter += 1

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

                yield cv2.imencode('.jpg', rgb)[1].tostring()
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
    status = "UK"
    streaming = False
    capturing = False
    capturing_thread = None
    overlay = True
    selected_camera = "front"
    face_detection = False
    front_capture_device = None
    arm_capture_device = None
    last_frame_lock = threading.Lock()
    last_frame = None
    servo_id = 1
    servo_center_position = 60
    servo_position = 0

    @staticmethod
    def setup():
        Camera.available_device = get_camera_index()
        Camera.center_position()
        if Config.get('front_capturing_device') == "usb" and Camera.available_device is None:
            Camera.status = "KO"
        else:
            Camera.status = "OK"

    @staticmethod
    def set_position(position):
        Camera.servo_position = int(position)
        ServoHandler.move(Camera.servo_id, 100 - Camera.servo_position)

    @staticmethod
    def center_position():
        Camera.set_position(Camera.servo_center_position)

    @staticmethod
    def stream():
        Camera.streaming = True
        Camera.start_continuous_capture()
        while Camera.streaming:
            try:
                Camera.last_frame_lock.acquire()
                last_frame = Camera.last_frame
                Camera.last_frame_lock.release()
                Camera.last_frame = None
                if last_frame is not None:
                    yield "--FRAME\r\n"
                    yield "Content-Type: image/jpeg\r\n"
                    yield "Content-Length: %i\r\n" % len(last_frame)
                    yield "\r\n"
                    yield last_frame
                    yield "\r\n"
            except:
                traceback.print_exc()
                if Camera.last_frame_lock.locked():
                    Camera.last_frame_lock.release()
                continue
        Camera.streaming = False

    @staticmethod
    def capture_continuous():
        front_capturing_device = Config.get('front_capturing_device')
        front_resolution = Config.get('front_capturing_resolution')
        front_angle = Config.get('front_capturing_angle')
        if platform.machine() not in ["aarch", "aarch64"]:
            arm_capturing_device = None
        else:
            arm_capturing_device = Config.get('back_capturing_device')
        arm_resolution = Config.get('back_capturing_resolution')
        arm_angle = Config.get('back_capturing_angle')

        Camera.front_capture_device = CaptureDevice(resolution=front_resolution,
                                                    capturing_device=front_capturing_device,
                                                    angle=front_angle)
        if arm_capturing_device is None:
            if platform.machine() not in ["aarch", "aarch64"] and Config.get('robot_has_back_camera'):
                Camera.arm_capture_device = Camera.front_capture_device
            else:
                Camera.arm_capture_device = None
        else:
            Camera.arm_capture_device = CaptureDevice(resolution=arm_resolution,
                                                      capturing_device=arm_capturing_device,
                                                      angle=arm_angle)

        framerate = Config.get('capturing_framerate')
        Camera.capturing = True
        frame_delay = 1.0 / framerate
        last_frame_ts = 0
        while Camera.capturing:
            try:
                Camera.front_capture_device.grab()
                if Camera.arm_capture_device is not None:
                    Camera.arm_capture_device.grab()

                if time.time() > last_frame_ts + frame_delay:
                    last_frame_ts = time.time()
                    if Camera.arm_capture_device is None or Camera.selected_camera == "front":
                        frame = Camera.front_capture_device.retrieve()
                        # Detect face
                        if Camera.face_detection:
                            Camera.front_capture_device.detect_face(frame)
                        # Navigation
                        Camera.front_capture_device.add_navigation_lines(frame)
                    else:
                        frame = Camera.arm_capture_device.retrieve()
                    Camera.front_capture_device.add_radar(frame, [50, 0], [25, 25])
                    if Camera.arm_capture_device is not None and Camera.overlay:
                        if Camera.selected_camera == "front":
                            overlay_frame = Camera.arm_capture_device.retrieve()
                            Camera.front_capture_device.add_overlay(frame, overlay_frame, [75, 0], [25, 25])
                        else:
                            overlay_frame = Camera.front_capture_device.retrieve()
                            Camera.arm_capture_device.add_overlay(frame, overlay_frame, [75, 0], [25, 25])

                    if Camera.streaming:
                        frame = cv2.imencode('.jpg', frame)[1].tostring()
                        Camera.last_frame_lock.acquire()
                        Camera.last_frame = frame
                        Camera.last_frame_lock.release()
            except Exception:
                traceback.print_exc()
                if Camera.last_frame_lock.locked():
                    Camera.last_frame_lock.release()
                continue
        Camera.front_capture_device.close()
        Camera.front_capture_device = None
        if Camera.arm_capture_device is not None:
            Camera.arm_capture_device.close()
            Camera.arm_capture_device = None
        Camera.capturing = False
        print("Stop Capture")

    @staticmethod
    def start_continuous_capture():
        print(Camera.capturing, Camera.capturing_thread)
        if not Camera.capturing or Camera.capturing_thread is None or not Camera.capturing_thread.is_alive():
            Camera.capturing = True
            print("Start capture")
            Camera.capturing_thread = threading.Thread(target=Camera.capture_continuous, daemon=True)
            Camera.capturing_thread.start()

    @staticmethod
    def stop_continuous_capture():
        if not Camera.streaming:
            Camera.capturing = False

    @staticmethod
    def stream_setup(selected_camera, overlay, face_detection):
        Camera.selected_camera = selected_camera
        Camera.overlay = overlay
        Camera.face_detection = face_detection
        if face_detection:
            Camera.start_continuous_capture()
            Camera.set_position(100)
        else:
            if Camera.streaming:
               Camera.stop_continuous_capture()
            Camera.center_position()

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

        x_pos = (MAX_DISTANCE / (MAX_DISTANCE - min(y_pos, MAX_DISTANCE - 0.1))) * ((x - 50) / 50) * ROBOT_WIDTH/2
        lense_coeff_x_pos = Config.get('lense_coeff_x_pos')
        return x_pos * lense_coeff_x_pos, y_pos

    @staticmethod
    def capture_image(camera):
        if camera == "front" and Camera.front_capture_device is not None:
            return Camera.front_capture_device.capture()
        elif camera == "arm" and Camera.arm_capture_device is not None:
            return Camera.arm_capture_device.capture()

    @staticmethod
    def serialize():
        return {
            'status': Camera.status,
            'streaming': Camera.streaming,
            'overlay': Camera.overlay,
            'face_detection': Camera.face_detection,
            'selected_camera': Camera.selected_camera,
            'position': Camera.servo_position,
            'center_position': Camera.servo_center_position
        }
