
import pygame
import os
import random
import numpy as np

import particles
import animations
import tools
import settings

businessDwarfAnimations = animations.business_dwarf()

for animation_class in businessDwarfAnimations:
            #print(animation_class)
            print(animation_class.__dict__)
            for animation in animation_class.__dict__:
                for frame in animation_class.__dict__[animation]:
                    print(frame)
            
#setattr(animation, frame[0], tools.extrapolateImage(frame[0], (0,0), rect = False))

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
        
        self.isNextToTowerVar = False

        self.spawnIter = 0
        self.spawning = False
        self.spawned = False
        self.goals = pygame.sprite.Group()
        self.journey = []
        self.speed = speed
        self.movement = (0,0)
        self.hitbox = pygame.FRect((0,0), (14 * settings.UPSCALE, 14 * settings.UPSCALE))
        self.hitboxOffset = 1 * settings.UPSCALE

        self.target = self.gridTarget = None
        self.attacking = False

        self.accY = self.accX = 0 #Accumulated speeds for decimal movement

    def spawn(self, map, row):
        self.spawning = True
        self.spawnIter = 0

        self.gridPos = [len(map.tileGrid[row]) - 1, row]

        posX = map.pos[0] + len(map.tileGrid[row]) * 32 * settings.UPSCALE
        posY = map.pos[1] + self.hitboxOffset + row * 16 * settings.UPSCALE

        self.hitbox.x, self.hitbox.y = posX, posY
        self.spawned = True

    def go_to(self, map, goals): #A* algorithm
        self.gridJourney = map.NodeManager.navigate(self.gridPos, goals)
        self.journey = [(map.pos[0] + node[0] * 32 * settings.UPSCALE, map.pos[1] + self.hitboxOffset + node[1] * 16 * settings.UPSCALE) for node in self.gridJourney]

        nodeOffset = (160 - self.hitbox.width) // 2
        self.journey = [(node[0] + nodeOffset, node[1]) for node in self.journey]
        return self.gridJourney[-1]


    def go_up_to(self, map, goals, distance = 1):
        self.go_to(map, goals)
        for _ in range(distance):
            self.journey.pop(-1)
            lastGrisPos = self.gridJourney.pop(-1)
        return lastGrisPos

    def find_tower(self, map, whitelist = [], blacklist = [0]):
        goals = []
        for y, row in enumerate(map.towerGrid):
            for x, tower in enumerate(row):
                if tower in whitelist and tower not in blacklist:
                    goals.append((x, y))
                elif whitelist == [] and tower not in blacklist:
                    goals.append((x, y))

        self.target = self.go_up_to(map, goals)
        self.gridTarget = tools.get_tile(map, self.target).gridPos

    def adjust_to_tower(self, map):
        ''' Moves a sprite from diagonal of a tower to adjascent '''
        tile = self.get_closest_tile(map)
        for neighbour in tools.get_neighbours(map, tile):
            if neighbour != 3 and neighbour != None:
                for secondNeighbour in tools.get_neighbours(map, neighbour, layer = "towers"):
                    if secondNeighbour != 0 and secondNeighbour != None:
                        self.go_to(map, neighbour.gridPos)
                        return  

    def recalibrate_gridPos(self, map):
        tile = self.get_closest_tile(map)
        self.gridPos = tile.gridPos
    
    def get_closest_tile(self, map):
        for tile in map.tiles:
            if tile.rect.collidepoint(self.hitbox.center):
                return tile # Faster method

        closestTile = None # Backup
        closestDist = None
        for tile in map.tiles:
            if closestTile == None: closestTile = tile
            
            deltaY = self.hitbox.midbottom[0] - tile.rect.midbottom[0]
            deltaX = self.hitbox.midbottom[1] - tile.rect.midbottom[1]
            distance = (deltaY**2 + deltaX**2)

            if closestDist == None: closestDist = distance

            if distance < closestDist:
                closestTile = tile
                closestDist = distance

        return closestTile
    
    def next_to_tower(self, map):
        ''' Returns True if next to tower, False otherwise '''
        if self.isNextToTowerVar:
            return True
        
        tile = self.get_closest_tile(map)
        for neighbour in tools.get_neighbours(map, tile, layer = "towers"):
            if neighbour != 0 and neighbour != None:
                self.isNextToTowerVar = True
                return True
            
        return False

    def touching_tower(self, map, tower = "all"):
        ''' default: tower = "all", alternative, tower = <tower>
            Returns None if not touching                              '''
        if tower == "all":
            for tower in map.towers:
                if self.hitbox.colliderect(tower.hitbox):
                    direction = tools.collisionDir(tower.hitbox, self.hitbox)
                    return direction
            return None
        
        elif tower != "all":
            if self.hitbox.colliderect(tower.hitbox):
                    direction = tools.collisionDir(tower.hitbox, self.hitbox)
                    return direction
            return None
        
    def collide(self, direction, targetTower):
        if direction == (1, 0): self.hitbox.left = targetTower.hitbox.right
        if direction == (0, 1): self.hitbox.bottom = targetTower.hitbox.top
        if direction == (-1, 0): self.hitbox.right = targetTower.hitbox.left
        if direction == (0, -1): self.hitbox.top = targetTower.hitbox.bottom

    def move(self, map) -> None:
        self.goals.update()
        self.movement = (0,0)

        if self.spawning == True:
            deltaX = logistic_function(self.spawnIter, differentiated = True) * 2 * self.speed
            self.spawnIter += 0.01
            self.hitbox.move_ip(-abs(deltaX), 0)

            if abs(self.speed) < abs(deltaX):
                self.spawning = False
                self.spawned = True

            self.movement = (-1, 0)

        if self.spawned == True and len(self.journey) > 0:
            destX = self.journey[0][0]
            destY = self.journey[0][1]

            if destX - self.speed < int(self.hitbox.x) and destX + self.speed > int(self.hitbox.x): xBound = True
            else: xBound = False

            if destY - self.speed < int(self.hitbox.y) and destY + self.speed > int(self.hitbox.y): yBound = True
            else: yBound = False

            if xBound and yBound:
                self.journey.pop(0)
                self.gridPos = self.gridJourney.pop(0)
                if len(self.journey) > 0:
                    destX = self.journey[0][0]
                    destY = self.journey[0][1]

                self.isNextToTowerVar = False
                self.next_to_tower(map)
                

            deltaX = deltaY = 0
            
            if destX - self.speed >= int(self.hitbox.x): deltaX = self.speed
            if destY - self.speed >= int(self.hitbox.y): deltaY = self.speed

            if destX + self.speed <= int(self.hitbox.x): deltaX = -self.speed
            if destY + self.speed <= int(self.hitbox.y): deltaY = -self.speed

            vector = pygame.math.Vector2(deltaX, deltaY)
            self.movement = (deltaX / self.speed, deltaY / self.speed)
            
            if abs(deltaX) > 0 and abs(deltaY) > 0:
                vector.scale_to_length(self.speed)

            self.hitbox.x += vector.x
            self.hitbox.y += vector.y

    def draw(self, screen):
        if self.spawned == True:
            self.rect.midbottom = self.hitbox.midbottom
            screen.blit(self.image, self.rect.topleft)

    def update(self):
        self.move()
        self.draw()
            




