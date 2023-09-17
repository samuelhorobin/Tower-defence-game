import os
import tools
import pygame

root_dir = os.path.dirname(os.path.abspath(__file__))

tileFlavours = {"1":os.path.join(root_dir, "assets", "tiles", "darktile.png"),
               "2":os.path.join(root_dir, "assets", "tiles", "lighttile.png"),
               "3":os.path.join(root_dir, "assets", "tiles", "block.png")
              }