from camera import Camera
from motor.motor import Motor

import json
import socket
import struct
import threading

Camera.setup()
Camera.start_continuous_capture()
Motor.setup()


def stream_video():
    # Socket Create
    server_video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Socket Bind
    server_video_socket.bind(('', 8001))

    # Socket Listen
    server_video_socket.listen(5)

    # Socket Accept
    try:
        while True:
            try:
                client_socket, addr = server_video_socket.accept()
                print('GOT CONNECTION FROM:', addr)
                if client_socket:
                    while True:
                        frame = Camera.get_last_frame()
                        if frame is not None:
                            message = struct.pack("Q", len(frame)) + frame
                            client_socket.sendall(message)
            except KeyboardInterrupt:
                break
            except:
                continue
    finally:
        server_video_socket.close()


if __name__=="__main__":
    # Start video streaming
    threading.Thread(target=stream_video, daemon=True).start()

    # Socket Create
    server_socket = socket.socket(socket.AF_INET)

    # Socket Bind
    server_socket.bind(('', 8000))

    # Socket Listen
    server_socket.listen(5)

    # Socket Accept
    try:
        while True:
            try:
                client_socket, addr = server_socket.accept()
                print('GOT CONNECTION FROM:', addr)
                if client_socket:
                    while True:
                        message = client_socket.recv(2048)
                        if message:
                            message = json.loads(message)
                            if message["type"] == "motor":
                                if message["action"] == "move":
                                    Motor.move(**message["args"])

            except KeyboardInterrupt:
                break
            except:
                continue
    finally:
        server_socket.close()
