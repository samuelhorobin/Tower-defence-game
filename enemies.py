
import pygame
import os
import random
import numpy as np

import particles
import animations
import tools
import settings

businessDwarfAnimations = animations.business_dwarf()

class SpriteAI(pygame.sprite.Sprite):
    def __init__(self, speed = 1) -> None:
        super().__init__()
        root_dir = os.path.dirname(os.path.abspath(__file__))
        rawImageDir = os.path.join(root_dir, "assets", "enemies", "enemy.png")
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

        self.target = self.grid_target = None
        self.attacking = False

        self.accY = self.accX = 0 #Accumulated speeds for decimal movement

    def spawn(self, map, row):
        self.spawning = True
        self.spawnIter = 0

        self.grid_pos = [len(map.tile_grid[row]) - 1, row]

        posX = map.pos[0] + len(map.tile_grid[row]) * 32 * settings.UPSCALE
        posY = map.pos[1] + self.hitboxOffset + row * 16 * settings.UPSCALE

        self.hitbox.x, self.hitbox.y = posX, posY
        self.spawned = True

    def go_to(self, map, goals): #A* algorithm
        self.gridJourney = map.node_manager.navigate(self.grid_pos, goals)
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
        self.grid_target = tools.get_tile(map, self.target).grid_pos

    def adjust_to_tower(self, map):
        ''' Moves a sprite from diagonal of a tower to adjascent '''
        tile = self.get_closest_tile(map)
        for neighbour in tools.get_neighbours(map, tile):
            if neighbour != 3 and neighbour != None:
                for secondNeighbour in tools.get_neighbours(map, neighbour, layer = "towers"):
                    if secondNeighbour != 0 and secondNeighbour != None:
                        self.go_to(map, neighbour.grid_pos)
                        return  

    def recalibrate_grid_pos(self, map):
        tile = self.get_closest_tile(map)
        self.grid_pos = tile.grid_pos
    
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
            deltaX = tools.logistic_function(self.spawnIter, differentiated = True) * 2 * self.speed
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
                self.grid_pos = self.gridJourney.pop(0)
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
        self.animation_clock = self.idle_frame = self.walk_frame = 0
        self.facing = "West"
        self.seconds_per_frame = 0.2
        self.health = 100
        self.animations = businessDwarfAnimations
        self.image = self.animations["idle"].W[0][0]
        self.rect = pygame.FRect((0,0), (self.image.get_size()))
        self.height_offset = -3 * settings.UPSCALE

    def next_move(self, map):     
        if len(self.journey) == 0 and not self.isNextToTowerVar:
            self.find_tower(map)
            self.adjust_to_tower(map)

        if self.isNextToTowerVar:
            targetTower = tools.get_tile(map, self.grid_target, layer = "towers")
            if targetTower != None:
                selfCollisionDir = self.touching_tower(map, tower = targetTower)

        if len(self.journey) == 0 and self.isNextToTowerVar and not self.attacking:
            if selfCollisionDir == None:
                self.go_to(map, targetTower.grid_pos)

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
        self.rect.y += self.height_offset

        dt = 1/60
        self.animation_clock += dt * self.speed

        directions = [
            (0, 1, "S", "South"),
            (1, 1, "SE", "South-East"),
            (1, 0, "E", "East"),
            (1, -1, "NE", "North-East"),
            (0, -1, "N", "North"),
            (-1, -1, "NW", "North-West"),
            (-1, 0, "W", "West"),
            (-1, 1, "SW", "South-West"),
        ]

        for direction in directions:
            *vector, code, name = direction

            if self.movement == vector:
                screen.blit(
                    getattr(self.animations["walk"], code)[self.walk_frame][0],
                    self.rect.topleft,
                )
                self.facing = name

        if self.movement == (0,0):
            if self.facing == "South":
                screen.blit(self.animations["idle"].S[self.idle_frame][0], self.rect.topleft)
            elif self.facing == "South-East":
                screen.blit(self.animations["idle"].SE[self.idle_frame][0], self.rect.topleft)
            elif self.facing == "East":
                screen.blit(self.animations["idle"].E[self.idle_frame][0], self.rect.topleft)
            elif self.facing == "North-East":
                screen.blit(self.animations["idle"].NE[self.idle_frame][0], self.rect.topleft)
            elif self.facing == "North":
                screen.blit(self.animations["idle"].N[self.idle_frame][0], self.rect.topleft)
            elif self.facing == "North-West":
                screen.blit(self.animations["idle"].NW[self.idle_frame][0], self.rect.topleft)
            elif self.facing == "West":
                screen.blit(self.animations["idle"].W[self.idle_frame][0], self.rect.topleft)
            elif self.facing == "South-West":
                screen.blit(self.animations["idle"].SW[self.idle_frame][0], self.rect.topleft)

        if self.movement != (0, 0) and self.animation_clock >= self.seconds_per_frame:
            self.animation_clock = 0
            self.walk_frame += 1
            if self.walk_frame == 4: self.walk_frame = 0

        elif self.movement == (0,0) and self.animation_clock >= self.seconds_per_frame:
            self.animation_clock = 0
            self.idle_frame += 1
            if self.idle_frame == 4: self.idle_frame = 0

        # Hitbox
        #pygame.draw.rect(screen, (255,50,50), self.hitbox)