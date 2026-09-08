from enum import nonmember

import pygame

win = None

def init():
    global win
    pygame.init()
    win = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Tello Keyboard Control")

def update():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

def getKey(keyName):
    key_input = pygame.key.get_pressed()
    key = getattr(pygame, f"K_{keyName}")
    return bool(key_input[key])
