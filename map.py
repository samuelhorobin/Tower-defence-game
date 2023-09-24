import pygame
import settings
import tools
import tileflavours
import json
import os
import pathfinding
import numpy as np


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, flavour, grid_pos) -> None:
        super().__init__()
        rawImageDir = tileflavours.tileFlavours[flavour]
        rawImage = pygame.image.load(rawImageDir)
        self.image, self.rect = tools.extrapolateImage(rawImage, pos)
        self.grid_pos = grid_pos
        self.flavour = flavour

    def draw(self, screen) -> None:
        screen.blit(self.image, self.rect.topleft)


class MapManager:
    def __init__(self) -> None:
        self.tiles = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

    def load(self, upperLayer, map: str, pos=(0, 0)):
        self.pos = pos

        root_dir = os.path.dirname(os.path.abspath(__file__))
        mapDir = os.path.join(root_dir, "assets", "maps", map)
        dataDir = os.path.join(mapDir, f"{map}.tmj")

        with open(dataDir, "r") as f:
            data = json.load(f)

        tileList = data["layers"][0]["data"]
        height = data["height"]

        self.tile_grid = np.array_split(tileList, height)
        self.towerGrid = [[0 for x in y] for y in self.tile_grid]

        self.size = (len(self.tile_grid) * 32 * settings.UPSCALE,
                     len(self.tile_grid[0]) * 16 * settings.UPSCALE)
        self.load_tiles(upperLayer)

    def load_tiles(self, foreground):
        whitelist = [1, 2]
        for i, y in enumerate(self.tile_grid):
            for k, x in enumerate(y):
                x_offset, y_offset = [self.pos[i] + val for i,
                                    val in enumerate(tools.calcOffset(x))]
                pos = (x_offset + (k * 32 * settings.UPSCALE),
                       y_offset + (i * 16 * settings.UPSCALE))
                tile = Tile(pos=pos, flavour=str(x), grid_pos=(k, i))

                if x in whitelist:
                    self.tiles.add(tile)
                elif x == 3:
                    foreground.add(tile)

    def load_pathing(self):
        traversable_whitelist = [1, 2]
        node_grid = [list(row) for row in self.tile_grid]
        width = len(node_grid[0])
        height = len(node_grid)
        self.node_manager = pathfinding.Grid(width, height)

        for i, row in enumerate(node_grid):
            for k, x in enumerate(row):
                if x in traversable_whitelist:
                    pass
                else:
                    self.node_manager.add_wall(i, k)

    def setpos(self, pos, upperLayer):
        self.pos = pos

        self.tiles.empty()
        upperLayer.sprites.empty()

        self.load_tiles(upperLayer)

    def draw(self, screen):
        self.tiles.draw(screen)
