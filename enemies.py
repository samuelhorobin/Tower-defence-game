
import pygame
import os
import random
import numpy as np

import particles
import animations
import tools
import settings

businessDwarfAnimations = animations.business_dwarf()

for animation in businessDwarfAnimations:
            for frame in range(len(animation)):
                animation[frame][0] = tools.extrapolateImage(animation[frame][0], (0,0), rect = False)


def logistic_function(x, L = 1, k = 10, x0 = 0.5, differentiated = False):
    ''' L = max val, k = growth rate, a = xVal of midpoint'''
    if differentiated == False:
        return L / (1 + np.exp(-k * (x - x0)))
    
    elif differentiated == True:
        return (L * k * np.exp(-k * (x - x0))) / (1 + np.exp(-k * (x - x0)))**2


class SpriteAI(pygame.sprite.Sprite):
    def __init__(self, speed = 1) -> None:
        super().__init__()

        rawImageDir = os.path.join("Tower-defence-game", "assets", "enemies", "enemy.png")
        rawImage = pygame.image.load(rawImageDir)
        self.image, self.rect = tools.extrapolateImage(rawImage, pos = (0,0), float = True)
        self.heightOffset = (8 * settings.UPSCALE) - self.image.get_height()

        self.spawnIter = 0
        self.spawned = False
        self.goals = pygame.sprite.Group()
        self.journey = []
        self.speed = speed
        self.movement = (0,0)

        self.accY = self.accX = 0 #Accumulated speeds for decimal movement

    def spawn(self, map, row):
        self.gridPos = [len(map.tileGrid[row]) - 1, row]

        posX = map.pos[0] + len(map.tileGrid[row]) * 32 * settings.UPSCALE
        posY = map.pos[1] + self.heightOffset + row * 16 * settings.UPSCALE

        self.rect.x, self.rect.y = posX, posY
        self.spawned = True

    def set_goal(self, map, column, row):
        self.gridJourney = map.NodeManager.navigate(self.gridPos, (column, row))
        self.journey = [(map.pos[0] + node[0] * 32 * settings.UPSCALE, map.pos[1] + node[1] * 16 * settings.UPSCALE) for node in self.gridJourney]

        nodeOffset = (160 - self.rect.width) // 2
        self.journey = [(node[0] + nodeOffset, node[1] + self.heightOffset) for node in self.journey]


    def move(self) -> None:
        self.goals.update()

        if self.spawnIter < 0.7 and self.spawned == True:
            deltaX = logistic_function(self.spawnIter, differentiated = True) * -1.2 * self.speed
            self.rect.move_ip(deltaX, 0)
            self.spawnIter += 0.01 * self.speed

        if self.spawnIter > 0.7 and len(self.journey) > 0:
            destX = self.journey[0][0]
            destY = self.journey[0][1]

            if destX - self.speed < int(self.rect.x) and destX + self.speed > int(self.rect.x): xBound = True
            else: xBound = False

            if destY - self.speed < int(self.rect.y) and destY + self.speed > int(self.rect.y): yBound = True
            else: yBound = False

            if yBound == True and xBound == True:
                self.movement = (0,0)

            if xBound and yBound:
                self.journey.pop(0)
                self.gridPos = self.gridJourney.pop(0)
                if len(self.journey) > 0:
                    destX = self.journey[0][0]
                    destY = self.journey[0][1]
                

            deltaX = deltaY = 0
            
            if destX - self.speed >= int(self.rect.x): deltaX = self.speed
            if destY - self.speed >= int(self.rect.y): deltaY = self.speed

            if destX + self.speed <= int(self.rect.x): deltaX = -self.speed
            if destY + self.speed <= int(self.rect.y): deltaY = -self.speed

            vector = pygame.math.Vector2(deltaX, deltaY)
            self.movement = (deltaX / self.speed, deltaY / self.speed)
            
            if abs(deltaX) > 0 and abs(deltaY) > 0:
                vector.scale_to_length(self.speed)

            self.rect.x += vector.x
            self.rect.y += vector.y

    def draw(self, screen):
        if self.spawned == True:
            screen.blit(self.image, self.rect.topleft)

    def update(self):
        self.move()
        self.draw()
            




