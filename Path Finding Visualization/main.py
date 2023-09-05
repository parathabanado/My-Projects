import pygame
import math
from queue import PriorityQueue

WIDTH=800
WIN=pygame.display.set_mode((WIDTH,WIDTH)) #setting up the display/canvas and specifying the dimensions for it
pygame.display.set_caption("A* Algorithm Path Finding Visualization")

#Defining colors we require:
RED=(255,0,0)
GREEN=(0,255,0)
BLUE=(0,255,0)
YELLOW=(255,255,0)
WHITE=(255,255,255)
BLACK=(0,0,0)
PURPLE=(128,0,128)
ORANGE=(255,165,0)
GREY=(128,128,128)
TURQUOISE=(64,224,208)

class Spot: # used to keep track of its position, width, color(which signifies its type), neighbors,etc
    def __init__(self,row,col,width,total_rows) :
        self.row=row
        self.col=col
        self.x=row*width
        self.y=col*width
        self.color=WHITE
        self.neighbors=[]
        self.width=width
        self.total_rows=total_rows
    
    def get_pos(self):
        return self.row,self.col
    
    #Methods that check the status of a Spot
    def is_closed(self): #checks if we have already visited this Spot
        return self.color==RED #We use RED color for spots we have visited, the color is updated when we visit it first
    def is_open(self):
        return self.color==GREEN
    def is_barrier(self):
        return self.color==BLACK
    def is_start(self):
        return self.color==ORANGE
    def is_path(self):
        return self.color==PURPLE
    def is_end(self):
        return self.color==TURQUOISE
    def reset(self):
        return self.color==WHITE

    #Methods that update Spot
    def make_closed(self): #Updates the Spots color
        self.color=RED #We use RED color for spots we have visited, the color is updated when we visit it first
    def make_open(self):
        self.color=GREEN
    def make_barrier(self):
        self.color=BLACK
    def make_start(self):
        self.color=ORANGE
    def make_path(self):
        self.color=PURPLE
    def make_end(self):
        self.color=TURQUOISE
    def reset(self):
        self.color=WHITE

    
    def draw(self,win): #Used for drawing the spot
        pygame.draw.rect(win, self.color,(self.x,self.y,self.width,self.width))  #Obvs used to draw a rectangle here it takes parameters that specify In what display we want to draw, the color, 

    def update_neighbors(self,grid):
        self.neighbors=[]
        if self.row < self.total_rows-1 and not grid[self.row+1][self.col].is_barrier(): #Down
            self.neighbors.append(grid[self.row+1][self.col])
        if self.row > 0 and not grid[self.row-1][self.col].is_barrier(): #UP
            self.neighbors.append(grid[self.row-1][self.col])
        if self.col < self.total_rows-1 and not grid[self.row][self.col+1].is_barrier(): #Right
            self.neighbors.append(grid[self.row][self.col+1])
        if self.col > 0 and not grid[self.row][self.col-1].is_barrier(): #Left
            self.neighbors.append(grid[self.row][self.col-1])
    

    def __lt__(self,other):
        return False


def make_grid(rows,grid_width): #number rows and width of the grid
    grid=[]
    gap=grid_width // rows #We require an integer division for obvious reasons
    for i in range(rows): # adds rows
        grid.append([])
        for j in range(rows): # we use rows as our grid is of square shape
            spot=Spot(i,j,gap,rows)
            grid[i].append(spot)
    return grid

def draw_grid_lines(win,rows,grid_width):
    gap=grid_width//rows
    for i in range(rows):
        pygame.draw.line(win,GREY,(0,i*gap),(grid_width,i*gap)) #drawing horizontal lines
        pygame.draw.line(win,GREY,(i*gap,0),(i*gap,grid_width)) #drawing vertical lines

def draw(win,grid,rows,grid_width):
    win.fill(WHITE) #fills the entire frame with one color
    for row in grid:
        for spot in row:
            spot.draw(win)
    draw_grid_lines(win,rows,grid_width)
    pygame.display.update()


def get_clicked_pos(pos,rows,grid_width): #takes the position of mouse and returns what spot it has clicked 
    gap=grid_width//rows
    y,x=pos 
    row=y//gap
    col=x//gap
    return row,col

def h(p1,p2): # this returns the heuristic value, takes to position of two spots as input
    x1,y1=p1  #Splitting
    x2,y2=p2
    return abs(x1-x2) +abs(y1-y2)

def reconstruct_path(came_from,current,start,draw):
    while current in came_from:
        current=came_from[current]
        if(current!=start):
            current.make_path()
            draw()


def algorithm(draw, grid,start,end):
    count=0 #used to break ties in F score
    open_set=PriorityQueue()
                #Fscore,count,node
    open_set.put((0,count,start)) #adding start node to the Queue
    came_from={}
    g_score={spot:float("inf") for row in grid for spot in row}
    g_score[start]=0
    f_score={spot:float("inf") for row in grid for spot in row}
    f_score[start]=h(start.get_pos(),end.get_pos())

    open_set_hash={start} #keeps track of all items in the PriorityQueue and allows us to check if an element is present in it or not, we cant search for elements in a priority queue and hence we implement this

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
        current=open_set.get()[2] #deque current node
        open_set_hash.remove(current) #sync with open_set_hash
        if current==end:
            reconstruct_path(came_from,end,start,draw)
            current.make_end()
            return True
        for neighbor in current.neighbors:
            temp_g_score=g_score[current]+1
            if temp_g_score<g_score[neighbor]:
                came_from[neighbor]=current
                g_score[neighbor]=temp_g_score
                f_score[neighbor]=temp_g_score +h(neighbor.get_pos(),end.get_pos())
                if neighbor not in open_set_hash: #checking if the neighbor is present in open_set_hash is the same as checking if it is in open_set or not 
                    count+=1
                    open_set.put((f_score[neighbor],count,neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()
    return False




def main(win,grid_width):
    ROWS=50
    grid=make_grid(ROWS,grid_width)
    

    start=None
    end=None

    run=True
    started=False #keeps check if the algoriithm has started runninf
    while run:
        draw(win,grid,ROWS,grid_width)
        for event in pygame.event.get(): #looping through all events that happen
            if event.type==pygame.QUIT:
                run=False
            if started: #if the the algorithm is running that is it is finding the shortest patht hen we don't want to allow any events to change the status of the spots in our grid as that will affect the algorithm
                continue
            if pygame.mouse.get_pressed()[0]: #if mouse was pressed and [0] is for the left click
                pos=pygame.mouse.get_pos()
                row,col=get_clicked_pos(pos,ROWS,grid_width)
                spot=grid[row][col]
                if not start and spot!=end: #The first and the second click should put down the start and end position respectively
                    start=spot
                    start.make_start()
                elif not end and spot!=start: #start exist but end does not
                    end=spot
                    end.make_end()
                elif spot !=end and spot !=start:
                    spot.make_barrier()
            elif pygame.mouse.get_pressed()[2]: #1 is for the wheel click, 2 is for the right click
                pos=pygame.mouse.get_pos()
                row,col=get_clicked_pos(pos,ROWS,grid_width)
                spot=grid[row][col]
                spot.reset()
                if spot==start:
                    start = None
                elif spot==end:
                    end= None

            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    algorithm(lambda:draw(win,grid,ROWS,grid_width),grid, start, end)
                elif event.key==pygame.K_c :
                    start=None
                    end=None
                    grid=make_grid(ROWS,grid_width)
    pygame.quit()
main(WIN,WIDTH)