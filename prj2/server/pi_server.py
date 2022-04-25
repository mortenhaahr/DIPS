#!/usr/bin/env python3
from glob import glob
import logging
import threading

from mqtt_callback_client import MQTTCallbackClient
from colorsys import hsv_to_rgb

import socket
import json

from .topics import *

client = None
emotion = None
system_on = False

def room_callback(payload, room_nbr):
	global client
	global system_on
	logging.debug(payload)

	try:
		if payload["occupancy"] and system_on:
			json_to_send = {
				"emotion": emotion,
				"room": room_nbr
			}

			client.publish(audio_topic, json.dumps(json_to_send))
	except KeyError:
		logging.error("The key 'occupancy' was not in the JSON!")	

def voice_callback(payload):
	global system_on
	logging.info(payload)

	try:
		system_on = payload["on"]

	except KeyError:
		logging.error("The key 'on' was not in the JSON!")	


def emotion_callback(payload):
	global client
	global emotion
	global system_on
	logging.debug(payload)

	try:
		emotion = payload['emotion']

		if emotion == "happy":
			logging.info("Happy emotion")
		elif emotion == "sad":
			logging.info("Sad emotion")
		elif emotion == "angry":
			logging.info("Angry emotion")
		else:
			raise ValueError

		system_on = True
		room_callback({"occupancy": True},1)

	except ValueError:
		logging.error("Unknown emotion: " + emotion)

	except KeyError:
		logging.error("The key 'emotion' was not in the JSON!")


def main():
	global client
	logging.basicConfig(
	    level=logging.INFO, format="%(asctime)s : %(levelname)s:  %(message)s"
	)
	pi_ip = socket.gethostbyname("rpi-server.local")

	client = MQTTCallbackClient(client_id="Kubuntu_sub", userdata="DumDumReceiver")
	client.connect(pi_ip, 1883)  # rpi-server ip
	
	#All topics - use for extreme debugging
	#client.subscribe(base_topic + "#") 

	client.subscribe(emotion_topic, 	callback=emotion_callback)
	client.subscribe(room1_topic, 	callback=lambda payload: room_callback(payload, 1))
	client.subscribe(room2_topic, 	callback=lambda payload: room_callback(payload, 2))
	client.subscribe(voice_topic, 	callback=voice_callback)

	client.loop_forever()

if __name__ == "__main__":
	main()
