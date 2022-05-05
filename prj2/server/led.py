#!/usr/bin/env python3

from topics import *
from datetime import datetime
import blinkt
from colorsys import hsv_to_rgb
import logging
import json

led_control = False
led_occupancy = {
    "room1" : False,
    "room2" : False
}

class LedStrip():
    def __init__(self, client, topic):
        self.client = client
        self.colors = {"sad": 300, "angry":360, "happy":120, "neutral":60}
        self.topic = topic
        self.brightness = 100
        self.emotion = None

    def on(self):
        if (self.emotion != None):
            self.client.publish(self.topic + "/set", self.emotion)
        
            payload = '{"brightness": %d}'%self.brightness
            self.client.publish(self.topic + "/set", payload)
        
            self.client.publish(led_topic, json.dumps({"room": "2", "on": True}))

    def update_emotion(self, emotion):
        self.emotion = '{"color": {"hue": %d, "saturation": 100}}'%self.colors[emotion]

    def set_brightness(self, value):
        self.brightness = value

    def off(self):
        self.client.publish(self.topic + "/set", '{"state": "OFF"}')
        self.client.publish(led_topic, json.dumps({"room": "2", "on": False}))

class LedBlinkt():
    def __init__(self, client):
        self.colors = {"sad": 300, "angry":360, "happy":120, "neutral":60}
        self.hue = None
        self.brightness = 0
        self.client = client

    def on(self):

        if (self.hue != None):
            for i in range(8):
                r, g, b = [int(c * 255) for c in hsv_to_rgb(self.hue/360, 1.0, 1.0)]
                blinkt.set_pixel(i, r, g, b)

            blinkt.set_brightness(self.brightness/254)
            blinkt.show()
            self.client.publish(led_topic, json.dumps({"room": "1", "on": True}))
    
    def update_emotion(self, emotion):
        self.hue = self.colors[emotion]
        
    def set_brightness(self, value):
        self.brightness = value

    def off(self):
        blinkt.clear()
        blinkt.show()
        self.client.publish(led_topic, json.dumps({"room": "1", "on": False}))


led1 = None
led2 = None


def led_new_emotion(payload):
    global led1
    global led2
    led1.update_emotion(payload['emotion'])
    led2.update_emotion(payload['emotion'])


def led_room_control(payload, room_nbr):
    global led1
    global led2

    global led_occupancy


    logging.debug(f"led_room_control: room_nbr = {room_nbr}")
    global led_control

    led_occupancy['room' + room_nbr] = payload["occupied"];

    if led_occupancy['room' + room_nbr] and led_control:
        if room_nbr == 1:
            led1.on()

        elif room_nbr == 2:
            led2.on()
        
    else:
        if room_nbr == 1:
            led1.off()

        elif room_nbr == 2:
            led2.off()


def led_brightness_control(payload):
    global led1
    global led2
    brightness = 0

    curr_time = datetime.strptime(payload["datetime"], "%d/%m/%Y %H:%M:%S")

    if curr_time.hour < 12:
        brightness = 254 - (curr_time.hour * (254/12))
    
    if curr_time.hour >= 12:
        brightness = ((curr_time.hour - 12) * (254/12))

    logging.debug(f"brightness: {brightness}")

    led1.set_brightness(brightness)
    led2.set_brightness(brightness)

def led_system_control(payload):
    global led1
    global led2

    global led_control
    global led_occupancy

    led_control = payload['on']

    led_room_control(led_occupancy["room1"], 1);
    led_room_control(led_occupancy["room2"], 2);


def setup_leds(client):
    global led1
    global led2

    led1 = LedBlinkt(client)
    led2 = LedStrip(client, led_topic + room2)

    client.subscribe(datetime_context,      callback=led_brightness_control)
    client.subscribe(room_context + "1" + occupied_context,    callback=lambda payload: led_room_control(payload, 1))
    client.subscribe(room_context + "2" + occupied_context,    callback=lambda payload: led_room_control(payload, 2))
    client.subscribe(emotion_context,       callback=led_new_emotion)
    client.subscribe(leds_context,        callback=led_system_control)
