#!/usr/bin/env python3
import logging
import threading
from mqtt_callback_client import MQTTCallbackClient
import blinkt
from colorsys import hsv_to_rgb

led_on = False

def led_blink():
    global led_on
    global timer
    if led_on:
        led_on = False
        blinkt.set_brightness(0.0)
    else:
        led_on = True
        blinkt.set_brightness(0.1)
    blinkt.show()
    timer = threading.Timer(1, led_blink)
    timer.start()

timer = threading.Timer(1, led_blink)

def led_callback(payload):
    global timer
    MAX_ILLUM = 1000 # Approximately
    SPACING = 45
    logging.info(payload)
    blinkt.clear()
    if payload["occupancy"]:
        for i in range(8):
            hue = (payload["illuminance"] + i * SPACING) % MAX_ILLUM # Add rainbow effect
            hue = hue / MAX_ILLUM # Between 0 and 1
            r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)] # Convert from hue to rgb
            blinkt.set_pixel(i, r, g, b)
        blinkt.show()
        if not timer.is_alive():
            timer.start()
    else:
        if timer.is_alive():
            timer.stop()
        blinkt.set_brightness(0.0)
        blinkt.show()

def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s : %(levelname)s:  %(message)s"
    )
    blinkt.set_brightness(0)
    client = MQTTCallbackClient(client_id="Kubuntu_sub", userdata="DumDumReceiver")
    client.connect("192.168.0.106", 1883)  # Mortens laptop IP
    client.subscribe("mortens_sick_bee/#")
    client.subscribe("mortens_sick_bee/pir_sensor", callback=led_callback)
    client.loop_forever()


if __name__ == "__main__":
    main()
