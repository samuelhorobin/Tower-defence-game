''' LESSON 1: Tile-based map using sprites '''
# Libraries
import pygame
import os
import json
import numpy as np
import random

import cProfile

from tileflavours import * # tileFlavours
import keybinds
import pathfinding
import tools
import animations

pygame.init()

# Constants
RESOLUTION = (1920, 1080)
UPSCALE = 5
SCREEN = pygame.display.set_mode(RESOLUTION, pygame.FULLSCREEN)



# Functions
def logistic_function(x, L = 1, k = 10, x0 = 0.5, differentiated = False):
    ''' L = max val, k = growth rate, a = xVal of midpoint'''
    if differentiated == False:
        return L / (1 + np.exp(-k * (x - x0)))
    
    elif differentiated == True:
        return (L * k * np.exp(-k * (x - x0))) / (1 + np.exp(-k * (x - x0)))**2
    

def respond(eventKey):
    ''' Requires event.key as input'''
    if eventKey == keybinds.fullscreen:
        SCREEN = pygame.display.set_mode(RESOLUTION)


def extrapolateImage(rawImage, pos, float = False, rect = True):
    newDimensions = (rawImage.get_width() * UPSCALE, rawImage.get_height() * UPSCALE)
    if rect == False:
        return pygame.transform.scale(rawImage, newDimensions).convert_alpha()
    elif rect == True:
        if float == False:
            return pygame.transform.scale(rawImage, newDimensions).convert_alpha(), pygame.Rect(pos, newDimensions)
        elif float == True:
            return pygame.transform.scale(rawImage, newDimensions).convert_alpha(), pygame.FRect(pos, newDimensions)


def calcOffset(flavour):
    if flavour == 3:
        return 0, -8 * UPSCALE
    return 0, 0


def allign(foreVol,  backVol = RESOLUTION, backPos = (0,0), allignment = "centre"):
    ''' Allignment format: "centre, topmiddle, topleft, left, bottomleft ect '''
    xCent = int((backVol[0] / 2) - (foreVol[0] / 2)) + backPos[0] 
    yCent = int((backVol[1] / 2) - (foreVol[1] / 2)) + backPos[1]

    return xCent, yCent



# Load images/animations
businessDwarfAnimations = animations.business_dwarf()

for animation in businessDwarfAnimations:
            for frame in range(len(animation)):
                animation[frame][0] = extrapolateImage(animation[frame][0], (0,0), rect = False)


# Classes
class BlitSort:
    def __init__(self) -> None:
        self.list = pygame.sprite.Group()

    def add(self, sprite): self.list.add(sprite)
    def remove(self, sprite): self.list.remove(sprite)

    def sort(self):
        sortedSprites = sorted(self.list.sprites(), key=lambda sprite: sprite.rect.bottom)
        self.list = pygame.sprite.Group(sortedSprites)

    def update(self, screen, map, Foreground, Background):
        self.sort()
        for sprite in self.list:
            if sprite.__class__.__name__ == "BusinessDwarf":
                sprite.update(map, screen, Foreground)
            elif sprite.__class__.__name__ == "Rectparticle":
                sprite.update(screen)
            else:
                sprite.update()

