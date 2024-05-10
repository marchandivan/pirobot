from dataclasses import asdict
from enum import Enum
import logging
import nmcli
import time

from models import Config


logger = logging.getLogger(__name__)


class WifiStatus(Enum):
    connected = "connected"
    disconnected = "disconnected"
    device_not_found = "device_not_found"


class Wifi:
    WIFI_CONNECTION_TIMEOUT = 10

    @staticmethod
    def setup():
        device = Wifi.get_device()
        if device is not None:
            start_time = time.time()
            while device.state != "connected" and time.time() - start_time < Wifi.WIFI_CONNECTION_TIMEOUT:
                logger.info("Waiting for wifi connection...")
                time.sleep(1)
                device = Wifi.get_device()

            if device.state == "connected":
                logger.info(f"Successfully connected to wifi network '{device.connection}'")
            else:
                # If wifi is not connected, start wifi hotspot
                Wifi.start_hotspot()
        else:
            logger.warning(f"Unable to find wifi device {Config.get('wifi_device')}")

    @staticmethod
    def get_device() -> nmcli.device:
        wifi_device = Config.get("wifi_device")
        for device in nmcli.device():
            if device.device == wifi_device:
                return device
        return None

    @staticmethod
    def start_hotspot():
        hotspot_ssid = Config.get("hotspot_ssid")
        logger.info(f"Starting wifi hotspot '{hotspot_ssid}'")
        nmcli.device.wifi_hotspot(
            ifname=Config.get("wifi_device"),
            ssid=hotspot_ssid,
            password=Config.get("hotspot_password"),
        )

    @staticmethod
    def start_wifi():
        nmcli.radio.wifi_off()
        nmcli.radio.wifi_on()

    @staticmethod
    def get_networks():
        saved_networks = {n.name for n in nmcli.connection()}
        wifi_device = Config.get("wifi_device")
        networks = []
        for network in nmcli.device.wifi(ifname=wifi_device):
            network_dict = asdict(network)
            network_dict["saved"] = network.ssid in saved_networks
            networks.append(network_dict)
        return networks

    @staticmethod
    def connect_to_network(ssid, password):
        wifi_device = Config.get("wifi_device")
        if password is None:
            nmcli.connection._syscmd.nmcli(["connection", "up", ssid, "ifname", wifi_device])
        else:
            nmcli.device.wifi_connect(ssid=ssid, password=password, ifname=wifi_device)

    @staticmethod
    def forget_network(ssid):
        nmcli.connection.delete(ssid)

    @staticmethod
    def get_status():
        device = Wifi.get_device()
        if device is not None and device.connection is not None:
            hotspot = device.connection.lower() == "hotspot"
            if hotspot:
                signal = 100
            else:
                wifi_network = {n.ssid: n for n in nmcli.device.wifi(ifname=device.device)}.get(device.connection)
                if wifi_network is not None:
                    signal = wifi_network.signal
                else:
                    signal = 0
            return dict(
                state=device.state,
                connection=device.connection,
                hotspot=hotspot,
                signal=signal,
            )
        else:
            return dict(state="device_not_found", connection=None, hotspot=False, signal=0)
