import pygame
import settings
import animations
import tools
import particles

import random

from enum import Enum

cogWheelAnimations = animations.cogwheel()

for animation in cogWheelAnimations:
    for frame in range(len(animation)):
        animation[frame][0] = tools.extrapolateImage(
            animation[frame][0], (0, 0), rect=False)


class TowerAI(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.identifier = 0

        self.animation_clock = self.idle_frame = self.walkFrame = 0
        self.facing = "West"
        self.secondsPerFrame = 0.1
        self.health = 200

        self.idleE, self.idleW = cogWheelAnimations
        self.animation = self.idleE
        self.idle_frame_count = 6
        self.speed = 1

        self.image = self.idleE[0][0]
        self.rect = pygame.FRect((0, 0), (self.image.get_size()))
        self.hitbox = pygame.FRect(
            (0, 0), (16 * settings.UPSCALE, 16 * settings.UPSCALE))
        self.grid_pos = None

        self.state = "idle"

    def set_pos(self, coords, map):
        self.grid_pos = coords

        map.towerGrid[coords[1]][coords[0]] = self.identifier

        left = map.pos[0] + (coords[0] * 32 * settings.UPSCALE)
        top = map.pos[1] + (coords[1] * 16 * settings.UPSCALE)
        tileRect = pygame.Rect(
            (left, top), (32*settings.UPSCALE, 16*settings.UPSCALE))
        self.rect.midbottom = self.hitbox.midbottom = tileRect.midbottom

    def draw(self, screen):
        dt = 1/60
        self.animation_clock += dt * self.speed

        if self.state == "idle":
            screen.blit(self.animation[self.idle_frame][0], self.rect.topleft)

            if self.animation_clock >= self.secondsPerFrame:
                self.idle_frame += 1
                self.animation_clock = 0

                if self.idle_frame == self.idle_frame_count:
                    self.idle_frame = 0

    def damage(self, dmg, foreground):
        for i in range(dmg):
            foreground.add(particles.ElixirParticle(self.rect.center))
        self.health -= dmg
        if self.health <= 0:
            for _ in range(100):
                foreground.add(particles.ElixirParticle(self.rect.center))
            self.kill()


class CogWheel(TowerAI):
    def __init__(self):
        super().__init__()
        self.identifier = 1
        self.idleFrameCount = 6
        self.idleE, self.idleW = cogWheelAnimations

        self.attack_box = pygame.Rect(
            (0, 0), (8*settings.UPSCALE, 16*settings.UPSCALE))

    def draw(self, screen):
        self.dt = 1/60
        self.animation_clock += self.dt * self.speed

        if self.state == "idle":
            screen.blit(self.animation[self.idle_frame][0], self.rect.topleft)

            if self.animation_clock >= self.secondsPerFrame:
                self.idle_frame += 1
                self.animation_clock = 0

                if self.idle_frame == self.idleFrameCount:
                    self.idle_frame = 0

    def update(self, map, foreground):
        if self.idle_frame == 4 and self.animation_clock == 0 + self.dt * self.speed:
            self.attack(map, foreground)

    def attack(self, map, foreground):
        self.attack_box.midleft = self.hitbox.midright
        for enemy in map.enemies:
            if self.attack_box.colliderect(enemy.hitbox):
                enemy.damage(random.randint(75, 200), foreground, angle = -90)

        # pygame.draw.rect(screen, (255,250,50), self.attackBox)
