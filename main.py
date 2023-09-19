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
import particles
import map as mp



# Classes
class BlitSort:
    def __init__(self) -> None:
        self.list = pygame.sprite.Group()

    def add(self, sprite): self.list.add(sprite)
    def remove(self, sprite): self.list.remove(sprite)

    def sort(self):
        sortedSprites = sorted(self.list.sprites(), key=lambda sprite: sprite.rect.bottom)
        self.list = pygame.sprite.Group(sortedSprites)

    def draw(self, screen):
        self.sort()
        for sprite in self.list:
            sprite.draw(screen)
            

def main():
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()

    frame = 0

    foreground = BlitSort()

    map = mp.MapManager()
    map.load(foreground, "testMap3")
    map.setpos(tools.allign(map.size), foreground)
    map.load_pathing()
    
    subject = enemies.BusinessDwarf(speed = 5)
    subject.spawn(map, 3)
    foreground.add(subject)
    map.enemies.add(subject)

    cog = towers.CogWheel()
    cog.set_pos((0,4), map)
    map.towers.add(cog)
    foreground.add(cog)

    # for i in range(10):
    #     test = enemies.BusinessDwarf(foreground = foreground, speed = random.uniform(2, 3))
    #     test.spawn(map, random.randint(0,7))
    #     foreground.add(test)
    #     map.enemies.add(test)

    for i in range(8):
        cog = towers.CogWheel()
        cog.set_pos((0,i), map)
        map.towers.add(cog)
        foreground.add(cog)

    

    while True:
        dt = clock.tick(settings.FPS) / 1000
        frame += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                #profiler.print_stats(sort='tottime')
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                print("true")
                keybinds.respond(event.key)
        
        SCREEN.fill((0,0,0))

        
        map.enemies.update(map)
        map.towers.update(map, foreground)
        
        particles.RectParticle_Manager.update(dt)
        particles.SkullParticle_Manager.update(dt)

        map.draw(SCREEN)
        foreground.draw(SCREEN)
        
        

        pygame.display.update()
        

        if frame % 10 == 0:
            test = enemies.BusinessDwarf(speed = random.uniform(2, 3))
            test.spawn(map, random.randint(0,7))
            foreground.add(test)
            map.enemies.add(test)


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    
    

