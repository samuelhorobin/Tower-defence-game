''' LESSON 1: Tile-based map using sprites '''
# Libraries
import pygame
import os
import json
import numpy as np
import random

import cProfile
import settings

pygame.init()
RESOLUTION = (1920, 1080)
SCREEN = pygame.display.set_mode(RESOLUTION, pygame.FULLSCREEN)
UPSCALE = settings.UPSCALE

from tileflavours import * # tileFlavours
import keybinds
import pathfinding
import enemies



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
    
    subject = enemies.BusinessDwarf(Foreground = Foreground, speed = 1)
    subject.spawn(map, 1)
    Foreground.add(subject)
    subject.set_goal(map, 0, 0)

    # enemySprites = pygame.sprite.Group()
    # for i in range(10):
    #     enemySprites.add(enemies.BusinessDwarf(random.uniform(1,4), speed = 3))
    
    # for sprite in enemySprites:
    #     sprite.spawn(map, random.randint(0, 7))
    #     Foreground.add(sprite)
    #     sprite.set_goal(map, 0, random.randint(0, 7))

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
    
    

