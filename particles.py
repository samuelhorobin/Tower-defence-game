import pygame
import random
import settings
import numpy as np
import animations
import tools
import math
import cProfile

skullSpin = animations.skull()


for frame in range(len(skullSpin)):
    skullSpin[frame][0] = tools.extrapolateImage(skullSpin[frame][0], (0,0), rect = False)

class RectParticleCache:
    def __init__(self):
        self.cache = {}

    def get_cached_particle(self, *key):
        ''' Key format: width, colour'''
        if key in self.cache:
            return self.cache[key]
        else:
            image = self.create_particle(key)
            self.cache[key] = image
            return image

    def create_particle(self, key):
        width = height = key[0]
        rgb = key[1]

        image = pygame.Surface((width, height))
        image.fill(rgb)

        return image

class RectParticle_Manager:
    particles = pygame.sprite.Group()
    cache = RectParticleCache()

    @staticmethod
    def update(dt):
        for rp in RectParticle_Manager.particles:
            rp.time += dt
            if rp.time >= rp.lifespan:
                rp.kill()

            if not rp.settled:
                rp.vector.y += rp.yGrav
                rp.vector.x *= (1 - rp.xRes)
                if abs(rp.vector.x) < 0.5:
                    rp.vector.x = 0

                rp.rect.move_ip(rp.vector)

                if rp.rect.bottom > rp.floor:
                    rp.vector.y = 0
                    rp.yGrav = 0
                    rp.rect.bottom = rp.floor

                if rp.vector.x == 0 and rp.vector.y == 0:
                    rp.settled = True

class SkullParticle_Manager:
    particles = pygame.sprite.Group()

    @staticmethod
    def update(dt):
        for p in SkullParticle_Manager.particles:
            p.time += dt
            if p.time >= p.lifespan:
                p.kill()

            if not p.settled:
                if p.rect.bottom > p.floor:
                    SkullParticle_Manager.bounce(p)

                p.vector.y += p.yGrav
                p.rect.move_ip(p.vector)
        
                p.animationClock += dt * p.spinSpeed
                if p.animationClock > 0.05:
                    p.animationClock = 0
                    p.frame += 1
                    if p.frame == 8: p.frame = 0


    @staticmethod
    def bounce(p):
        if not p.settled:
            p.vector.y *= -0.5

            if p.vector.y < 0 and p.vector.y > -0.5:
                p.vector.y = 0
                p.settled = True

class Skull(pygame.sprite.Sprite):
    def __init__(self, sprite):
        super().__init__()
        self.frame = 0
        self.animationClock = 0
        self.time = 0
        self.lifespan = 5
        self.settled = False

        self.strength = abs(sprite.health) / 2

        self.spinSpeed = random.uniform(0.4, 1)
        self.xRes = 0.1
        self.yGrav = 1
        self.angle = random.randint(-10, 10)

        self.vector = pygame.Vector2(0, self.strength * -1)
        self.vector.rotate_ip(self.angle)

        self.animation = skullSpin
        self.rect = self.airRect = self.animation[0][0].get_frect(midtop=sprite.rect.midtop)
        
        self.floor = sprite.rect.bottom + random.randint(-1, 1) * settings.UPSCALE

    def draw(self, screen):
        screen.blit(self.animation[self.frame][0], self.airRect.topleft)

        

class Rectparticle(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos

        self.width = self.height = random.randint(1, 2) * 5
        self.rgb = (random.randint(150, 200), 61, 61)

        self.lifespanB = 2  # Base
        self.lifespanV = random.uniform(-1, 1)  # Variance

        self.angle = random.randint(10, 170)
        self.strength = random.randint(5, 10)

        self.xRes = 0.1
        self.yGrav = 1
        
        
    def load(self):
        self.time = 0
        self.settled = False

        self.vector = pygame.Vector2(self.strength, self.strength * -1)
        self.vector.rotate_ip(self.angle)

        self.lifespan = (self.lifespanB + self.lifespanV)

        self.image = RectParticle_Manager.cache.get_cached_particle(self.width, self.rgb)

        self.rect = self.image.get_frect(topleft=self.pos)

        self.floor = self.rect.bottom + random.randint(4, 11) * settings.UPSCALE


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

