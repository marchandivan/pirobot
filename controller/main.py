from camera import Camera
from light import Light
from models import Config
from motor.motor import Motor
from server import Server
from terminal import Terminal

import argparse
import json
import platform
import pyttsx3
import socket
import struct
import threading
import traceback

if platform.machine() == "aarch64":  # Mac OS
    from lcd.LCD_2inch import LCD_2inch
else:
    from lcd.LCD_Mock import LCD_2inch


def stream_video():
    # Socket Create
    server_video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
                        Camera.start_continuous_capture()
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


def run_server():
    server_socket = socket.socket(socket.AF_INET)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(('', 8000))
    server_socket.listen(5)
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print('GOT CONNECTION FROM:', addr)
            if client_socket:
                message = ""
                while True:
                    try:
                        message += client_socket.recv(4096).decode()
                        pos = message.find("\n")
                        while pos > 0:
                            m = message[:pos]
                            message = message[pos+1:]
                            pos = message.find("\n")
                            m = json.loads(m)
                            if "type" in m:
                                Server.process(m)

                    except KeyboardInterrupt:
                        raise
                    except:
                        traceback.print_exc()
                        continue
    finally:
        server_socket.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start robot')
    parser.add_argument('-c', '--config', type=str, help='Config name or config file path', default='default')

    args = parser.parse_args()

    Config.setup(args.config)

    # Voice
    voice_engine = pyttsx3.init()

    # LCD & terminal Initialization
    RST = 24
    DC = 25
    BL = 23
    lcd = LCD_2inch(rst=RST, dc=DC, bl=BL)
    lcd.Init()
    lcd.clear()
    terminal = Terminal("Courier", lcd)
    terminal.header("PiRobot v1.0")
    terminal.text("Starting...")

    # Motor Initialization
    Motor.setup()
    terminal.text(f"Motor setup... {Motor.get_status()}")

    # Light
    if Config.get('robot_has_light'):
        Light.setup()
        terminal.text(f"Light setup... {Light.status}")

    # Motor Initialization
    Camera.setup()
    terminal.text(f"Camera setup.. {Camera.status}")

    terminal.text("Ready!")

    # Start video streaming
    threading.Thread(target=stream_video, daemon=True).start()

    # Start server
    threading.Thread(target=run_server, daemon=True).start()

    while True:
        try:
            pass
        except KeyboardInterrupt:
            print("Stopping...")
            break