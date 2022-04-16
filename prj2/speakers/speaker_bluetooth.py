import os
#from playsound import playsound

import pygame

pygame.mixer.init()

#play sound
file = 'Tammy-Stan-Devereaux.mp3'
pygame.mixer.music.load(file)

print('Playing sound \n')
pygame.mixer.music.play(loops=-1)

print("Volume is: ", pygame.mixer.music.get_volume(),"\n")

while pygame.mixer.music.get_busy() == True:
    continue


