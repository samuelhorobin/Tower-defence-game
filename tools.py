import pygame
import os
import json

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