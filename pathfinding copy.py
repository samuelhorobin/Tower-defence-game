import pygame

# Libraries
import pygame
import numpy as np

# Classes
class Node:
    def __init__(self, pos = None, parent = None) -> None:
        self.parent = parent
        self.pos = pos
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.pos == other.pos


class Grid:
    def __init__(self, width, height) -> None:
        self.grid = [[0 for x in range(width)] for y in range(height)]
        self.width = width
        self.height = height

    def add_wall(self, *pos):
        self.grid[pos[1]][pos[0]] = 1


    def remove_wall(self, *pos):
        self.grid[pos[0]][pos[1]] = 0


    def navigate(self, start, *end):
        startNode = Node(start, None)
        startNode.g = startNode.f = startNode.h = 0
        endNodes = [Node(end, None) for end in end]
        for endNode in endNodes:
            endNode.g = endNode.f = endNode.h = 0

        openList = [startNode]
        closedList = []

        while len(openList) > 0:
            currentNode = openList[0]
            currentIndex = 0
            
            for i, item in enumerate(openList):
                if item.f < currentNode.f:
                    currentNode = item
                    currentIndex = i

            openList.pop(currentIndex)
            closedList.append(currentNode)


            if currentNode == endNode:
                path = []
                previousNode = currentNode
                while previousNode is not None:
                    path.append(previousNode.pos)
                    previousNode = previousNode.parent

                return path[::-1]
            

            children = []
            
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]:
                childPos = (currentNode.pos[0] + dx, currentNode.pos[1] + dy)
                if childPos[0] < 0 or self.width <= childPos[0]:
                    continue
                if childPos[1] < 0 or self.height <= childPos[1]:
                    continue

                if self.grid[childPos[0]][childPos[1]] != 0:
                    continue

                # Check for unnecessary diagonal movement
                try:
                    if dx != 0 and dy != 0:
                        if self.grid[currentNode.pos[0]][currentNode.pos[1] + dy] != 0 or self.grid[currentNode.pos[0] + dx][currentNode.pos[1]] != 0:
                            continue
                except:
                    pass
                
                childNode = Node(childPos, currentNode)
                children.append(childNode)


            for child in children:
                if child in closedList:
                    continue

                child.g = currentNode.g + 1
                child.h = (((child.pos[0] - endNode.pos[0]) ** 2) + ((child.pos[1] - endNode.pos[1]) ** 2))**1/2
                child.f = child.g + child.h

                if child in openList:
                    existing_child = openList[openList.index(child)]
                    if child.f > existing_child.f:
                        continue

                openList.append(child)


def main():
    pygame.init()

    # Constants
    pygame.display.set_caption("Game")
    clock = pygame.time.Clock()

    map =  [[0,0,0,0,0],
            [0,1,1,0,0],
            [0,1,1,0,0],
            [0,1,1,0,0],
            [0,0,0,0,0]]
    
    width, height = len(map[0]), len(map)

    RESOLUTION = width * 50, height * 50
    SCREEN = pygame.display.set_mode(RESOLUTION)

    PMap = Grid(width, height)

    for i, y in enumerate(map):
        for k, x in enumerate(y):
            if x == 1:
                PMap.add_wall(i, k)

    start = (4, 2)
    end = (0,1)

    path = PMap.navigate(start, end)



    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
        
        SCREEN.fill((0,0,0))

        for i, y in enumerate(PMap.grid):
            for k, x in enumerate(y):
                xCoord, yCoord = i*50, k*50
                rect = pygame.Rect(xCoord, yCoord, 50, 50)
                if x == 0:
                    pygame.draw.rect(SCREEN, (49, 40, 54), rect)
                elif x == 1:
                    pygame.draw.rect(SCREEN, (27, 26, 43), rect)

        for dest in path:
            destRect = pygame.Rect(dest[0]*50, dest[1]*50, 50, 50)
            pygame.draw.rect(SCREEN, (41, 82, 78), destRect)

        startRect = pygame.Rect(start[0]*50, start[1]*50, 50, 50)
        pygame.draw.rect(SCREEN, (189, 72, 68), startRect)

        endRect = pygame.Rect(end[0]*50, end[1]*50, 50, 50)
        pygame.draw.rect(SCREEN, (105, 148, 52), endRect)


        pygame.display.update()
    



if __name__ == "__main__":
    main()


    


