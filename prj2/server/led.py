#!/usr/bin/env python3

from topics import *
from datetime import datetime
import blinkt
from colorsys import hsv_to_rgb
import logging

class LedStrip():
    def __init__(self, client, topic):
        self.client = client
        self.colors = {"sad": 300, "angry":360, "happy":120, "neutral":60}
        self.topic = topic
        self.brightness = 100

    def on(self):
        self.client.publish(self.topic + "/set", self.emotion)
        self.set_brigtness(self.brightness)

    def update_emotion(self, emotion):
        self.emotion = '{"color": {"hue": %d, "saturation": 100}}'%self.colors[emotion]
        self.on()

    def set_brigtness(self, value):
        self.brightness = value
        payload = '{"brightness": %d}'%self.brightness
        self.client.publish(self.topic + "/set", payload)
        

    def off(self):
        self.client.publish(self.topic + "/set", '{"state": "OFF"}')

class LedBlinkt():
    def __init__(self):
        self.colors = {"sad": 300, "angry":360, "happy":120, "neutral":60}
        self.hue = 0

    def on(self):
        self.off()

        for i in range(8):
            r, g, b = [int(c * 255) for c in hsv_to_rgb(self.hue/360, 1.0, 1.0)]
            blinkt.set_pixel(i, r, g, b)

        blinkt.show()
    
    def update_emotion(self, emotion):
        self.hue = self.colors[emotion]
        self.on()

        
    def set_brigtness(self, value):
        self.brightness = value
        blinkt.set_brightness(self.brightness/254)
        self.on()

    def off(self):
        blinkt.clear()
        blinkt.show()


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

    logging.info(f"led_room_control: room_nbr = {room_nbr}")

    if payload["occupied"]:
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
    brightness = 127

    time = datetime.datetime.strptime(payload["datetime"])

    if time.hour < 12:
        brightness += 127 - (time.hour * (127/12))
    
    if time.hour > 12:
        brightness += ((time.hour - 12) * (127/12))

    led1.set_brightness(brightness)
    led2.set_brightness(brightness)

def led_voice_control(payload):
    global led1
    global led2

    if payload['on']:
        led1.on()
        led2.on()
    else:
        led1.off()
        led2.off()


def setup_leds(client):
    global led1
    global led2

    led1 = LedBlinkt()
    led2 = LedStrip(client, led_topic + room2)

    client.subscribe(datetime_context,      callback=led_brightness_control)
    client.subscribe(room_context + "1",    callback=lambda payload: led_room_control(payload, 1))
    client.subscribe(room_context + "2",    callback=lambda payload: led_room_control(payload, 2))
    client.subscribe(emotion_context,       callback=led_new_emotion)
    client.subscribe(voice_context,         callback=lambda payload: led_voice_control(payload))
