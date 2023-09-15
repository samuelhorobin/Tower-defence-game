import tools
import pygame
from dataclasses import dataclass, field

@dataclass
class Animation:
    S: list[list[pygame.Surface, int]]
    SW: list[list[pygame.Surface, int]]
    W: list[list[pygame.Surface, int]]
    NW: list[list[pygame.Surface, int]]
    N: list[list[pygame.Surface, int]]
    NE: list[list[pygame.Surface, int]] = field(init=False)
    E: list[list[pygame.Surface, int]] = field(init=False)
    SE: list[list[pygame.Surface, int]] = field(init=False)

    def __post_init__(self):
        self.NE = [[pygame.transform.flip(image, True, False), interval] for image, interval in self.NW]
        self.E = [[pygame.transform.flip(image, True, False), interval] for image, interval in self.W]
        self.SE = [[pygame.transform.flip(image, True, False), interval] for image, interval in self.SW]


def business_dwarf():
    path = "Tower-defence-game/assets/enemies/business-dwarf"

    directions = ["South", "South West", "West", "North West", "North"]

    walk = Animation(*(tools.get_animation(path, direction, spritesheet_name="walk-spritesheet", data_name="walk-data", name="walk") for direction in directions))
    idle = Animation(*(tools.get_animation(path, direction, spritesheet_name="idle-spritesheet", data_name="idle-data", name="idle") for direction in directions))

    # walkS = tools.get_animation(path, "South", spritesheet_name="walk-spritesheet", data_name="walk-data", name="walk")
    # walkSW = tools.get_animation(path, "South West", spritesheet_name="walk-spritesheet", data_name="walk-data", name="walk")
    # walkW = tools.get_animation(path, "West", spritesheet_name="walk-spritesheet", data_name="walk-data", name="walk")
    # walkNW = tools.get_animation(path, "North West", spritesheet_name="walk-spritesheet", data_name="walk-data", name="walk")
    # walkN = tools.get_animation(path, "North", spritesheet_name="walk-spritesheet", data_name="walk-data", name="walk")
    # walkNE = [[pygame.transform.flip(image, True, False), interval] for image, interval in walkNW]
    # walkE = [[pygame.transform.flip(image, True, False), interval] for image, interval in walkW]
    # walkSE = [[pygame.transform.flip(image, True, False), interval] for image, interval in walkSW]

    # idleS = tools.get_animation(path, "south", spritesheet_name="idle-spritesheet", data_name="idle-data", name="idle")
    # idleSE = tools.get_animation(path, "South West", spritesheet_name="idle-spritesheet", data_name="idle-data", name="idle")
    # idleE = tools.get_animation(path, "West", spritesheet_name="idle-spritesheet", data_name="idle-data", name="idle")
    # idleNE = tools.get_animation(path, "North West", spritesheet_name="idle-spritesheet", data_name="idle-data", name="idle")
    # idleN = tools.get_animation(path, "North", spritesheet_name="idle-spritesheet", data_name="idle-data", name="idle")
    # idleNW = [[pygame.transform.flip(image, True, False), interval] for image, interval in idleNE]
    # idleW = [[pygame.transform.flip(image, True, False), interval] for image, interval in idleE]
    # idleSW = [[pygame.transform.flip(image, True, False), interval] for image, interval in idleSE]

    return [walk, idle]

def cogwheel():
    idleE = tools.get_animation("Tower-defence-game/assets/towers/Cogwall", "idleE")
    idleW = [[pygame.transform.flip(image, True, False), interval] for image, interval in idleE]
    
    return [idleE, idleW]

def skull():
    spin = tools.get_animation("Tower-defence-game/assets/particles/skull 8x8", "spin")
    return spin