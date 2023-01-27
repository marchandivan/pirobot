from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread

import json
import cv2
import numpy as np
import socket
import struct
import threading

from gamepad import GamePad

#host_ip = socket.gethostbyname("picaterpillar.local")
host_ip = socket.gethostbyname("localhost")


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # create socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 8001
        client_socket.connect((host_ip, port))  # a tuple
        data = b""
        payload_size = struct.calcsize("Q")
        while True:
            while len(data) < payload_size:
                packet = client_socket.recv(4 * 1024)  # 4K
                if not packet: break
                data += packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += client_socket.recv(4 * 1024)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            frame = np.frombuffer(frame_data, dtype="byte")
            frame = cv2.imdecode(frame, cv2.IMREAD_UNCHANGED)
            self.change_pixmap_signal.emit(frame)

        client_socket.close()


class ImageLabel(QLabel):
    def mousePressEvent(self, event):
        print("clicked", event)
        cursor = QtGui.QCursor()
        print(event.pos())


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PiCaterillar")
        self.display_width = 640
        self.display_height = 480
        # create the label that holds the image
        self.image_label = ImageLabel(self)
        self.image_label.resize(self.display_width, self.display_height)

        # create a vertical box layout and add the two labels
        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)

        # Connect to server
        self.client_socket = None
        self.connect()

        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

        # GamePad
        self.gamepad_thread = None
        self.start_gamepad()

    def start_gamepad(self):
        callback = {
            "joystick": self.joystick_callback
        }
        self.gamepad_thread = threading.Thread(target=GamePad.start_loop, kwargs=dict(callback=callback), daemon=True)
        self.gamepad_thread.start()

    def stop_gamepad(self):
        if self.gamepad_thread is not None:
            GamePad.stop_loop()
            self.gamepad_thread = None

    def joystick_callback(self, x_pos, y_pos):
        if abs(x_pos) < 10 and abs(y_pos) < 10:
            self.send_message(dict(type="motor", action="stop"))
        else:
            left_speed = 100 * (x_pos - y_pos) / (abs(x_pos) + abs(y_pos))
            right_speed = 100 * (-x_pos - y_pos) / (abs(x_pos) + abs(y_pos))

            if left_speed < 0:
                left_orientation = 'B'
            else:
                left_orientation = 'F'

            if right_speed < 0:
                right_orientation = 'B'
            else:
                right_orientation = 'F'

            self.send_message(dict(type="motor", action="move", args=dict(left_orientation=left_orientation,
                                                                          left_speed=abs(left_speed),
                                                                          right_orientation=right_orientation,
                                                                          right_speed=abs(right_speed),
                                                                          duration=10,
                                                                          distance=None,
                                                                          rotation=None
                                                                          )))

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET)
        self.client_socket.connect((host_ip, 8000))

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def _resize(self, w, h):
        self.display_width = w
        self.display_height = h
        self.resize(self.display_width, self.display_height)
        self.image_label.resize(self.display_width, self.display_height)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        self._resize(w, h)
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def send_message(self, message):
        self.client_socket.sendall(json.dumps(message).encode() + b"\n")

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Up:
            self.send_message(dict(type="motor", action="move", args=dict(left_orientation='F',
                                                                          left_speed=100,
                                                                          right_orientation='F',
                                                                          right_speed=100,
                                                                          duration=0.5,
                                                                          distance=None,
                                                                          rotation=None
                                                                          )))
        elif e.key() == Qt.Key_Down:
            self.send_message(dict(type="motor", action="move", args=dict(left_orientation='B',
                                                                          left_speed=100,
                                                                          right_orientation='B',
                                                                          right_speed=100,
                                                                          duration=0.5,
                                                                          distance=None,
                                                                          rotation=None
                                                                          )))
        elif e.key() == Qt.Key_Right:
            self.send_message(dict(type="motor", action="move", args=dict(left_orientation='F',
                                                                          left_speed=100,
                                                                          right_orientation='B',
                                                                          right_speed=100,
                                                                          duration=0.5,
                                                                          distance=None,
                                                                          rotation=None
                                                                          )))
        elif e.key() == Qt.Key_Left:
            self.send_message(dict(type="motor", action="move", args=dict(left_orientation='B',
                                                                          left_speed=100,
                                                                          right_orientation='F',
                                                                          right_speed=100,
                                                                          duration=0.5,
                                                                          distance=None,
                                                                          rotation=None
                                                                          )))
