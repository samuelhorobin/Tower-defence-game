import pygame
import settings
import animations
import tools
import particles

from enum import Enum

cogWheelAnimations = animations.cogwheel()

for animation in cogWheelAnimations:
            for frame in range(len(animation)):
                animation[frame][0] = tools.extrapolateImage(animation[frame][0], (0,0), rect = False)



class TowerAI(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.identifier = 0

        self.animationClock = self.idleFrame = self.walkFrame = 0
        self.facing = "West"
        self.secondsPerFrame = 0.1
        self.health = 200

        self.idleE, self.idleW = cogWheelAnimations
        self.animation = self.idleE
        self.idleFrameCount = 6
        self.speed = 1

        self.image = self.idleE[0][0]
        self.rect = pygame.FRect((0,0), (self.image.get_size()))
        self.hitbox = pygame.FRect((0,0), (16 * settings.UPSCALE, 16 * settings.UPSCALE))
        self.gridPos = None

        self.state = "idle"

    def set_pos(self, coords, map):
        self.gridPos = coords

        map.towerGrid[coords[1]][coords[0]] = self.identifier

        left = map.pos[0] + (coords[0] * 32 * settings.UPSCALE)
        top = map.pos[1] + (coords[1] * 16 * settings.UPSCALE)
        tileRect = pygame.Rect((left, top), (32*settings.UPSCALE, 16*settings.UPSCALE))
        self.rect.midbottom = self.hitbox.midbottom = tileRect.midbottom
        

    def draw(self, screen):
        dt = 1/60
        self.animationClock += dt * self.speed

        if self.state == "idle":
            screen.blit(self.animation[self.idleFrame][0], self.rect.topleft)
     
            if self.animationClock >= self.secondsPerFrame:
                self.idleFrame += 1
                self.animationClock = 0

                if self.idleFrame == self.idleFrameCount: self.idleFrame = 0

    def damage(self, dmg, Foreground):
        for i in range(dmg):
            Foreground.add(particles.ElixirParticle(self.rect.center))
        self.health -= dmg
        if self.health <= 0:
            for _ in range(100): Foreground.add(particles.ElixirParticle(self.rect.center))
            self.kill()



class CogWheel(TowerAI):
    def __init__(self):
        super().__init__()
        self.identifier = 1
        self.idleFrameCount = 6
        self.idleE, self.idleW = cogWheelAnimations

        self.attackBox = pygame.Rect((0,0), (8*settings.UPSCALE, 16*settings.UPSCALE))

    def draw(self, screen):
        dt = 1/60
        self.animationClock += dt * self.speed

        if self.state == "idle":
            screen.blit(self.animation[self.idleFrame][0], self.rect.topleft)
     
            if self.animationClock >= self.secondsPerFrame:
                self.idleFrame += 1
                self.animationClock = 0

                if self.idleFrame == self.idleFrameCount: self.idleFrame = 0

    def update(self, screen, map, foreGround):
        self.draw(screen)
        
        if self.idleFrame == 4:
            self.attack(screen, map, foreGround)


    def attack(self, screen, map, foreGround):
        self.attackBox.midleft = self.hitbox.midright
        for enemy in map.enemies:
            if self.attackBox.colliderect(enemy.hitbox):
                enemy.damage(5, foreGround)


        #pygame.draw.rect(screen, (255,250,50), self.attackBox)
        