#!/usr/bin/env python3
import logging
import threading
from mqtt_callback_client import MQTTCallbackClient
from colorsys import hsv_to_rgb

import socket


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s : %(levelname)s:  %(message)s"
    )
    client = MQTTCallbackClient(client_id="Kubuntu_sub", userdata="DumDumReceiver")
    client.connect("192.168.0.106", 1883)  # Mortens laptop IP
    client.subscribe("mortens_sick_bee/#")
    client.subscribe("mortens_sick_bee/pir_sensor", callback=led_callback)
    client.loop_forever()


if __name__ == "__main__":
	print(socket.gethostbyname(socket.gethostname()))
	main()
