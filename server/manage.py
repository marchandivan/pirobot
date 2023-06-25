import argparse
import asyncio
import json
import logging
import socket
import struct
import sys

from camera import Camera
from logger import RobotLogger
from models import Config
from prettytable import PrettyTable
from server import Server


logger = logging.getLogger(__name__)


class VideoServerProtocol(asyncio.Protocol):

    def __init__(self):
        self.buffer = ""
        self.transport = None

    def send_new_frame(self, frame):
        if self.transport is not None:
            self.transport.write(struct.pack("Q", len(frame)) + frame)

    def connection_made(self, transport):
        self.transport = transport
        peername = transport.get_extra_info("peername")
        logger.info(f"Connection from {peername}")
        Camera.add_new_frame_callback(self.send_new_frame)
        Camera.start_continuous_capture(streaming=True)

    def connection_lost(self, exc):
        logger.info(f"The client closed the connection {exc}")
        Server.connection_lost()
        self.transport = None
        Camera.stop_streaming()


async def run_video_server():
    #server_video = await asyncio.start_server(
    #    handle_video_client, port=8001, reuse_address=True, family=socket.AF_INET, flags=socket.SOCK_STREAM
    #)
    loop = asyncio.get_running_loop()
    server_video = await loop.create_server(
        lambda: VideoServerProtocol(), port=8001, reuse_address=True, family=socket.AF_INET, flags=socket.SOCK_STREAM
    )

    async with server_video:
        await server_video.serve_forever()


class ServerProtocol(asyncio.Protocol):

    def __init__(self):
        self.buffer = ""

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        logger.info('Connection from {}'.format(peername))

    def data_received(self, data):
        self.buffer += data.decode()
        while len(self.buffer) > 0:
            pos = self.buffer.find("\n")
            if pos > 0:
                message = self.buffer[:pos]
                self.buffer = self.buffer[pos + 1:]
                RobotLogger.log_message("SOCKET", "R", message)
                try:
                    message = json.loads(message)
                    if "type" in message:
                        Server.process(message)
                except:
                    logger.error(f"Unable to process message {message}", exc_info=True)
            else:
                break

    def connection_lost(self, exc):
        logger.info(f"The client closed the connection {exc}")
        Server.connection_lost()


async def run_server():
    loop = asyncio.get_running_loop()
    server_socket = await loop.create_server(
        lambda: ServerProtocol(), port=8000, reuse_address=True, family=socket.AF_INET, flags=socket.SOCK_STREAM
    )

    async with server_socket:
        await server_socket.serve_forever()


async def start_server():
    # Setup server
    await Server.setup()

    try:
        # Start video streaming
        await asyncio.gather(run_video_server(), run_server(), return_exceptions=True)
    except KeyboardInterrupt:
        logger.info("Stopping...")
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