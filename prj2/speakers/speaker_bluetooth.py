import json
import os
import logging
import bluetoothctl

import paho.mqtt.client as mqtt
from mqtt_callback_client import MQTTCallbackClient

import pygame
import socket

client = None
emotion = None
room = None

class Speaker():
    def __init__(self):#, client):
        #self.client = client
        self.playing = False
        self.Mac = "00:58:50:1D:B3:35"
        self.conn = bluetoothctl.Bluetoothctl()
        self.connected = False
        
        self.Rooms = {"Room1": "Kitchen",
                    "Room2": "Livingroom"}
        self.song = {"sad": 'Tammy-Stan-Devereaux.mp3', 
                    "happy": 'Pharrell-Williams-Happy-f7.mp3',
                    "angry": 'tbd',
                    "neutral": 'tbd'}
        pygame.mixer.init()
        pygame.mixer.music.load(self.song["happy"])  
        
    def loadMusic(self, file):
        pygame.mixer.music.load(file)

    def stopMusic(self,roomNr):
        if roomNr == 1:
            #Stop music on smart speaker
            pass
        elif roomNr == 2:
            pygame.mixer.music.stop()
        else:
            print("stopMusic: Unknown roomNr")

    def playMusic(self, emotion, roomNr):
        if roomNr == 1:
            print("Playing in room 1")
            self.stopMusic(roomNr=2)
            #play on smart speaker
        elif roomNr == 2:
            print("Playing in room 2")
            self.stopMusic(roomNr=1)
            pygame.mixer.music.play(loops=-1)  
        else:
            print("playMusic: Unknown roomNr")

    """ def connectToRoom(self, roomNr):
        if roomNr == 1:
            print("Connecting to Smart speaker")
            #Connect here
            print("Stop playing music from ",self.Mac)
            self.stopMusic()
        elif roomNr == 2:
            print("Playing from ",self.Mac)
            #self.conn.connect(self.Mac)
            print("Stop playing from Smart speaker")
        else:
            print("Invalid room Nr") """

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
        print("Room Calback for room: ",roomNr)
        if playing == True:
            #self.connectToRoom(roomNr)
            self.playMusic(emotion,roomNr)
        else:
            self.stopMusic(roomNr)

    #tænd og sluk begge rum
    def system_Callback(self, payload):
        global emotion
        if payload["audio_on"] == True:
            #Start smart speaker
            pygame.mixer.music.play(-1)
        elif payload["audio_on"] == False:
            self.stopMusic(1)
            self.stopMusic(2)


    def setupTopics(self,client):
        client.subscribe("pi_server/context/emotion", callback=self.emotion_callback,qos=1)
        client.subscribe("pi_server/context/room" + "1" + "/music_playing", callback=lambda payload: self.room_callback(payload, 1))
        client.subscribe("pi_server/context/room" + "2" + "/music_playing", callback=lambda payload: self.room_callback(payload, 2))
        client.subscribe("pi_server/context/system/audio", callback=self.system_Callback,qos=1)


def main():
    global client
    logging.basicConfig(
	    level=logging.INFO, format="%(asctime)s : %(levelname)s:  %(message)s"
	)
    #Setup mqtt
    pi_ip = socket.gethostbyname("rpi-server.local")
    #pi_ip = "192.168.143.239"   #server
    

    #Setup client
    client = MQTTCallbackClient(client_id="Kubuntu_sub2", userdata="DumDumReceiver")
    client.connect(pi_ip, 1883)  # rpi-server ip

    #Setup speaker
    spk = Speaker()
    spk.setupTopics(client)

    print("Ready to play \n")
     
    client.loop_forever()

if __name__ == "__main__":
	main()




