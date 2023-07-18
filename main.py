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
SCREEN = pygame.display.set_mode(settings.RESOLUTION, pygame.FULLSCREEN)
UPSCALE = settings.UPSCALE

import keybinds
import enemies
import tools
import towers
import map as mp



def respond(eventKey):
    ''' Requires event.key as input'''
    if eventKey == keybinds.fullscreen:
        SCREEN = pygame.display.set_mode(settings.RESOLUTION)




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
            if     sprite.__class__.__name__ == "BusinessDwarf" \
                or sprite.__class__.__name__ == "CogWheel":
                sprite.update(screen, map, Foreground)

            elif   sprite.__class__.__name__ == "Rectparticle" \
                or sprite.__class__.__name__ == "ElixirParticle" \
                or sprite.__class__.__name__ == "Tile":
                sprite.update(screen)

            else:
                sprite.update()




def main():
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()

    Foreground = BlitSort()

    map = mp.MapManager()
    map.load(Foreground, "testMap3")
    map.setpos(tools.allign(map.size), Foreground)
    map.load_pathing()
    
    # subject = enemies.BusinessDwarf(Foreground = Foreground, speed = 2)
    # subject.spawn(map, 1)
    # Foreground.add(subject)
    # map.enemies.add(subject)

    # cog = towers.CogWheel()
    # cog.set_pos((0,0), map)
    # map.towers.add(cog)
    # Foreground.add(cog)

    for i in range(100):
        test = enemies.BusinessDwarf(Foreground = Foreground, speed = random.uniform(2, 3))
        test.spawn(map, random.randint(0,7))
        Foreground.add(test)
        map.enemies.add(test)

    for i in range(8):
        cog = towers.CogWheel()
        cog.set_pos((0,i), map)
        map.towers.add(cog)
        Foreground.add(cog)

    

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                profiler.print_stats(sort='tottime')
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                keybinds.respond(event.key)
        
        SCREEN.fill((0,0,0))

        map.update(SCREEN)
        Foreground.update(SCREEN, map, Foreground, map)

        pygame.display.update()


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    
    

