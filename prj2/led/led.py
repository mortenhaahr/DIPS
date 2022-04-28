#!/usr/bin/env python3
import paho.mqtt.client as mqtt
from topics import *

class Led():
    def __init__(self, client, topic):
        self.client = client
        self.colors = {"sad": 300, "angry":360, "happy":120, "neutral":60}
        self.topic = topic

    def set_emotion(self, emotion):
        payload = '{"color": {"hue": %d, "saturation": 100}}'%self.colors[emotion]
        self.client.publish(self.topic + "/set", payload)

    def set_brigtness(self, value):
        payload = '{"color": {"hue": %d, "saturation": 100}}'%self.colors[value]
        self.client.publish(self.topic + "/set", payload)

    def off(self):
        self.client.publish(self.topic + "/set", '{"state": "OFF"}')

def setup_leds(client):
    