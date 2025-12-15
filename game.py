import pygame
import time
import random

#setting display
WIDTH,HEIGHT= 1000,800
WIN= pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('bunnies beta V 1.0')

#defining gameplay loop
def main():
    run = True

    while run:
        for event in pygame.event.get():
            if event.type==






