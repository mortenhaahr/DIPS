#!/usr/bin/env python3
from paho.mqtt import client as mqtt
import time

def on_message(client, userdata, msg):
    print(f"""
    Received message:
    Topic:              {msg.topic}
    Userdata:           {userdata}
    Payload:            {msg.payload}""")

def main():
    client = mqtt.Client(client_id="Kubuntu_sub", userdata="DumDumReceiver")
    client.on_message = on_message
    client.connect("localhost", 1883)
    client.subscribe("test_topic/#")
    client.loop_forever()

if __name__ == "__main__":
    main()