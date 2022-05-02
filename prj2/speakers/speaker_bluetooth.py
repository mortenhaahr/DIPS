import json
import os
import logging

import paho.mqtt.client as mqtt
from mqtt_callback_client import MQTTCallbackClient

import pygame
import socket

#from bluepy.btle import Peripheral

client = None
emotion = None
room = None

class Speaker():
    def __init__(self):#, client):
        #self.client = client
        self.playing = False
        #self.Peripheral = Peripheral()
        self.Mac = "00:58:50:1D:B3:35"
        self.Rooms = {"Room1": "Kitchen",
                    "Room2": "Livingroom"}
        self.song = {"sad": 'Tammy-Stan-Devereaux.mp3', 
                    "happy": 'Pharrell-Williams-Happy-f7.mp3',
                    "angry": 'tbd',
                    "neutral": 'tbd'}
        pygame.mixer.init()

    
        
    def loadMusic(self, file):
        pygame.mixer.music.load(file)

    def connectToRoom(self, roomNr):
        if roomNr == 0:
            print("Disconnecting from {0}",self.Mac)
            #self.Peripheral.disconnect()
            print("Disconnected")
        elif roomNr == 1:
            print("Connecting to {0}",self.Mac)
            #self.Peripheral.connect(self.Mac)
            print("Connected")
        else:
            print("Invalid room Nr")

    def playMusic(self, emotion, roomNr):
        
            #self.connectToRoom(roomNr)
            print('Playing sound "song": {0}, "room": {1}\n'.format(self.song[emotion], roomNr))
            #payload = '{"playing": {"song": {0}, "room": {1}}}', self.song[emotion], roomNr
            #self.client.publish("zigbee2mqtt/audio/music", payload)
            pygame.mixer.music.play(loops=-1)  

    def stopMusic(self):
        pygame.mixer.music.stop()

    def updatePlayStatus(self):
        self.playing = pygame.mixer.music.get_busy()
        return self.playing
        
    def emotion_callback(self, payload):
        global emotion
        emotion = payload['emotion']
        print("emotionCallback \n")
        if self.song[emotion] == 'tbd':
            print('No song implemented yet \n Loading happy \n')
            self.loadMusic(self.song['happy'])
        else:
            self.loadMusic(self.song[emotion])

    def room_callback(self, payload, roomNr):
        global emotion
        playing = payload['music_playing']
        if playing == True:
            self.connectToRoom(roomNr)
            self.playMusic(emotion,roomNr)
        else:
            self.stopMusic()

    def setupTopics(self,client):
        client.subscribe("pi_server/context/emotion", callback=self.emotion_callback)
        client.subscribe("pi_server/context/room" + "1", callback=lambda payload: self.room_callback(payload, 1))
        client.subscribe("pi_server/context/room" + "2", callback=lambda payload: self.room_callback(payload, 2))


def main():
    global client
    logging.basicConfig(
	    level=logging.INFO, format="%(asctime)s : %(levelname)s:  %(message)s"
	)
    #Setup mqtt
    pi_ip = socket.gethostbyname("rpi-server.local")
    #pi_ip = "192.168.43.146"
    #pi_ip = "192.168.143.44"    #pc
    

    #Setup client
    client = MQTTCallbackClient(client_id="Kubuntu_sub", userdata="DumDumReceiver")
    client.connect(pi_ip, 1883)  # rpi-server ip

    json_to_send = {
			"emotion": "happy"
		}
    client.publish("pi_server/context/emotion",json.dumps(json_to_send))


    #Setup speaker
    spk = Speaker()

    client.subscribe("pi_server/context/emotion", callback=spk.emotion_callback)


    spk.setupTopics(client)

    print("Ready to play \n")

    while True:
        continue

if __name__ == "__main__":
	main()




