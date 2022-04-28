import os
#from playsound import playsound

import pygame

#play sound
def loadMusic(file):
    pygame.mixer.music.load(file)

def playMusic(emotion):
    sad_file = 'Tammy-Stan-Devereaux.mp3'
    happy_file = 'Pharrell-Williams-Happy-f7.mp3'

    if emotion == "sad":
        loadMusic(sad_file)
    elif emotion == "happy":
        loadMusic(happy_file)

    print('Playing sound \n')
    pygame.mixer.music.play(loops=-1)    

def initMusic():
    pygame.mixer.init()

playMusic("happy")



print("Volume is: ", pygame.mixer.music.get_volume(),"\n")

while pygame.mixer.music.get_busy() == True:
    continue


