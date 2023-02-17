from camera import Camera
from sfx import SFX
from light import Light
from models import Config
from motor.motor import Motor
from prettytable import PrettyTable
from server import Server
from terminal import Terminal

import argparse
import json
import platform
import pyttsx3
import socket
import struct
import time
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
                print('Get video connection:', addr)
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


def run_socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setblocking(True)
    server_socket.bind(('', 8000))
    server_socket.listen(5)

    client_sockets = set()
    try:
        while True:
            try:
                try:
                    client_socket, addr = server_socket.accept()
                    client_sockets.add(client_socket)
                except BlockingIOError:
                    pass
                for client_socket in client_sockets:
                    try:
                        message = client_socket.recv(4096).decode()
                        while len(message) > 0:
                            pos = message.find("\n")
                            while pos > 0:
                                m = message[:pos]
                                message = message[pos+1:]
                                pos = message.find("\n")
                                m = json.loads(m)
                                if "type" in m:
                                    Server.process(m)
                            message += client_socket.recv(4096).decode()

                    except socket.timeout as e:
                        print("No clients found")
                        continue
            except:
                traceback.print_exc()
                continue
    finally:
        server_socket.close()


def run_server():
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

    # SFX
    SFX.setup()

    # Setup server
    Server.setup(lcd)

    # Start video streaming
    threading.Thread(target=stream_video, daemon=True).start()

    # Start server
    threading.Thread(target=run_socket_server, daemon=True).start()

    while True:
        try:
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("Stopping...")
            break


def configure(action, key, value):
    table = PrettyTable()
    table.field_names = ["Key", "Type", "Value"]
    table.align = "l"
    full_config = Config.get_config()
    if action == "get":
        if key is not None:
            if key in full_config:
                key_config = full_config[key]
                table.add_row([key, key_config["type"], key_config["value"]])
        else:
            for k, key_config in full_config.items():
                table.add_row([k, key_config["type"], key_config["value"]])
        print(table)
    elif action == "update":
        if Config.save(key, value):
            print("Configuration successfully updated")
            table.add_row([key, full_config[key]["type"], value])
            print(table)
        else:
            print("Unable to update configuration")
    elif action == "delete":
        if Config.delete(key):
            print("Key successfully deleted")
            table.add_row([key, full_config[key]["type"], full_config[key]["default"]])
            print(table)
        else:
            print("Unable to delete configuration")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start robot')
    parser.add_argument('-c', '--config', type=str, help='Config name or config file path')
    subparsers = parser.add_subparsers(dest="command")

    # Run server parameters
    parser_runserver = subparsers.add_parser('runserver')
    parser_runserver.add_argument('-p', '--port', type=int, help='Port use by socket server', default=8000)

    # Configuration parameters
    parser_configure = subparsers.add_parser('configuration')
    parser_configure.add_argument('action', choices=["get", "update", "delete"])
    parser_configure.add_argument('key', type=str, nargs='?')
    parser_configure.add_argument('value', type=str, nargs='?')

    args = parser.parse_args()

    Config.setup(args.config)

    if args.command == "runserver":
        run_server()
    elif args.command == "configuration":
        if args.action == "update" and not args.value:
            print(f"Missing value for update")
            parser.print_usage()
        elif args.action == "delete" and not args.key:
            print(f"Missing key for delete")
            parser.print_usage()
        else:
            configure(args.action, args.key, args.value)