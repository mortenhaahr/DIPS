import os
import logging

import paho.mqtt.client as mqtt
from mqtt_callback_client import MQTTCallbackClient

import pygame
import socket

from bluepy.btle import Peripheral

client = None

class Speaker():
    def __init__(self):#, client):
        #self.client = client
        self.playing = False
        self.Peripheral = Peripheral()
        self.Mac = "00:58:50:1D:B3:35"
        self.Rooms = {"Room1": "Kitchen",
                    "Room2": "Livingroom"}
        self.song = {"sad": 'Tammy-Stan-Devereaux.mp3', 
                    "happy": 'Pharrell-Williams-Happy-f7.mp3',
                    "angry": 'tbd',
                    "neutral": 'tbd'}
        pygame.mixer.init()


    #play sound
    def loadMusic(self, file):
        pygame.mixer.music.load(file)

    def connectToRoom(self, roomNr):
        if roomNr == 0:
            self.Peripheral.disconnect(self.Mac)
            print("Disconnecting from {0}",self.Mac)
        elif roomNr == 1:
            self.Peripheral.connect(self.Mac)
            print("Connecting to {0}",self.Mac)
        else:
            print("Invalid room Nr")

    def playMusic(self, emotion, roomNr):
        if self.song[emotion] == 'tbd':
            print('No song implemented yet \n')
        else:
            self.connectToRoom(roomNr)
            self.loadMusic(self.song[emotion])
            print('Playing sound "song": {0}, "room": {1}\n'.format(self.song[emotion], roomNr))
            payload = '{"playing": {"song": {0}, "room": {1}}}', self.song[emotion], roomNr
            #self.client.publish("zigbee2mqtt/audio/music", payload)
            pygame.mixer.music.play(loops=-1)  

    def updatePlayStatus(self):
        self.playing = pygame.mixer.music.get_busy()
        return self.playing
        
    
    def audio_callback(self, payload):
        global client

        emotion = payload['emotion']
        room = payload['room']
        self.playMusic(emotion,room)


def main():
    global client
    logging.basicConfig(
	    level=logging.INFO, format="%(asctime)s : %(levelname)s:  %(message)s"
	)
    #Setup mqtt
    #pi_ip = socket.gethostbyname("rpi-audio.local")
    pi_ip = "192.168.43.146"
    
    #client = MQTTCallbackClient(client_id="Kubuntu_sub", userdata="DumDumReceiver")
    #client.connect(pi_ip, 1883)  # rpi-server ip

    #client.subscribe("pi_server/audio", callback=spk.audio_callback)

    spk = Speaker()
    spk.playMusic(emotion="happy",roomNr=1)
    print("Volume is: ", pygame.mixer.music.get_volume(),"\n")

    while spk.updatePlayStatus() == True:
        continue

if __name__ == "__main__":
	main()




