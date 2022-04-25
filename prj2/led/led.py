#!/usr/bin/env python3
import paho.mqtt.client as mqtt

class Led():
    def __init__(self, client):
        self.client = client
        self.colors = {"sad": 300, "angry":360, "happy":120, "neutral":60}

    def set_emotion(self, emotion):
        payload = '{"color": {"hue": %d, "saturation": 100}}'%self.colors[emotion]
        self.client.publish("zigbee2mqtt/led/set", payload)

    def set_brigtness(self, value):
        payload = '{"color": {"hue": %d, "saturation": 100}}'%self.colors[value]
        self.client.publish("zigbee2mqtt/led/set", payload)

    def off(self):
        self.client.publish("zigbee2mqtt/led/set", '{"state": "OFF"}')