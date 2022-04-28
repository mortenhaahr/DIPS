#!/usr/bin/env python3
from glob import glob
import logging
import threading
from datetime import datetime

from mqtt_callback_client import MQTTCallbackClient
from colorsys import hsv_to_rgb

import socket
import json
import geocoder

room 			= "_room"
room1		 	= room + "1"
room2 			= room + "2"

base_topic 		= "pi_server/"

emotion_topic 	= base_topic + "emotion"
voice_topic 	= base_topic + "voice"
pir_topic 		= base_topic + "pir"
led_topic 		= base_topic + "led"
audio_topic 	= base_topic + "audio"

context_topic  		= base_topic + "context/"
datetime_context 	= context_topic + "datetime"
emotion_context 	= context_topic + "emotion"
position_context 	= context_topic + "position"
room_context 		= context_topic + "room"
voice_context 		= context_topic + "voice"



client = None
emotion = None
system_on = False


def room_callback(payload, room_nbr):
	global client
	global system_on
	logging.debug(payload)

	try:
		if system_on:
			json_to_send = {
				"occupied": payload["occupancy"]
			}

			client.publish(room_context + room_nbr, json.dumps(json_to_send))

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


def time_updater():
	global client
	# dd/mm/YY H:M:S
	client.publish(datetime_context, datetime.now().strftime('{"datetime": %d/%m/%Y %H:%M:%S }'))
	threading.Timer(3600, time_updater).start()

def position_updater():
	global client_id

	lat, lng = geocoder.ip('me').latlng	
	send = {
		"position": f"{lat},{lng}"
	}

	client.publish(position_context, json.dumps(send))
	threading.Timer(3600*24, position_updater).start()

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
	client.subscribe(pir_topic + room1, callback=lambda payload: room_callback(payload, 1))
	client.subscribe(pir_topic + room2, callback=lambda payload: room_callback(payload, 2))
	client.subscribe(voice_topic, 	callback=voice_callback)

	time_updater()
	position_updater()

	client.loop_forever()

if __name__ == "__main__":
	main()
