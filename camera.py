import pygame

class Camera:
    def __init__(self):
        self.zoom = 1
        self.pos = [0,0]
        self.sprites = pygame.sprite.Group()

    def add(self, sprite): self.sprites.add(sprite)
    def remove(self, sprite): self.sprites.remove(sprite)

    def sort(self):
        sortedSprites = sorted(self.sprites.sprites(), key=lambda sprite: sprite.rect.bottom)
        self.sprites = pygame.sprite.Group(sortedSprites)

    def draw(self, screen):
        self.sort()
        for sprite in self.sprites:
            sprite.draw(screen)

    def change_zoom(self, val):
        ''' Changes zoom via addition, using the inputed val 
            Zoom is a constant, default being 1, which represents 100% zoom.
            Adding x, increases zoom by 100x%                '''
        
        self.zoom += val
        for sprite in self.sprites:
            sprite.resize(val)