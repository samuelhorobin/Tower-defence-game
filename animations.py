import tools
import pygame

def business_dwarf():
    walkS = tools.get_animation("assets/enemies/business-dwarf", "south", spritesheetName="walk-spritesheet", dataName="walk-data", name="walk")
    walkSW = tools.get_animation("assets/enemies/business-dwarf", "South West", spritesheetName="walk-spritesheet", dataName="walk-data", name="walk")
    walkW = tools.get_animation("assets/enemies/business-dwarf", "West", spritesheetName="walk-spritesheet", dataName="walk-data", name="walk")
    walkNW = tools.get_animation("assets/enemies/business-dwarf", "North West", spritesheetName="walk-spritesheet", dataName="walk-data", name="walk")
    walkN = tools.get_animation("assets/enemies/business-dwarf", "North", spritesheetName="walk-spritesheet", dataName="walk-data", name="walk")
    walkNE = [[pygame.transform.flip(image, True, False), interval] for image, interval in walkNW]
    walkE = [[pygame.transform.flip(image, True, False), interval] for image, interval in walkW]
    walkSE = [[pygame.transform.flip(image, True, False), interval] for image, interval in walkSW]

    idleS = tools.get_animation("assets/enemies/business-dwarf", "south", spritesheetName="idle-spritesheet", dataName="idle-data", name="idle")
    idleSE = tools.get_animation("assets/enemies/business-dwarf", "South West", spritesheetName="idle-spritesheet", dataName="idle-data", name="idle")
    idleE = tools.get_animation("assets/enemies/business-dwarf", "West", spritesheetName="idle-spritesheet", dataName="idle-data", name="idle")
    idleNE = tools.get_animation("assets/enemies/business-dwarf", "North West", spritesheetName="idle-spritesheet", dataName="idle-data", name="idle")
    idleN = tools.get_animation("assets/enemies/business-dwarf", "North", spritesheetName="idle-spritesheet", dataName="idle-data", name="idle")
    idleNW = [[pygame.transform.flip(image, True, False), interval] for image, interval in idleNE]
    idleW = [[pygame.transform.flip(image, True, False), interval] for image, interval in idleE]
    idleSW = [[pygame.transform.flip(image, True, False), interval] for image, interval in idleSE]

    return [walkS, walkSW, walkW, walkNW, walkN, walkNE, walkE, walkSE, idleS, idleSE, idleE, idleNE, idleN, idleNW, idleW, idleSW]