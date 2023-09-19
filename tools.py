import pygame
import os
import json
import settings
import numpy as np

def get_animation(spritesheetDir, animation, spritesheet_name = "spritesheet", data_name = "data", name = None):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    sprite_png = os.path.join(root_dir, spritesheetDir, f"{spritesheet_name}.png")
    sprite_json = os.path.join(root_dir, spritesheetDir, f"{data_name}.json")
    
    

    with open(sprite_json, "r") as file:
        data = json.load(file)
        for tag in data["meta"]["frameTags"]:
            if tag["name"] == animation:
                start = tag["from"]
                end = tag["to"]

        if name == None:
            name = os.path.basename(spritesheetDir)
        framesData = [data["frames"][f"{name} {i}.aseprite"] for i in range(start, end + 1)]

        frames = []
        spritesheet = pygame.image.load(sprite_png)

        for frame in framesData:
            x, y, w, h = [frame["frame"][i] for i in ["x", "y", "w", "h"]]
            frameSurface = spritesheet.subsurface(pygame.Rect(x, y, w, h))
            frames.append([frameSurface, frame["duration"]])

        return frames
    

def extrapolateImage(raw_image, pos = None, float = False, rect = True):
    new_dimensions = (raw_image.get_width() * settings.UPSCALE, raw_image.get_height() * settings.UPSCALE)
    if rect == False:
        return pygame.transform.scale(raw_image, new_dimensions).convert_alpha()
    elif rect == True:
        if float == False:
            return pygame.transform.scale(raw_image, new_dimensions).convert_alpha(), pygame.Rect(pos, new_dimensions)
        elif float == True:
            return pygame.transform.scale(raw_image, new_dimensions).convert_alpha(), pygame.FRect(pos, new_dimensions)
        
        
def logistic_function(x, L = 1, k = 10, x0 = 0.5, differentiated = False):
    ''' L = max val, k = growth rate, a = xVal of midpoint'''
    if differentiated == False:
        return L / (1 + np.exp(-k * (x - x0)))
    
    elif differentiated == True:
        return (L * k * np.exp(-k * (x - x0))) / (1 + np.exp(-k * (x - x0)))**2
    
    
def calcOffset(flavour):
    if flavour == 3:
        return 0, -8 * settings.UPSCALE
    return 0, 0


def allign(foreVol,  backVol = settings.RESOLUTION, backPos = (0,0), allignment = "centre"):
    ''' Allignment format: "centre, topmiddle, topleft, left, bottomleft ect '''
    x_cent = int((backVol[0] / 2) - (foreVol[0] / 2)) + backPos[0] 
    y_cent = int((backVol[1] / 2) - (foreVol[1] / 2)) + backPos[1]

    return x_cent, y_cent


def rotate(surface, angle, pivot, offset):
    """Rotate the surface around the pivot point.

    Args:
        surface (pygame.Surface): The surface that is to be rotated.
        angle (float): Rotate by this angle.
        pivot (tuple, list, pygame.math.Vector2): The pivot point.
        offset (pygame.math.Vector2): This vector is added to the pivot.
    """
    rotated_image = pygame.transform.rotozoom(surface, -angle, 1)  # Rotate the image.
    rotated_offset = offset.rotate(angle)  # Rotate the offset vector.
    # Add the offset vector to the center/pivot point to shift the rect.
    rect = rotated_image.get_rect(center=pivot+rotated_offset)
    return rotated_image, rect


def blitRotate(surf, image, pos, originPos, angle):

    # offset from pivot to center
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    
    # roatated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # roatetd image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

    # rotate and blit the image
    surf.blit(rotated_image, rotated_image_rect)
  
    # draw rectangle around the image
    pygame.draw.rect(surf, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()),2)


def get_neighbours(map, tile, layer = "tiles"):
    '''Layers: towers, tiles '''
    neighbours = []
    pos = tile.grid_pos
    for direction in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
        neighbour_pos = (pos[0] + direction[0], pos[1] + direction[1])
        try:
            if layer == "tiles": neighbour = get_tile(map, neighbour_pos, layer = "tiles")
            if layer == "towers": neighbour = get_tile(map, neighbour_pos, layer = "towers")
        except IndexError:
            neighbour = None

        neighbours.append(neighbour)
    
    return neighbours

def get_tile(map, pos, layer = "tiles"):
    ''' Layers: towers, tiles '''
    if layer == "tiles":
        for tile in map.tiles:
            if tile.grid_pos == pos:
                return tile
    elif layer == "towers":
        for tower in map.towers:
            if tower.grid_pos == pos:
                return tower
    return None

def collisionDir(rect1, rect2):
    deltaY = rect1.centery - rect2.centery
    deltaX = rect1.centerx - rect2.centerx

    if abs(deltaY) > abs(deltaX):
        if deltaY > 0: return (0, 1)
        elif deltaY < 0: return (0, -1)

    elif abs(deltaY) < abs(deltaX):
        if deltaX > 0: return (-1, 0)
        elif deltaX < 0: return (1, 0)

    elif abs(deltaY) == abs(deltaX):
        if deltaY > 0 and deltaX > 0: return (-1, -1)
        if deltaY < 0 and deltaX > 0: return (-1, 1)
        if deltaY > 0 and deltaX < 0: return (1, -1)
        if deltaY < 0 and deltaX < 0: return (1, 1)