class BusinessDwarf(SpriteAI):
    def __init__(self, speed = 1):
        super().__init__(speed=speed)
        self.animationClock = self.idleFrame = self.walkFrame = 0
        self.facing = "West"
        self.secondsPerFrame = 0.2
        self.health = 100
        
        self.walk, self.idle = businessDwarfAnimations

        self.image = self.idleS[0][0]
        self.rect = pygame.FRect((0,0), (self.image.get_size()))
        self.heightOffset = -3 * settings.UPSCALE


        

    def next_move(self, map):     
        if len(self.journey) == 0 and not self.isNextToTowerVar:
            self.find_tower(map)
            self.adjust_to_tower(map)

        if self.isNextToTowerVar:
            targetTower = tools.get_tile(map, self.gridTarget, layer = "towers")
            if targetTower != None:
                selfCollisionDir = self.touching_tower(map, tower = targetTower)

        if len(self.journey) == 0 and self.isNextToTowerVar and not self.attacking:
            if selfCollisionDir == None:
                self.go_to(map, targetTower.gridPos)

        if len(self.journey) != 0 and self.isNextToTowerVar:
            if selfCollisionDir != None:
                self.collide(selfCollisionDir, targetTower)
                self.attacking = True
                self.journey = []

    def update(self, map):
        self.move(map)
        self.next_move(map)

    def damage(self, dmg, foreground, angle = 0):
        self.health -= dmg

        if self.health <= 0:
            for i in range(40):
                particle = particles.FleshParticle(self.rect.center)
                particle.angle += angle
                particle.load()
                foreground.add(particle)
                particles.RectParticle_Manager.particles.add(particle)

            skull = particles.Skull(self)
            particles.SkullParticle_Manager.particles.add(skull)
            foreground.add(skull)
            
            self.kill()

        if self.health > 0:
            for i in range(dmg):
                particle = particles.Rectparticle(self.rect.center)
                particle.angle += angle
                particle.load()
                foreground.add(particle)
                particles.RectParticle_Manager.particles.add(particle)

    def draw(self, screen):
        self.rect.midbottom = self.hitbox.midbottom
        self.rect.y += self.heightOffset

        dt = 1/60
        self.animationClock += dt * self.speed

        if self.movement == (0, 1):
            screen.blit(self.walk.S[self.walkFrame][0], self.rect.topleft)
            self.facing = "South"
        if self.movement == (1, 1):
            screen.blit(self.walk.SW[self.walkFrame][0], self.rect.topleft)
            self.facing = "South-East"
        if self.movement == (1, 0):
            screen.blit(self.walk.W[self.walkFrame][0], self.rect.topleft)
            self.facing = "East"
        if self.movement == (1, -1):
            screen.blit(self.walk.NW[self.walkFrame][0], self.rect.topleft)
            self.facing = "North-East"
        if self.movement == (0, -1):
            screen.blit(self.walk.N[self.walkFrame][0], self.rect.topleft)
            self.facing = "North"
        if self.movement == (-1, -1):
            screen.blit(self.walk.NE[self.walkFrame][0], self.rect.topleft)
            self.facing = "North-West"
        if self.movement == (-1, 0):
            screen.blit(self.walk.E[self.walkFrame][0], self.rect.topleft)
            self.facing = "West"
        if self.movement == (-1, 1):
            screen.blit(self.walk.SE[self.walkFrame][0], self.rect.topleft)
            self.facing = "South-West"

        if self.movement == (0,0):
            if self.facing == "South":
                screen.blit(self.idle.S[self.idleFrame][0], self.rect.topleft)
            if self.facing == "South-East":
                screen.blit(self.idle.SE[self.idleFrame][0], self.rect.topleft)
            if self.facing == "East":
                screen.blit(self.idle.E[self.idleFrame][0], self.rect.topleft)
            if self.facing == "North-East":
                screen.blit(self.idle.NE[self.idleFrame][0], self.rect.topleft)
            if self.facing == "North":
                screen.blit(self.idle.N[self.idleFrame][0], self.rect.topleft)
            if self.facing == "North-West":
                screen.blit(self.idle.NW[self.idleFrame][0], self.rect.topleft)
            if self.facing == "West":
                screen.blit(self.idle.W[self.idleFrame][0], self.rect.topleft)
            if self.facing == "South-West":
                screen.blit(self.idle.SW[self.idleFrame][0], self.rect.topleft)

        if self.movement != (0, 0) and self.animationClock >= self.secondsPerFrame:
            
            self.animationClock = 0
            self.walkFrame += 1
            if self.walkFrame == 4: self.walkFrame = 0

        elif self.movement == (0,0) and self.animationClock >= self.secondsPerFrame:
            self.animationClock = 0
            self.idleFrame += 1
            if self.idleFrame == 4: self.idleFrame = 0

        # Hitbox
        #pygame.draw.rect(screen, (255,50,50), self.hitbox)