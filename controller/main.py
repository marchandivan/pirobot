from camera import Camera
from motor.motor import Motor

import socket
import struct
import threading

Camera.setup()
Camera.start_continuous_capture()
Motor.setup()

# Socket Create
server_socket = socket.socket(socket.AF_INET)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)


def stream_video():
    # Socket Create
    server_video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Socket Bind
    server_video_socket.bind((host_ip, 8001))

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

    # Socket Bind
    server_socket.bind((host_ip, 8000))

    # Socket Listen
    server_socket.listen(5)

    # Socket Accept
    try:
        while True:
            try:
                client_socket, addr = server_socket.accept()
                print('GOT CONNECTION FROM:', addr)
                if client_socket:
                    message = client_socket.recv(2048)
                    Motor.move(
                        left_orientation='F',
                        left_speed=50,
                        right_orientation='F',
                        right_speed=50,
                        duration=5,
                        distance=None,
                        rotation=None
                    )

            except KeyboardInterrupt:
                break
            except:
                continue
    finally:
        server_socket.close()
