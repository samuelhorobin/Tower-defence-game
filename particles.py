import pygame
import random
import settings
import numpy as np
import math


class VFX_Manager:
    rectParticles = pygame.sprite.Group()

    @staticmethod
    def add(particle):
        if isinstance(particle, Rectparticle):
            VFX_Manager.rectParticles.add(particle)
            #print(len(VFX_Manager.rectParticles))

    @staticmethod
    def update():
        VFX_Manager.update_rectparticle()

    @staticmethod
    def update_rectparticle():
        for rp in VFX_Manager.rectParticles:
            rp.time += 1
            if rp.time >= rp.lifespan:
                rp.kill()

            if not rp.settled:
                if rp.rect.bottom > rp.floor:
                    rp.vector.y = 0
                    rp.yGrav = 0
                    rp.rect.bottom = rp.floor

                rp.rect.move_ip(rp.vector)

                rp.vector.x *= (1 - rp.xRes)
                if abs(rp.vector.x) < 0.5:
                    rp.vector.x = 0

                if rp.vector.x == 0 and rp.vector.y == 0:
                    rp.settled == True

                rp.vector.y += rp.yGrav
        



class Rectparticle(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos

        self.width = self.height = random.randint(1, 2) * 5
        self.rgb = (random.randint(150, 200), 61, 61)

        self.lifespanB = 2  # Base
        self.lifespanV = random.uniform(-1, 1)  # Variance

        self.angle = random.randint(0, 180)
        self.strength = random.randint(5, 10)

        self.xRes = 0.1
        self.yGrav = 1
        
        
    def load(self):
        self.time = 0
        self.settled = False

        self.vector = pygame.Vector2(self.strength, self.strength * -1)
        self.vector.rotate_ip(self.angle)

        self.lifespan = (self.lifespanB + self.lifespanV) * 60

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.rgb)
        self.rect = self.image.get_frect(topleft=self.pos)

        self.floor = self.rect.bottom + \
            random.randint(4, 11) * settings.UPSCALE


    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)


class ElixirParticle(Rectparticle):
    def __init__(self, pos):
        super().__init__(pos)
        self.width = self.height = random.randint(2, 3) * 5
        self.rgb = (66, random.randint(0, 70), 144)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.rgb)
        self.rect = self.image.get_frect(topleft=pos)

class FleshParticle(Rectparticle):
    def __init__(self, pos):
        super().__init__(pos)
        self.width = self.height = random.randint(3, 4) * 5
        self.rgb = (random.randint(125, 225), 40, 61)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.rgb)
        self.rect = self.image.get_frect(topleft=pos)
