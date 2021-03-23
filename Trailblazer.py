from types import LambdaType
import pygame
import math
from queue import PriorityQueue
import time

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH,WIDTH))
pygame.display.set_caption("TrailBlazer")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Node:
    def __init__(self,row,col,width,total_rows):
        self.row=row
        self.col=col
        self.x=row*width
        self.y=col*width
        self.color=WHITE
        self.neighbors= []
        self.width = width
        self.total_rows = total_rows
        self.previous = None
    
    def get_pos(self):
        return self.row,self.col

    def is_closed(self):
        return self.color == RED
    
    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE
    
    def is_end(self):
        return self.color == PURPLE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = PURPLE

    def make_path(self):
        self.color = BLUE

    def draw(self,WIN):
        pygame.draw.rect(WIN,self.color,(self.x,self.y,self.width,self.width))

    def update_neighbors(self,grid):
        self.neighbors=[]
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): #Down node
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): #Up node
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): #Right node
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): #Left node
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self,other):
        return False

# A* Algorithm 
def Astar(draw, grid, start, end):

    cost = {node: float("inf") for row in grid for node in row}
    cost[start] = 0
    pqueue = PriorityQueue()
    pqueue.put((heuristic(start.get_pos(),end.get_pos()),start))
    tSet = {start}

    while not pqueue.empty():
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = pqueue.get()[1]
        tSet.remove(current)
        current.make_closed()
        if current == end:
            while current.previous != None:     #Reconstruct the path using previous
                current.make_path()
                current= current.previous

            end.make_end()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            if not neighbor.make_closed():
                temp_cost = cost[current] + 1
                if temp_cost < cost[neighbor]:
                    cost[neighbor] = temp_cost
                    neighbor.previous = current
                    if neighbor not in tSet:
                        pqueue.put(((cost[neighbor] + heuristic(neighbor.get_pos(), end.get_pos())), neighbor))
                        tSet.add(neighbor)
                        neighbor.make_open()
                        
    return False

def heuristic(p1,p2):
    #return int(math.dist(p1,p2))
    x1,y1 = p1
    x2,y2 = p2
    return abs(x2-x1)+abs(y2-y1)

def make_grid(rows,width):
    grid = []
    gap = width//rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i,j,gap,rows)
            grid[i].append(node)
    return grid

def draw_grid(win,rows,width):
    gap = width//rows
    for i in range(rows):
        pygame.draw.line(win,GREY,(0,i*gap),(width,i*gap))
        for j in range(rows):
            pygame.draw.line(win,GREY,(j*gap,0),(j*gap,width))

def draw(win,grid,rows,width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid (win, rows,width)
    pygame.display.update()

def get_mouse_pos(pos,rows,width):
    gap = width//rows
    x,y = pos

    row = x//gap
    col = y//gap
    return row,col

def main(win,width):
    ROWS = 50
    grid = make_grid(ROWS,width)

    start = None
    end = None

    run = True

    while run:
        draw(win,grid,ROWS,width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:   #Left button
                pos = pygame.mouse.get_pos()
                row,col = get_mouse_pos(pos,ROWS,width)
                node = grid[row][col]
                if not start and node!=end:
                    start = node
                    node.make_start()

                elif not end and node != start:
                    end = node
                    node.make_end()

                elif node != start and node != end:
                    node.make_barrier()   

            elif pygame.mouse.get_pressed()[2]: #Right button
                pos = pygame.mouse.get_pos()
                row,col = get_mouse_pos(pos,ROWS,width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    Astar(lambda: draw(win,grid,ROWS,width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

main(WIN,WIDTH)