class Rectparticle(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.width = self.height = random.randint(1, 2) * 5
        self.colour = (random.randint(150, 200), 61, 61)
        self.rect = pygame.FRect(pos, (self.width, self.height))

        self.lifespan = 2 + random.uniform(-1, 1) # s
        self.time = 0

        self.angle = random.randint(0, 180)
        self.strength = random.randint(5,10)
        self.xComp = np.cos(self.angle) * self.strength
        self.yComp = np.sin(self.angle) * self.strength * -1

        self.xRes = 0.1
        self.yGrav = 1

        self.floor = self.rect.bottom + random.randint(4, 11) * UPSCALE
    
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

        pygame.draw.rect(screen, self.colour, self.rect)



class SpriteAI(pygame.sprite.Sprite):
    def __init__(self, speed = 1) -> None:
        super().__init__()

        rawImageDir = os.path.join("Tower-defence-game", "assets", "enemies", "enemy.png")
        rawImage = pygame.image.load(rawImageDir)
        self.image, self.rect = extrapolateImage(rawImage, pos = (0,0), float = True)
        self.heightOffset = (8 * UPSCALE) - self.image.get_height()

        self.spawnIter = 0
        self.spawned = False
        self.goals = pygame.sprite.Group()
        self.journey = []
        self.speed = speed
        self.movement = (0,0)

        self.accY = self.accX = 0 #Accumulated speeds for decimal movement

    def spawn(self, map, row):
        self.gridPos = [len(map.tileGrid[row]) - 1, row]

        posX = map.pos[0] + len(map.tileGrid[row]) * 32 * UPSCALE
        posY = map.pos[1] + self.heightOffset + row * 16 * UPSCALE

        self.rect.x, self.rect.y = posX, posY
        self.spawned = True

    def set_goal(self, map, column, row):
        self.gridJourney = map.NodeManager.navigate(self.gridPos, (column, row))
        self.journey = [(map.pos[0] + node[0] * 32 * UPSCALE, map.pos[1] + node[1] * 16 * UPSCALE) for node in self.gridJourney]

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

    def draw(self):
        if self.spawned == True:
            SCREEN.blit(self.image, self.rect.topleft)

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
        self.health = 300
        
        self.walkS, self.walkSW, self.walkW, self.walkNW, \
        self.walkN, self.walkNE, self.walkE, self.walkSE, \
        self.idleS, self.idleSE, self.idleE, self.idleNE, \
        self.idleN, self.idleNW, self.idleW, self.idleSW = businessDwarfAnimations

        self.image = self.idleS[0][0]
        self.rect = pygame.FRect((0,0), (self.image.get_size()))
        self.heightOffset -= 2 * UPSCALE
        

    def update(self, map, screen, Foreground):
        self.move()
        self.draw()
        if len(self.journey) == 0:
            self.set_goal(map, random.randint(0, 7), random.randint(0, 7))
        
        self.damage(1, Foreground)

    def damage(self, dmg, Foreground):
        for i in range(dmg):
            Foreground.add(Rectparticle(self.rect.center))
        self.health -= dmg
        if self.health <= 0:
            for i in range(100): Foreground.add(Rectparticle(self.rect.center))
            self.kill()

    def draw(self):
        dt = 1/60
        self.animationClock += dt * self.speed

        if self.movement == (0, 1):
            SCREEN.blit(self.walkS[self.walkFrame][0], self.rect.topleft)
            self.facing = "South"
        if self.movement == (1, 1):
            SCREEN.blit(self.walkSW[self.walkFrame][0], self.rect.topleft)
            self.facing = "South-East"
        if self.movement == (1, 0):
            SCREEN.blit(self.walkW[self.walkFrame][0], self.rect.topleft)
            self.facing = "East"
        if self.movement == (1, -1):
            SCREEN.blit(self.walkNW[self.walkFrame][0], self.rect.topleft)
            self.facing = "North-East"
        if self.movement == (0, -1):
            SCREEN.blit(self.walkN[self.walkFrame][0], self.rect.topleft)
            self.facing = "North"
        if self.movement == (-1, -1):
            SCREEN.blit(self.walkNE[self.walkFrame][0], self.rect.topleft)
            self.facing = "North-West"
        if self.movement == (-1, 0):
            SCREEN.blit(self.walkE[self.walkFrame][0], self.rect.topleft)
            self.facing = "West"
        if self.movement == (-1, 1):
            SCREEN.blit(self.walkSE[self.walkFrame][0], self.rect.topleft)
            self.facing = "South-West"

        if self.movement == (0,0):
            if self.facing == "South":
                SCREEN.blit(self.idleS[self.idleFrame][0], self.rect.topleft)
            if self.facing == "South-East":
                SCREEN.blit(self.idleSE[self.idleFrame][0], self.rect.topleft)
            if self.facing == "East":
                SCREEN.blit(self.idleE[self.idleFrame][0], self.rect.topleft)
            if self.facing == "North-East":
                SCREEN.blit(self.idleNE[self.idleFrame][0], self.rect.topleft)
            if self.facing == "North":
                SCREEN.blit(self.idleN[self.idleFrame][0], self.rect.topleft)
            if self.facing == "North-West":
                SCREEN.blit(self.idleNW[self.idleFrame][0], self.rect.topleft)
            if self.facing == "West":
                SCREEN.blit(self.idleW[self.idleFrame][0], self.rect.topleft)
            if self.facing == "South-West":
                SCREEN.blit(self.idleSW[self.idleFrame][0], self.rect.topleft)

        if self.movement != (0, 0) and self.animationClock >= self.secondsPerFrame:
            
            self.animationClock = 0
            self.walkFrame += 1
            if self.walkFrame == 4: self.walkFrame = 0

        elif self.movement == (0,0) and self.animationClock >= self.secondsPerFrame:
            self.animationClock = 0
            self.idleFrame += 1
            if self.idleFrame == 4: self.idleFrame = 0
    


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, flavour) -> None:
        super().__init__()
        rawImageDir = tileFlavours[flavour]
        rawImage = pygame.image.load(rawImageDir)
        self.image, self.rect = extrapolateImage(rawImage, pos)

    def update(self) -> None:
        SCREEN.blit(self.image, self.rect.topleft)


