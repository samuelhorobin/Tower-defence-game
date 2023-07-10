import pygame
import os
import json
import settings
import numpy as np

def get_animation(spritesheetDir, animation, spritesheetName = "spritesheet", dataName = "data", name = None):
    spritePng = os.path.join(spritesheetDir, f"{spritesheetName}.png")
    spriteJson = os.path.join(spritesheetDir, f"{dataName}.json")

    with open(spriteJson, "r") as file:
        data = json.load(file)
        for tag in data["meta"]["frameTags"]:
            if tag["name"] == animation:
                start = tag["from"]
                end = tag["to"]

        if name == None:
            name = os.path.basename(spritesheetDir)
        framesData = [data["frames"][f"{name} {i}.aseprite"] for i in range(start, end + 1)]

        frames = []
        spritesheet = pygame.image.load(spritePng)

        for frame in framesData:
            x, y, w, h = [frame["frame"][i] for i in ["x", "y", "w", "h"]]
            frameSurface = spritesheet.subsurface(pygame.Rect(x, y, w, h))
            frames.append([frameSurface, frame["duration"]])

        return frames
    
def extrapolateImage(rawImage, pos, float = False, rect = True):
    newDimensions = (rawImage.get_width() * settings.UPSCALE, rawImage.get_height() * settings.UPSCALE)
    if rect == False:
        return pygame.transform.scale(rawImage, newDimensions).convert_alpha()
    elif rect == True:
        if float == False:
            return pygame.transform.scale(rawImage, newDimensions).convert_alpha(), pygame.Rect(pos, newDimensions)
        elif float == True:
            return pygame.transform.scale(rawImage, newDimensions).convert_alpha(), pygame.FRect(pos, newDimensions)
        
def logistic_function(x, L = 1, k = 10, x0 = 0.5, differentiated = False):
    ''' L = max val, k = growth rate, a = xVal of midpoint'''
    if differentiated == False:
        return L / (1 + np.exp(-k * (x - x0)))
    
    elif differentiated == True:
        return (L * k * np.exp(-k * (x - x0))) / (1 + np.exp(-k * (x - x0)))**2