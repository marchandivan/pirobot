import sys

from camera import Camera
from sfx import SFX
from light import Light
from models import Config
from motor.motor import Motor
from prettytable import PrettyTable
from server import Server
from terminal import Terminal
from uart import UART

import argparse
import asyncio
import json
import platform
import pyttsx3
import socket
import struct
import traceback

if platform.machine() == "aarch64":  # Mac OS
    from lcd.LCD_2inch import LCD_2inch
else:
    from lcd.LCD_Mock import LCD_2inch


async def handle_video_client(reader, writer):
    Camera.start_continuous_capture()
    while True:
        frame = await Camera.next_frame()
        writer.write(struct.pack("Q", len(frame)) + frame)
        await writer.drain()


async def run_video_server():
    server_video = await asyncio.start_server(
        handle_video_client, port=8001, reuse_address=True, family=socket.AF_INET, flags=socket.SOCK_STREAM
    )

    async with server_video:
        await server_video.serve_forever()


class ServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))

    def data_received(self, data):
        message = data.decode()
        while len(message) > 0:
            pos = message.find("\n")
            if pos > 0:
                m = message[:pos]
                message = message[pos + 1:]
                m = json.loads(m)
                if "type" in m:
                    try:
                        Server.process(m)
                    except:
                        traceback.print_exc()
            else:
                break

    def connection_lost(self, exc):
        print('The client closed the connection')
        Server.connection_lost()


async def run_server():
    loop = asyncio.get_running_loop()
    server_socket = await loop.create_server(
        lambda: ServerProtocol(), port=8000, reuse_address=True, family=socket.AF_INET, flags=socket.SOCK_STREAM
    )

    async with server_socket:
        await server_socket.serve_forever()


async def start_server():
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

    # Open UART Port
    await UART.open()

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

    try:
        # Start video streaming
        await asyncio.gather(run_video_server(), run_server(), return_exceptions=True)
    except KeyboardInterrupt:
        print("Stopping...")
        sys.exit(0)


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
        asyncio.run(start_server())
    elif args.command == "configuration":
        if args.action == "update" and not args.value:
            print(f"Missing value for update")
            parser.print_usage()
        elif args.action == "delete" and not args.key:
            print(f"Missing key for delete")
            parser.print_usage()
        else:
            configure(args.action, args.key, args.value)