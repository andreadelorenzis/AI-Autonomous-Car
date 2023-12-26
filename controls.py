import pygame

class Controls:
    def __init__(self):
        self.forward = False
        self.backward = False
        self.right = False
        self.left = False

    def update(self, keys):
        self.left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        self.right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        self.forward = keys[pygame.K_UP] or keys[pygame.K_w]
        self.backward = keys[pygame.K_DOWN] or keys[pygame.K_s]