class Map:
    def __init__(self) -> None:
        self.tiles = pygame.sprite.Group()

    def load(self, upperLayer, map: str, pos = (0,0)):
        self.pos = pos

        mapDir = os.path.join("Tower-defence-game", "assets", "maps", map)
        dataDir = os.path.join(mapDir, f"{map}.tmj")

        with open(dataDir, "r") as f:
            data = json.load(f)

        tileList = data["layers"][0]["data"]
        height = data["height"]

        self.tileGrid = np.array_split(tileList, height)
        self.size = (len(self.tileGrid) * 32 * UPSCALE, len(self.tileGrid[0]) * 16 * UPSCALE)
        self.load_tiles(upperLayer)
        
    def load_tiles(self, upperLayer):
        whitelist = [1, 2]
        for i, y in enumerate(self.tileGrid):
            for k, x in enumerate(y):
                xOffset, yOffset = [self.pos[i] + val for i, val in enumerate(calcOffset(x))]
                pos = (xOffset + (k * 32 * UPSCALE), yOffset + (i * 16 * UPSCALE))
                tile = Tile(pos = pos, flavour = str(x))
            
                if x in whitelist:
                    self.tiles.add(tile)
                elif x == 3:
                    upperLayer.add(tile)

    def load_pathing(self):
        traversableWhitelist = [1,2]
        nodeGrid = [list(row) for row in self.tileGrid]
        width = len(nodeGrid[0])
        height = len(nodeGrid)
        self.NodeManager = pathfinding.Grid(width, height)

        for i, row in enumerate(nodeGrid):
            for k, x in enumerate(row):
                if x in traversableWhitelist:
                    pass
                else:
                    self.NodeManager.add_wall(i, k)
        
    def setpos(self, pos, upperLayer):
        self.pos = pos

        self.tiles.empty()
        upperLayer.list.empty()

        self.load_tiles(upperLayer)

    def update(self):
        self.tiles.update()


def main():
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()

    Foreground = BlitSort()

    map = Map()
    map.load(Foreground, "testMap3")
    map.setpos(allign(map.size), Foreground)
    map.load_pathing()
    
    subject = BusinessDwarf(Foreground = Foreground, speed = 1)
    subject.spawn(map, 1)
    Foreground.add(subject)
    subject.set_goal(map, 0, 5)

    enemies = pygame.sprite.Group()
    for i in range(10):
        enemies.add(BusinessDwarf(random.uniform(1,4)))
    
    for sprite in enemies:
        sprite.spawn(map, random.randint(0, 7))
        Foreground.add(sprite)
        sprite.set_goal(map, 0, random.randint(0, 7))

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                #profiler.print_stats(sort='tottime')
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                keybinds.respond(event.key)
        
        SCREEN.fill((0,0,0))

        map.update()
        Foreground.update(SCREEN, map, Foreground, map)

        pygame.display.update()

    

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    
    

