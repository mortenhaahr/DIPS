#!/usr/bin/env python3
import logging
import threading

from mqtt_callback_client import MQTTCallbackClient
from colorsys import hsv_to_rgb


client = None

def mood_callback(payload):
	global client
	print("I received a mood!")
	logging.info(payload)


def main():
	global client
	logging.basicConfig(
	    level=logging.INFO, format="%(asctime)s : %(levelname)s:  %(message)s"
	)
	client = MQTTCallbackClient(client_id="Kubuntu_sub", userdata="DumDumReceiver")
	client.connect("localhost", 1883)  # Mortens laptop IP
	client.subscribe("pi_server/#")
	client.subscribe("pi_server/mood_detector", callback=mood_callback)
	client.loop_forever()


if __name__ == "__main__":
	
	main()
