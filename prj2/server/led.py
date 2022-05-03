#!/usr/bin/env python3

from topics import *
from datetime import datetime
import blinkt
from colorsys import hsv_to_rgb
import logging

led_control = False

class LedStrip():
    def __init__(self, client, topic):
        self.client = client
        self.colors = {"sad": 300, "angry":360, "happy":120, "neutral":60}
        self.topic = topic
        self.brightness = 100
        self.emotion = None

    def on(self):
        global led_control
        if ((self.emotion != None) and led_control):
            self.client.publish(self.topic + "/set", self.emotion)
            self.set_brightness(self.brightness)
        else:
            self.off()

    def update_emotion(self, emotion):
        self.emotion = '{"color": {"hue": %d, "saturation": 100}}'%self.colors[emotion]
        self.on()

    def set_brightness(self, value):
        self.brightness = value
        payload = '{"brightness": %d}'%self.brightness
        self.client.publish(self.topic + "/set", payload)
        

    def off(self):
        self.client.publish(self.topic + "/set", '{"state": "OFF"}')

class LedBlinkt():
    def __init__(self):
        self.colors = {"sad": 300, "angry":360, "happy":120, "neutral":60}
        self.hue = None

    def on(self):
        self.off()

        global led_control

        if ((self.hue != None) and led_control):
            for i in range(8):
                r, g, b = [int(c * 255) for c in hsv_to_rgb(self.hue/360, 1.0, 1.0)]
                blinkt.set_pixel(i, r, g, b)

            blinkt.show()
    
    def update_emotion(self, emotion):
        self.hue = self.colors[emotion]
        self.on()

        
    def set_brightness(self, value):
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

    logging.debug(f"led_room_control: room_nbr = {room_nbr}")

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

    led_control = payload['on']

    if led_control:
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
    client.subscribe(room_context + "1" + occupied_context,    callback=lambda payload: led_room_control(payload, 1))
    client.subscribe(room_context + "2" + occupied_context,    callback=lambda payload: led_room_control(payload, 2))
    client.subscribe(emotion_context,       callback=led_new_emotion)
    client.subscribe(leds_context,        callback=led_system_control)
