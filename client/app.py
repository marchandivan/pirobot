import traceback

from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread

import cv2
import numpy as np
import socket
import struct
import time
import threading

from gamepad import GamePad
from client import Client


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, host_ip):
        super().__init__()
        self.host_ip = host_ip

    def run(self):
        while True:
            try:
                # create socket
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                port = 8001
                client_socket.connect((self.host_ip, port))  # a tuple
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
            except KeyboardInterrupt:
                self.stop()
            except ConnectionRefusedError:
                print("Unable to connect to video server")
                time.sleep(1)
                continue
            except:
                traceback.print_exc()
                continue
            finally:
                client_socket.close()


class ImageLabel(QLabel):
    def mousePressEvent(self, event):
        print("clicked", event)
        cursor = QtGui.QCursor()
        print(event.pos())


class Button(QPushButton):
    def __init__(self, id, client, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clicked.connect(lambda: client.button_callback(id))


class App(QWidget):
    def __init__(self, hostname, full_screen=False):
        super().__init__()
        host_ip = socket.gethostbyname(hostname)

        self.client = Client(host_ip, self)

        self.setWindowTitle("PiCaterillar")
        self.resize(640, 480)
        if full_screen:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.showFullScreen()

        # create a vertical box layout and add the two labels
        vbox = QHBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)

        # create the label that holds the image
        self.image_label = ImageLabel(self)

#        vbox.addWidget(Button('light_toggle', self.client, 'Front Lights'))
        vbox.addWidget(self.image_label)
#        vbox.addWidget(Button('face_detection', self.client, 'Face Detection'))
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)

        # create the video capture thread
        self.thread = VideoThread(host_ip)
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

        # GamePad
        self.gamepad_thread = None
        self.start_gamepad()

    def start_gamepad(self):
        callback = {
            "joystick": self.client.gamepad_joystick_callback,
            "right_joystick":  self.client.gamepad_right_joystick_callback,
            "key": self.client.gamepad_key_callback
        }
        self.gamepad_thread = threading.Thread(target=GamePad.start_loop, kwargs=dict(callback=callback), daemon=True)
        self.gamepad_thread.start()

    def stop_gamepad(self):
        if self.gamepad_thread is not None:
            GamePad.stop_loop()
            self.gamepad_thread = None

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        rgb_image = cv2.resize(rgb_image, (self.size().width(), self.size().height()))
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(w, h, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def keyPressEvent(self, e):
        self.client.key_press_callback(e)