class BusinessDwarf(SpriteAI):
    def __init__(self, Foreground, speed = 1):
        super().__init__(speed=speed)
        self.idleFrame = 0
        self.walkFrame = 0
        self.facing = "West"
        self.animationClock = 0
        self.secondsPerFrame = 0.2
        self.health = 700
        
        self.walkS, self.walkSW, self.walkW, self.walkNW, \
        self.walkN, self.walkNE, self.walkE, self.walkSE, \
        self.idleS, self.idleSE, self.idleE, self.idleNE, \
        self.idleN, self.idleNW, self.idleW, self.idleSW = businessDwarfAnimations

        self.image = self.idleS[0][0]
        self.rect = pygame.FRect((0,0), (self.image.get_size()))
        self.heightOffset -= 2 * settings.UPSCALE
        

    def update(self, map, screen, Foreground):
        self.move()
        self.draw(screen)

    def damage(self, dmg, Foreground):
        for i in range(dmg):
            Foreground.add(particles.Rectparticle(self.rect.center))
        self.health -= dmg
        if self.health <= 0:
            for i in range(100): Foreground.add(particles.Rectparticle(self.rect.center))
            self.kill()

    def draw(self, screen):
        dt = 1/60
        self.animationClock += dt * self.speed

        if self.movement == (0, 1):
            screen.blit(self.walkS[self.walkFrame][0], self.rect.topleft)
            self.facing = "South"
        if self.movement == (1, 1):
            screen.blit(self.walkSW[self.walkFrame][0], self.rect.topleft)
            self.facing = "South-East"
        if self.movement == (1, 0):
            screen.blit(self.walkW[self.walkFrame][0], self.rect.topleft)
            self.facing = "East"
        if self.movement == (1, -1):
            screen.blit(self.walkNW[self.walkFrame][0], self.rect.topleft)
            self.facing = "North-East"
        if self.movement == (0, -1):
            screen.blit(self.walkN[self.walkFrame][0], self.rect.topleft)
            self.facing = "North"
        if self.movement == (-1, -1):
            screen.blit(self.walkNE[self.walkFrame][0], self.rect.topleft)
            self.facing = "North-West"
        if self.movement == (-1, 0):
            screen.blit(self.walkE[self.walkFrame][0], self.rect.topleft)
            self.facing = "West"
        if self.movement == (-1, 1):
            screen.blit(self.walkSE[self.walkFrame][0], self.rect.topleft)
            self.facing = "South-West"

        if self.movement == (0,0):
            if self.facing == "South":
                screen.blit(self.idleS[self.idleFrame][0], self.rect.topleft)
            if self.facing == "South-East":
                screen.blit(self.idleSE[self.idleFrame][0], self.rect.topleft)
            if self.facing == "East":
                screen.blit(self.idleE[self.idleFrame][0], self.rect.topleft)
            if self.facing == "North-East":
                screen.blit(self.idleNE[self.idleFrame][0], self.rect.topleft)
            if self.facing == "North":
                screen.blit(self.idleN[self.idleFrame][0], self.rect.topleft)
            if self.facing == "North-West":
                screen.blit(self.idleNW[self.idleFrame][0], self.rect.topleft)
            if self.facing == "West":
                screen.blit(self.idleW[self.idleFrame][0], self.rect.topleft)
            if self.facing == "South-West":
                screen.blit(self.idleSW[self.idleFrame][0], self.rect.topleft)

        if self.movement != (0, 0) and self.animationClock >= self.secondsPerFrame:
            
            self.animationClock = 0
            self.walkFrame += 1
            if self.walkFrame == 4: self.walkFrame = 0

        elif self.movement == (0,0) and self.animationClock >= self.secondsPerFrame:
            self.animationClock = 0
            self.idleFrame += 1
            if self.idleFrame == 4: self.idleFrame = 0