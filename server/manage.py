import argparse
import asyncio
import logging
import sys

from models import Config
from prettytable import PrettyTable
from server import Server
from webserver.app import run_webserver


logger = logging.getLogger(__name__)


async def start_server():
    try:
        # Setup server
        server = Server()
        server.setup()

        # Start video streaming
        await run_webserver(server)
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
    parser.add_argument('-c', '--config', type=str, help='Robot config name or config file path')
    subparsers = parser.add_subparsers(dest="command")

    # Run server parameters
    parser_runserver = subparsers.add_parser('runserver')

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