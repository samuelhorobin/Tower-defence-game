import pygame
import settings

class Camera:
    def __init__(self):
        self.display = pygame.Surface(settings.RESOLUTION)
        self.zoom = 1
        self.pos = [0,0]
        self.sprites = pygame.sprite.Group()

    def add(self, sprite): self.sprites.add(sprite)
    def remove(self, sprite): self.sprites.remove(sprite)

    def sort(self):
        sortedSprites = sorted(self.sprites.sprites(), key=lambda sprite: sprite.rect.bottom)
        self.sprites = pygame.sprite.Group(sortedSprites)

    def load(self):
        ''' Sorts sprites in order of y value for blit prioritization and blits them onto camera surface '''
        self.sort()
        for sprite in self.sprites:
            print(sprite)
            image, pos = sprite.load()
            self.display.blit(image, pos)

    def draw(self, surface):
        new_res = (settings.RESOLUTION[0] * self.zoom, settings.RESOLUTION[1] * self.zoom)
        self.display = pygame.transform.scale(self.display, new_res)
        surface.blit(self.display, self.pos)

    def change_zoom(self, val):
        ''' Changes zoom via addition, using the inputed val 
            Zoom is a constant, default being 1, which represents 100% zoom.
            Adding x, increases zoom by 100x%                '''
        
        self.zoom += val