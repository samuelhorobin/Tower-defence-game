import pygame
import settings
import tools
import tileflavours
import json
import os
import pathfinding
import numpy as np



class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, flavour, gridPos) -> None:
        super().__init__()
        rawImageDir = tileflavours.tileFlavours[flavour]
        rawImage = pygame.image.load(rawImageDir)
        self.image, self.rect = tools.extrapolateImage(rawImage, pos)
        self.gridPos = gridPos
        self.flavour = flavour

    def update(self, screen) -> None:
        screen.blit(self.image, self.rect.topleft)


class MapManager:
    def __init__(self) -> None:
        self.tiles = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()


    def load(self, upperLayer, map: str, pos = (0,0)):
        self.pos = pos

        mapDir = os.path.join("Tower-defence-game", "assets", "maps", map)
        dataDir = os.path.join(mapDir, f"{map}.tmj")

        with open(dataDir, "r") as f:
            data = json.load(f)

        tileList = data["layers"][0]["data"]
        height = data["height"]

        self.tileGrid = np.array_split(tileList, height)
        self.towerGrid = [[0 for x in y] for y in self.tileGrid]

        self.size = (len(self.tileGrid) * 32 * settings.UPSCALE, len(self.tileGrid[0]) * 16 * settings.UPSCALE)
        self.load_tiles(upperLayer)
        

    def load_tiles(self, upperLayer):
        whitelist = [1, 2]
        for i, y in enumerate(self.tileGrid):
            for k, x in enumerate(y):
                xOffset, yOffset = [self.pos[i] + val for i, val in enumerate(tools.calcOffset(x))]
                pos = (xOffset + (k * 32 * settings.UPSCALE), yOffset + (i * 16 * settings.UPSCALE))
                tile = Tile(pos = pos, flavour = str(x), gridPos = (k, i))
            
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


    def update(self, screen):
        self.tiles.update(screen)