#!/usr/bin/env python3
import logging

from mqtt_callback_client import MQTTCallbackClient

import socket

from contexts import init_contexts
from led import setup_leds


def main():
	logging.basicConfig(
	    level=logging.INFO, format="%(asctime)s : %(levelname)s:  %(message)s"
	)
	pi_ip = socket.gethostbyname("rpi-server.local")

	client = MQTTCallbackClient(client_id="Kubuntu_sub", userdata="DumDumReceiver")
	client.connect(pi_ip, 1883)  # rpi-server ip
	
	#All topics - use for extreme debugging
	#client.subscribe(base_topic + "#") 

	init_contexts(client)
	setup_leds(client)

	client.loop_forever()

if __name__ == "__main__":
	main()
