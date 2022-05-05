#!/usr/bin/env python3
import logging
import json

from topics import *
import threading
from datetime import datetime
import geocoder

system_control = {
	"leds_on" : False,
	"audio_on": False
}

occupations = {
	"room1": False,
	"room2": False
}

def update_room_context(payload, client, room_nbr):
	global system_control
	global occupations
	logging.debug(payload)

	try:
		occupations["room" + room_nbr] = payload["occupancy"]
		client.publish(room_context + room_nbr + music_playing_context, json.dumps({
			"music_playing": (system_control["audio_on"] and occupations["room" + room_nbr])
			}))

		client.publish(room_context + room_nbr + occupied_context, json.dumps({
			"occupied": occupations["room" + room_nbr]
			}))
			
		update_time(client)

	except KeyError:
		logging.error("The key 'occupancy' was not in the JSON!")	


def update_emotion_callback(payload, client):
	logging.debug(payload)

	try:
		emotion = payload['emotion']

		to_send = {
			"emotion": emotion
		}

		client.publish(emotion_context, json.dumps(to_send))

		command_context_callback({
				"leds_on" : True,
				"audio_on": True
			}, client)

		update_time(client)

	except ValueError:
		logging.error("Unknown emotion: " + emotion)

	except KeyError:
		logging.error("The key 'emotion' was not in the JSON!")

def update_time(client):
	# dd/mm/YY H:M:S
	client.publish(datetime_context, datetime.now().strftime('{"datetime": "%d/%m/%Y %H:%M:%S" }'))

def time_context_updater(client):
	update_time(client)
	threading.Timer(3600, lambda: time_context_updater(client)).start()

def position_context_updater(client):
	try:
		lat, lng = geocoder.ip('me').latlng	
		send = {
			"position": f"{lat},{lng}"
		}

		client.publish(position_context, json.dumps(send))
		update_time(client)
	except TypeError: 
		logging.error("Failed to update the position context")
	finally:
		threading.Timer(3600*24, lambda: position_context_updater(client)).start()


def command_context_callback(payload, client):
	global system_control
	global occupations
	logging.debug(payload)

	try:
		system_control["leds_on"] = payload["leds_on"]
		client.publish(leds_context, json.dumps({"on": system_control["leds_on"]}))

	except KeyError:
		logging.debug("The key 'leds_on' was not in the JSON!")	

	try:
		system_control["audio_on"] = payload["audio_on"]
		client.publish(audio_context, json.dumps({"on": system_control["audio_on"]}))

		update_room_context(occupations["room1"], client, "1")
		update_room_context(occupations["room2"], client, "2")

	except KeyError:
		logging.debug("The key 'audio_on' was not in the JSON!")
	
	
	update_time(client)

def update_led_context(payload, client):
	logging.debug("Updating led context")
	try:
		client.publish(room_context + payload["room"] + lamp_context, json.dumps({
		"on": payload["on"]
		}))
	except KeyError:
		logging.error("Incorrect payload for update_led_context")


def init_contexts(client):
	client.subscribe(command_topic, 	callback=lambda payload: command_context_callback(payload, client))
	client.subscribe(emotion_topic, 	callback=lambda payload: update_emotion_callback(payload, client))
	client.subscribe(pir_topic + room1, callback=lambda payload: update_room_context(payload, client, "1"))
	client.subscribe(pir_topic + room2, callback=lambda payload: update_room_context(payload, client, "2"))
	client.subscribe(led_topic, 		callback=lambda payload: update_led_context(payload, client))

	time_context_updater(client)
	position_context_updater(client)
