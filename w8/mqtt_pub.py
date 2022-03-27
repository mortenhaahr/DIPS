#!/usr/bin/env python3
from paho.mqtt import client as mqtt
import time

def main():
    i = 0
    while True:
        client = mqtt.Client(client_id="Kubuntu_pub", userdata="DumDumProvider")
        client.connect("localhost", 1883)
        msg = client.publish(topic="test_topic/dumdum/i_am_dum_dum", payload=f'{{message: {i}}}', qos=0)
        print(f"""
        Printed msg with payload:   {i}
        Status:                     {msg.rc}
        Msg ID:                     {msg.mid}
        IsPublished:                {msg.is_published()}""")
        client.disconnect()
        i += 1
        time.sleep(1)

if __name__ == "__main__":
    main()