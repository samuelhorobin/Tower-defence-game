import pygame
import random
import settings
import numpy as np

class Rectparticle(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.width = self.height = random.randint(1, 2) * 5
        self.rgb = (random.randint(150, 200), 61, 61)
        self.rect = pygame.FRect(pos, (self.width, self.height))

        self.lifespan = 2 + random.uniform(-1, 1) # s
        self.time = 0

        self.angle = random.randint(0, 180)
        self.strength = random.randint(5,10)
        self.xComp = np.cos(self.angle) * self.strength
        self.yComp = np.sin(self.angle) * self.strength * -1

        self.xRes = 0.1
        self.yGrav = 1

        self.floor = self.rect.bottom + random.randint(4, 11) * settings.UPSCALE
    
    def update(self, screen):
        self.time += 1/60
        if self.time >= self.lifespan:
            self.kill()

        if self.rect.bottom > self.floor:
            self.yComp = 0
            self.yGrav = 0
            self.rect.bottom = self.floor

        self.rect.x += self.xComp
        self.rect.y += self.yComp

        self.xComp *= (1 - self.xRes)
        if abs(self.xComp) < 0.5: self.xComp = 0
        self.yComp += self.yGrav

        pygame.draw.rect(screen, self.rgb, self.rect)

class ElixirParticle(Rectparticle):
    def __init__(self, pos):
        super().__init__(pos)
        self.width = self.height = random.randint(2, 3) * 5
        self.rgb = (66, random.randint(0, 70), 144)
        self.rect = pygame.FRect(pos, (self.width, self.height))
        

        