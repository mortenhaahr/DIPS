#!/usr/bin/env python3
import logging
import json

from topics import *
import threading
from datetime import datetime
import geocoder

system_on = False

def update_room_context(payload, client, room_nbr):
	global system_on
	logging.debug(payload)

	try:
		if system_on:
			json_to_send = {
				"occupied": payload["occupancy"]
			}

			client.publish(room_context + room_nbr, json.dumps(json_to_send))
			update_time(client)

	except KeyError:
		logging.error("The key 'occupancy' was not in the JSON!")	


def update_emotion_callback(payload, client):
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

		to_send = {
			"emotion": emotion
		}

		client.publish(emotion_context, json.dumps(to_send))

		new_status = {"on": True}
		voice_context_callback(new_status, client)
		update_time(client)

		logging.info("Update Emotion callback, not implemented yet!")

	except ValueError:
		logging.error("Unknown emotion: " + emotion)

	except KeyError:
		logging.error("The key 'emotion' was not in the JSON!")

def update_time(client):
	# dd/mm/YY H:M:S
	client.publish(datetime_context, datetime.now().strftime('{"datetime": %d/%m/%Y %H:%M:%S }'))

def time_context_updater(client):
	update_time(client)
	threading.Timer(3600, lambda: time_context_updater(client)).start()

def position_context_updater(client):
	lat, lng = geocoder.ip('me').latlng	
	send = {
		"position": f"{lat},{lng}"
	}

	client.publish(position_context, json.dumps(send))
	update_time(client)
	threading.Timer(3600*24, lambda: position_context_updater(client)).start()


def voice_context_callback(payload, client):
	global system_on
	logging.debug(payload)

	try:
		system_on = payload["on"]

		to_send = {
			"on": system_on
		}
		client.publish(voice_context, json.dumps(to_send))
		update_time(client)

	except KeyError:
		logging.error("The key 'on' was not in the JSON!")	


def init_contexts(client):
	client.subscribe(voice_topic, 		callback=lambda payload: voice_context_callback(payload, client))
	client.subscribe(emotion_topic, 	callback=lambda payload: update_emotion_callback(payload, client))
	client.subscribe(pir_topic + room1, callback=lambda payload: update_room_context(payload, client, "1"))
	client.subscribe(pir_topic + room2, callback=lambda payload: update_room_context(payload, client, "2"))

	time_context_updater(client)
	position_context_updater(client)
