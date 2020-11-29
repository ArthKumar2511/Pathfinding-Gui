import pygame
import time
from priority_queue import PrioritySet, PriorityQueue, AStarQueue
from math import inf
import random
from collections import deque

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (0, 111, 255)
ORANGE = (255, 128, 0)
PURPLE = (128, 0, 255)
YELLOW = (255, 255, 0)
GREY = (143, 143, 143)
BROWN = (186, 127, 50)
DARK_GREEN = (0, 128, 0)
DARKER_GREEN = (0, 50, 0)
DARK_BLUE = (0, 0, 128)

class Button():
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.text = text

    def draw(self,win,outline=None):
        if outline:
            pygame.draw.rect(win, outline, (self.x,self.y,self.width,self.height),0)
            
        pygame.draw.rect(win, self.color, (self.x+1,self.y+1,self.width-1,self.height-1),0)
        
        if self.text != '':
            font = pygame.font.SysFont('arial', 12)
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + int(self.width/2 - text.get_width()/2), self.y + int(self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False

class Node():

    nodetypes = ['blank', 'start', 'end', 'wall', 'mud', 'dormant']

    colors = {  'regular': {'blank': WHITE, 'start': RED, 'end': LIGHT_BLUE, 'wall': BLACK, 'mud': BROWN, 'dormant': GREY},
                'visited': {'blank': GREEN, 'start': RED, 'end': LIGHT_BLUE, 'wall': BLACK, 'mud': DARK_GREEN, 'dormant': GREY},
                'path': {'blank': BLUE, 'start': RED, 'end': LIGHT_BLUE, 'wall': BLACK, 'mud': DARK_BLUE, 'dormant': GREY}
            }

    distance_modifiers = {'blank': 1, 'start': 1, 'end': 1, 'wall': inf, 'mud': 3, 'dormant': inf}

    def __init__(self, nodetype, text='', colors=colors, dmf=distance_modifiers):
        self.nodetype = nodetype
        self.rcolor = colors['regular'][self.nodetype]
        self.vcolor = colors['visited'][self.nodetype]
        self.pcolor = colors['path'][self.nodetype]
        self.is_visited = True if nodetype == 'start' else True if nodetype == 'end' else False
        self.is_path = True if nodetype == 'start' else True if nodetype == 'end' else False
        self.distance_modifier = dmf[self.nodetype]
        self.color = self.pcolor if self.is_path else self.vcolor if self.is_visited else self.rcolor

    def update(self, nodetype=False, is_visited='unchanged', is_path='unchanged', colors=colors, dmf=distance_modifiers, nodetypes=nodetypes):
        if nodetype:
            assert nodetype in nodetypes, f"nodetype must be one of: {nodetypes}"
            if (self.nodetype == ('start' or 'end')) and (nodetype == ('wall' or 'mud')):
                pass
            else:
                self.nodetype = nodetype        

        if is_visited != 'unchanged':
            assert type(is_visited) == bool, "'is_visited' must be boolean: True or False" 
            self.is_visited = is_visited

        if is_path != 'unchanged':
            assert type(is_path) == bool, "'is_path' must be boolean: True or False" 
            self.is_path = is_path

        self.rcolor = colors['regular'][self.nodetype]
        self.vcolor = colors['visited'][self.nodetype]
        self.pcolor = colors['path'][self.nodetype]
        self.distance_modifier = dmf[self.nodetype]
        self.color = self.pcolor if self.is_path else self.vcolor if self.is_visited else self.rcolor

WIDTH = 6
HEIGHT = WIDTH
BUTTON_HEIGHT = 40
MARGIN = 0

grid = []
ROWS = 90

for row in range(ROWS):
    grid.append([])
    for column in range(ROWS):
        grid[row].append(Node('blank')) 

START_POINT = (random.randrange(2,ROWS-1,2)-1,random.randrange(2,ROWS-1,2)-1)
END_POINT = (random.randrange(2,ROWS-1,2),random.randrange(2,ROWS-1,2))

grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
grid[END_POINT[0]][END_POINT[1]].update(nodetype='end')

DIAGONALS = False
VISUALISE = True
mouse_drag = False
drag_start_point = False
drag_end_point = False

path_found = False
algorithm_run = False

pygame.init()
FONT = pygame.font.SysFont('arial', 6)

SCREEN_WIDTH = ROWS * (WIDTH + MARGIN) + MARGIN * 2
SCREEN_HEIGHT = SCREEN_WIDTH + BUTTON_HEIGHT * 3
WINDOW_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(WINDOW_SIZE)

dijkstraButton = Button(GREY, 0, SCREEN_WIDTH, SCREEN_WIDTH/3, BUTTON_HEIGHT, "Dijkstra Algo")
dfsButton = Button(GREY, 0, SCREEN_WIDTH + BUTTON_HEIGHT, SCREEN_WIDTH/6, BUTTON_HEIGHT, "DFS Algo")
bfsButton = Button(GREY, 0 + SCREEN_WIDTH/6 + 1, SCREEN_WIDTH + BUTTON_HEIGHT, SCREEN_WIDTH/6, BUTTON_HEIGHT, "BFS Algo")
astarButton = Button(GREY, 0, SCREEN_WIDTH + BUTTON_HEIGHT*2, SCREEN_WIDTH/3, BUTTON_HEIGHT, "A* Algo")
resetButton = Button(GREY, SCREEN_WIDTH/3, SCREEN_WIDTH, SCREEN_WIDTH/3, BUTTON_HEIGHT*2, "Reset")
mazeButton = Button(GREY, (SCREEN_WIDTH/3)*2, SCREEN_WIDTH, SCREEN_WIDTH/6, BUTTON_HEIGHT, "Maze (Prim)")
altPrimButton = Button(GREY, (SCREEN_WIDTH/6)*5, SCREEN_WIDTH, SCREEN_WIDTH/6, BUTTON_HEIGHT, "Maze (Alt Prim)")
recursiveMazeButton = Button(GREY, (SCREEN_WIDTH/3)*2, SCREEN_WIDTH + BUTTON_HEIGHT, SCREEN_WIDTH/3, BUTTON_HEIGHT, "Maze (recursive div)")
terrainButton = Button(GREY, (SCREEN_WIDTH/3)*2, SCREEN_WIDTH + BUTTON_HEIGHT*2, SCREEN_WIDTH/3, BUTTON_HEIGHT, "Random Terrain")
visToggleButton = Button(GREY, SCREEN_WIDTH/3, SCREEN_WIDTH + BUTTON_HEIGHT*2, SCREEN_WIDTH/3, BUTTON_HEIGHT, f"Visualise: {str(VISUALISE)}")

pygame.display.set_caption("Pathfinder")
done = False
clock = pygame.time.Clock()

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            pressed = pygame.key.get_pressed()
            if pos[1] <= SCREEN_WIDTH-1:
                column = pos[0] // (WIDTH + MARGIN)
                row = pos[1] // (HEIGHT + MARGIN)

                if (row,column) == START_POINT:
                    drag_start_point = True
                elif (row,column) == END_POINT:
                    drag_end_point = True
                else:
                    cell_updated = grid[row][column]
                    if pressed[pygame.K_LCTRL]:
                        update_cell_to = 'mud'
                    else:
                        update_cell_to = 'wall'
                    cell_updated.update(nodetype=update_cell_to)
                    mouse_drag = True
                    if algorithm_run and cell_updated.is_path == True:
                        path_found = update_path()

            elif dijkstraButton.isOver(pos):
                clear_visited()
                update_gui(draw_background=False, draw_buttons=False)
                if VISUALISE:    
                    pygame.display.flip()
                path_found = dijkstra(grid, START_POINT, END_POINT)
                grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
                algorithm_run = 'dijkstra'
            
            elif dfsButton.isOver(pos):
                clear_visited()
                update_gui(draw_background=False, draw_buttons=False)
                if VISUALISE:
                    pygame.display.flip()
                path_found = xfs(grid, START_POINT, END_POINT, x='d')
                grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
                algorithm_run = 'dfs'
            
            elif bfsButton.isOver(pos):
                clear_visited()
                update_gui(draw_background=False, draw_buttons=False)
                if VISUALISE:
                    pygame.display.flip()
                path_found = xfs(grid, START_POINT, END_POINT, x='b')
                grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
                algorithm_run = 'bfs'

            elif astarButton.isOver(pos):
                clear_visited()
                update_gui(draw_background=False, draw_buttons=False)
                if VISUALISE:
                    pygame.display.flip()
                path_found = dijkstra(grid, START_POINT, END_POINT, astar=True)
                grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
                algorithm_run = 'astar'

            elif resetButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(ROWS):
                    for column in range(ROWS):
                        if (row,column) != START_POINT and (row,column) != END_POINT:
                            grid[row][column].update(nodetype='blank', is_visited=False, is_path=False)

            elif mazeButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(ROWS):
                    for column in range(ROWS):
                        if (row,column) != START_POINT and (row,column) != END_POINT:
                            grid[row][column].update(nodetype='blank', is_visited=False, is_path=False)
                grid = better_prim()

            elif altPrimButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(ROWS):
                    for column in range(ROWS):
                        if (row,column) != START_POINT and (row,column) != END_POINT:
                            grid[row][column].update(nodetype='blank', is_visited=False, is_path=False)
                grid = prim()

            elif recursiveMazeButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(ROWS):
                    for column in range(ROWS):
                        if (row,column) != START_POINT and (row,column) != END_POINT:
                            grid[row][column].update(nodetype='blank', is_visited=False, is_path=False)
                            draw_square(row,column)
                if VISUALISE:
                    pygame.display.flip()
                recursive_division()
        
            elif terrainButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(ROWS):
                    for column in range(ROWS):
                        if (row,column) != START_POINT and (row,column) != END_POINT:
                            grid[row][column].update(nodetype='blank', is_visited=False, is_path=False)
                update_gui(draw_background=False, draw_buttons=False)
                random_terrain()

            elif visToggleButton.isOver(pos):
                if VISUALISE:
                    VISUALISE = False
                else:
                    VISUALISE = True

        
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_drag = drag_end_point = drag_start_point = False
        
        elif event.type == pygame.MOUSEMOTION:
            left, middle, right = pygame.mouse.get_pressed()
            if not left:
                mouse_drag = drag_end_point = drag_start_point = False
                continue

            pos = pygame.mouse.get_pos()
            column = pos[0] // (WIDTH + MARGIN)
            row = pos[1] // (HEIGHT + MARGIN)
            
            if pos[1] >= SCREEN_WIDTH-2 or pos[1] <= 2 or pos[0] >= SCREEN_WIDTH-2 or pos[0] <= 2:
                mouse_drag = False
                continue
            
            cell_updated = grid[row][column]

            if mouse_drag == True:
                if (row,column) == START_POINT:
                    pass
                elif (row,column) == END_POINT:
                    pass
                else:
                    if pressed[pygame.K_LCTRL]:
                        update_cell_to = 'mud'
                    else:
                        update_cell_to = 'wall'
                    cell_updated.update(nodetype=update_cell_to)

                mouse_drag = True
                
                if algorithm_run:
                    if cell_updated.is_path == True:
                        path_found = update_path()
            
            elif drag_start_point == True:
                if grid[row][column].nodetype == "blank":
                    grid[START_POINT[0]][START_POINT[1]].update(nodetype='blank', is_path=False, is_visited=False)
                    START_POINT = (row,column)
                    grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
                    if algorithm_run:
                        path_found = update_path()
                        grid[START_POINT[0]][START_POINT[1]].update(nodetype='start') 
            
            elif drag_end_point == True:
                if grid[row][column].nodetype == "blank":
                    grid[END_POINT[0]][END_POINT[1]].update(nodetype='blank', is_path=False, is_visited=False)
                    END_POINT = (row,column)
                    grid[END_POINT[0]][END_POINT[1]].update(nodetype='end')
                    if algorithm_run:
                        path_found = update_path()
                        grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')

            pygame.display.flip()

    def clear_visited():
        excluded_nodetypes = ['start', 'end', 'wall', 'mud']
        for row in range(ROWS):
            for column in range(ROWS):
                if grid[row][column].nodetype not in excluded_nodetypes:
                    grid[row][column].update(nodetype="blank", is_visited=False, is_path=False)
                else:
                     grid[row][column].update(is_visited=False, is_path=False)
        update_gui(draw_background=False, draw_buttons=False)

    def update_path(algorithm_run=algorithm_run):
        
        clear_visited()
        
        valid_algorithms = ['dijkstra', 'astar', 'dfs', 'bfs']

        assert algorithm_run in valid_algorithms, f"last algorithm used ({algorithm_run}) is not in valid algorithms: {valid_algorithms}"

        if algorithm_run == 'dijkstra':
            path_found = dijkstra(grid, START_POINT, END_POINT, visualise=False)
        elif algorithm_run == 'astar':
            path_found = dijkstra(grid, START_POINT, END_POINT, visualise=False, astar=True)
        elif algorithm_run == 'dfs':
            path_found = xfs(grid, START_POINT, END_POINT, x='d', visualise=False)
        elif algorithm_run == 'bfs':
            path_found = xfs(grid, START_POINT, END_POINT, x='b', visualise=False)
        else:
            path_found = False
        return path_found

    def random_terrain(mazearray=grid, num_patches=False, visualise=VISUALISE):
        if not num_patches:
            num_patches = random.randrange(int(ROWS/10),int(ROWS/4))

        terrain_nodes = set([])

        if VISUALISE:
            pygame.display.flip()

        for patch in range(num_patches+1):
            neighbour_cycles = 0
            centre_point = (random.randrange(1,ROWS-1),random.randrange(1,ROWS-1))
            patch_type = 'mud'
            terrain_nodes.add(centre_point)
            
            while len(terrain_nodes) > 0:
                node = terrain_nodes.pop()
                
                if grid[node[0]][node[1]].nodetype != 'start' and grid[node[0]][node[1]].nodetype != 'end':
                    grid[node[0]][node[1]].update(nodetype=patch_type)
                    draw_square(node[0],node[1])
                    
                    if visualise:
                        update_square(node[0],node[1])
                        time.sleep(0.000001)
                
                neighbour_cycles += 1
                
                for node, ntype in get_neighbours(node):
                    
                    if grid[node[0]][node[1]].nodetype == 'mud':
                        continue
                    threshold = 700-(neighbour_cycles*10)
                    
                    if random.randrange(1,101) <= threshold:
                        terrain_nodes.add(node)

    def dict_move(from_dict, to_dict, item):
        to_dict[item] = from_dict[item]
        from_dict.pop(item)
        return from_dict, to_dict


    def get_neighbours(node, max_width=ROWS-1, diagonals=DIAGONALS):
        if not diagonals:
            neighbours = (
                ((min(max_width,node[0]+1),node[1]),"+"),
                ((max(0,node[0]-1),node[1]),"+"),
                ((node[0],min(max_width,node[1]+1)),"+"),
                ((node[0],max(0,node[1]-1)),"+")
            )
        else:
            neighbours = (
                ((min(max_width,node[0]+1),node[1]),"+"),
                ((max(0,node[0]-1),node[1]),"+"),
                ((node[0],min(max_width,node[1]+1)),"+"),
                ((node[0],max(0,node[1]-1)),"+"),
                ((min(max_width,node[0]+1),min(max_width,node[1]+1)),"x"),
                ((min(max_width,node[0]+1),max(0,node[1]-1)),"x"),
                ((max(0,node[0]-1),min(max_width,node[1]+1)),"x"),
                ((max(0,node[0]-1),max(0,node[1]-1)),"x")
            )

        return (neighbour for neighbour in neighbours if neighbour[0] != node)

    def draw_square(row,column,grid=grid):
        pygame.draw.rect(
            screen,
            grid[row][column].color,
            [
                (MARGIN + HEIGHT) * column + MARGIN,
                (MARGIN + HEIGHT) * row + MARGIN,
                WIDTH,
                HEIGHT
            ]
        )
        pygame.event.pump()

    def update_square(row,column):
        pygame.display.update(
            (MARGIN + WIDTH) * column + MARGIN,
            (MARGIN + HEIGHT) * row + MARGIN,
            WIDTH,
            HEIGHT
        )
        pygame.event.pump()

    def prim(mazearray=False, start_point=False, visualise=VISUALISE):
        if not mazearray:
            mazearray = []
            for row in range(ROWS):
                mazearray.append([])
                for column in range(ROWS):
                    mazearray[row].append(Node('wall'))
                    if visualise:
                        draw_square(row,column,grid=mazearray)

        n = len(mazearray) - 1

        if not start_point:
            start_point = (random.randrange(0,n,2),random.randrange(0,n,2))
        
        if visualise:
            draw_square(start_point[0], start_point[1], grid=mazearray)
            pygame.display.flip()

        walls = set([])

        neighbours = get_neighbours(start_point, n)

        for neighbour, ntype in neighbours:
            if mazearray[neighbour[0]][neighbour[1]].nodetype == 'wall':
                walls.add(neighbour)

        while len(walls) > 0:                
            wall = random.choice(tuple(walls))
            wall_neighbours = get_neighbours(wall, n)
            neighbouring_walls = set()
            pcount = 0
            for wall_neighbour, ntype in wall_neighbours:
                if wall_neighbour == (start_point or END_POINT):
                    continue
                if mazearray[wall_neighbour[0]][wall_neighbour[1]].nodetype != 'wall':
                    pcount += 1
                else:
                    neighbouring_walls.add(wall_neighbour)
                    
            if pcount <= 1:
                mazearray[wall[0]][wall[1]].update(nodetype='blank')
                if visualise:
                    draw_square(wall[0],wall[1],mazearray)
                    update_square(wall[0],wall[1])
                    time.sleep(0.000001)

                walls.update(neighbouring_walls)
            walls.remove(wall)            

        mazearray[END_POINT[0]][END_POINT[1]].update(nodetype='end')
        mazearray[START_POINT[0]][START_POINT[1]].update(nodetype='start')
        return mazearray

    def better_prim(mazearray=False, start_point=False, visualise=VISUALISE):
        if not mazearray:
            mazearray = []
            for row in range(ROWS):
                mazearray.append([])
                for column in range(ROWS):
                    if row % 2 != 0 and column % 2 != 0:
                        mazearray[row].append(Node('dormant'))
                    else:
                        mazearray[row].append(Node('wall'))
                    if visualise:
                        draw_square(row,column,grid=mazearray)

        n = len(mazearray) - 1

        if not start_point:
            start_point = (random.randrange(1,n,2),random.randrange(1,n,2))
            mazearray[start_point[0]][start_point[1]].update(nodetype='blank')
        
        if visualise:
            draw_square(start_point[0], start_point[1], grid=mazearray)
            pygame.display.flip()

        walls = set()

        starting_walls = get_neighbours(start_point, n)

        for wall, ntype in starting_walls:
            if mazearray[wall[0]][wall[1]].nodetype == 'wall':
                walls.add(wall)

        while len(walls) > 0:
            wall = random.choice(tuple(walls))
            visited = 0
            add_to_maze = []

            for wall_neighbour, ntype in get_neighbours(wall,n):
                if mazearray[wall_neighbour[0]][wall_neighbour[1]].nodetype == 'blank':
                    visited += 1

            if visited <= 1:
                mazearray[wall[0]][wall[1]].update(nodetype='blank')
                
                if visualise:
                    draw_square(wall[0],wall[1],mazearray)
                    update_square(wall[0],wall[1])
                    time.sleep(0.0001)

                for neighbour, ntype in get_neighbours(wall,n):
                    if mazearray[neighbour[0]][neighbour[1]].nodetype == 'dormant':
                        add_to_maze.append((neighbour[0],neighbour[1]))
                
                if len(add_to_maze) > 0:
                    cell = add_to_maze.pop()
                    mazearray[cell[0]][cell[1]].update(nodetype='blank')
                    
                    if visualise:
                        draw_square(cell[0],cell[1],mazearray)
                        update_square(cell[0],cell[1])
                        time.sleep(0.0001)
                    
                    for cell_neighbour, ntype in get_neighbours(cell,n):
                        if mazearray[cell_neighbour[0]][cell_neighbour[1]].nodetype == 'wall':
                            walls.add(cell_neighbour)

            walls.remove(wall)

        mazearray[END_POINT[0]][END_POINT[1]].update(nodetype='end')
        mazearray[START_POINT[0]][START_POINT[1]].update(nodetype='start')
        return mazearray

    def gaps_to_offset():
        return [x for x in range(2, ROWS, 3)]

    def recursive_division(chamber=None, visualise=VISUALISE, gaps_to_offset=gaps_to_offset(), halving=True):

        sleep = 0.001
        sleep_walls = 0.001

        if chamber == None:
            chamber_width = len(grid)
            chamber_height = len(grid[1])
            chamber_left = 0
            chamber_top = 0
        else:
            chamber_width = chamber[2]
            chamber_height = chamber[3]
            chamber_left = chamber[0]
            chamber_top = chamber[1]

        if halving:
            x_divide = int(chamber_width/2)
            y_divide = int(chamber_height/2)
        
        if chamber_width < 3:
            pass
        else:
            for y in range(chamber_height):
                grid[chamber_left + x_divide][chamber_top + y].update(nodetype='wall')
                draw_square(chamber_left + x_divide, chamber_top + y)
                if visualise:
                    update_square(chamber_left + x_divide, chamber_top + y)
                    time.sleep(sleep_walls)
         
        if chamber_height < 3:
            pass
        else:
            for x in range(chamber_width):
                grid[chamber_left + x][chamber_top + y_divide].update(nodetype='wall')
                draw_square(chamber_left + x, chamber_top + y_divide)
                if visualise:
                    update_square(chamber_left + x, chamber_top + y_divide)
                    time.sleep(sleep_walls)

        if chamber_width < 3 and chamber_height < 3:
            return

        top_left =      (chamber_left,                  chamber_top,                x_divide,                       y_divide)
        top_right =     (chamber_left + x_divide + 1,   chamber_top,                chamber_width - x_divide - 1,   y_divide)
        bottom_left =   (chamber_left,                  chamber_top + y_divide + 1, x_divide,                       chamber_height - y_divide - 1)
        bottom_right =  (chamber_left + x_divide + 1,   chamber_top + y_divide + 1, chamber_width - x_divide - 1,   chamber_height - y_divide - 1)

        chambers = (top_left, top_right, bottom_left, bottom_right)
                
        left =      (chamber_left,                     chamber_top + y_divide,      x_divide,                       1)
        right =     (chamber_left + x_divide + 1,      chamber_top + y_divide,      chamber_width - x_divide - 1,   1)
        top =       (chamber_left + x_divide,          chamber_top,                 1,                              y_divide)
        bottom =    (chamber_left + x_divide,          chamber_top + y_divide + 1,  1,                              chamber_height - y_divide - 1)
        
        walls = (left, right, top, bottom)

        gaps = 3
        for wall in random.sample(walls, gaps):
            if wall[3] == 1:
                x = random.randrange(wall[0],wall[0]+wall[2])
                y = wall[1]
                if x in gaps_to_offset and y in gaps_to_offset:
                    if wall[2] == x_divide:
                        x -= 1
                    else:
                        x += 1
                if x >= ROWS:
                    x = ROWS -1
            else: 
                x = wall[0]
                y = random.randrange(wall[1],wall[1]+wall[3])
                if y in gaps_to_offset and x in gaps_to_offset:
                    if wall[3] == y_divide:
                        y -=1
                    else:
                        y += 1
                if y >= ROWS:
                    y = ROWS-1
            grid[x][y].update(nodetype="blank")
            draw_square(x, y)
            if visualise:
                update_square(x, y)
                time.sleep(sleep)

        for num, chamber in enumerate(chambers):
            recursive_division(chamber)

    def dijkstra(mazearray, start_point=(0,0), goal_node=False, display=pygame.display, visualise=VISUALISE, diagonals=DIAGONALS, astar=False):

        heuristic = 0
        distance = 0

        n = len(mazearray) - 1
        
        visited_nodes = set()
        unvisited_nodes = set([(x,y) for x in range(n+1) for y in range(n+1)])
        queue = AStarQueue()

        queue.push(distance+heuristic, distance, start_point)
        v_distances = {}

        if not goal_node:
            goal_node = (n,n)
        priority, current_distance, current_node = queue.pop()
        start = time.perf_counter()
        
        while current_node != goal_node and len(unvisited_nodes) > 0:
            if current_node in visited_nodes:
                if len(queue.show()) == 0:
                    return False
                else:
                    priority, current_distance, current_node = queue.pop()
                    continue
            
            for neighbour in get_neighbours(current_node, n, diagonals=diagonals):
                neighbours_loop(
                    neighbour, 
                    mazearr=mazearray, 
                    visited_nodes=visited_nodes, 
                    unvisited_nodes=unvisited_nodes, 
                    queue=queue, 
                    v_distances=v_distances, 
                    current_node=current_node,
                    current_distance=current_distance,
                    astar=astar
                )

            visited_nodes.add(current_node)
            unvisited_nodes.discard(current_node)
            
            v_distances[current_node] = current_distance

            if (current_node[0],current_node[1]) != start_point:
                mazearray[current_node[0]][current_node[1]].update(is_visited = True)
                draw_square(current_node[0],current_node[1],grid=mazearray)

                if visualise:
                    update_square(current_node[0],current_node[1])
                    time.sleep(0.000001)
            
            if len(queue.show()) == 0:
                return False
            else:
                priority, current_distance, current_node = queue.pop()
        
        v_distances[goal_node] = current_distance + (1 if not diagonals else 2**0.5)
        visited_nodes.add(goal_node)

        trace_back(goal_node, start_point, v_distances, visited_nodes, n, mazearray, diags=diagonals, visualise=visualise)

        end = time.perf_counter()
        num_visited = len(visited_nodes)
        time_taken = end-start

        print(f"Program finished in {time_taken:.4f} seconds after checking {num_visited} nodes. That is {time_taken/num_visited:.8f} seconds per node.")
        
        return False if v_distances[goal_node] == float('inf') else True

    def neighbours_loop(neighbour, mazearr, visited_nodes, unvisited_nodes, queue, v_distances, current_node, current_distance, diags=DIAGONALS, astar=False):
        neighbour, ntype = neighbour
        heuristic = 0

        if astar:
            heuristic += abs(END_POINT[0] - neighbour[0]) + abs(END_POINT[1] - neighbour[1])
            heuristic *= 1
         
        if neighbour in visited_nodes:
            pass
        elif mazearr[neighbour[0]][neighbour[1]].nodetype == 'wall':
            visited_nodes.add(neighbour)
            unvisited_nodes.discard(neighbour)
        else:
            modifier = mazearr[neighbour[0]][neighbour[1]].distance_modifier
            if ntype == "+":
                queue.push(current_distance+(1*modifier)+heuristic, current_distance+(1*modifier), neighbour)
            elif ntype == "x": 
                queue.push(current_distance+((2**0.5)*modifier)+heuristic, current_distance+((2**0.5)*modifier), neighbour)

    def trace_back(goal_node, start_node, v_distances, visited_nodes, n, mazearray, diags=False, visualise=VISUALISE):
        path = [goal_node]
        current_node = goal_node
        
        while current_node != start_node:
            neighbour_distances = PriorityQueue()
            neighbours = get_neighbours(current_node, n, diags)
            try:
                distance = v_distances[current_node]
            except Exception as e:
                print(e)

            for neighbour, ntype in neighbours:
                if neighbour in v_distances:
                    distance = v_distances[neighbour]
                    neighbour_distances.push(distance, neighbour)
            
            distance, smallest_neighbour = neighbour_distances.pop()
            mazearray[smallest_neighbour[0]][smallest_neighbour[1]].update(is_path=True)
            draw_square(smallest_neighbour[0],smallest_neighbour[1],grid=mazearray)
            path.append(smallest_neighbour)
            current_node = smallest_neighbour

        pygame.display.flip()
        mazearray[start_node[0]][start_node[1]].update(is_path=True)

    def xfs(mazearray, start_point, goal_node, x, display=pygame.display, visualise=VISUALISE, diagonals=DIAGONALS):
        assert x == 'b' or x == 'd', "x should equal 'b' or 'd' to make this bfs or dfs"
        n = len(mazearray) - 1
        mydeque = deque()
        mydeque.append(start_point)
        visited_nodes = set([])
        path_dict = {start_point: None}

        while len(mydeque) > 0:
            if x == 'd':
                current_node = mydeque.pop()
            elif x == 'b':
                current_node = mydeque.popleft()
          
            if current_node == goal_node:
                path_node = goal_node
                while True:
                    path_node = path_dict[path_node]
                    mazearray[path_node[0]][path_node[1]].update(is_path = True)
                    draw_square(path_node[0],path_node[1],grid=mazearray)
                    if visualise:
                        update_square(path_node[0],path_node[1])
                    if path_node == start_point:
                        return True
            
            if mazearray[current_node[0]][current_node[1]].nodetype == 'wall':
                continue
            
            if current_node not in visited_nodes:
                visited_nodes.add(current_node)
                mazearray[current_node[0]][current_node[1]].update(is_visited = True)
                draw_square(current_node[0],current_node[1],grid=mazearray)
                if visualise:
                    update_square(current_node[0],current_node[1])
                    time.sleep(0.001)
                
                for neighbour, ntype in get_neighbours(current_node, n):
                    mydeque.append(neighbour)
                    if neighbour not in visited_nodes:
                        path_dict[neighbour] = current_node
        
        pygame.display.flip()
        return False

    grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
    grid[END_POINT[0]][END_POINT[1]].update(nodetype='end')

    def update_gui(draw_background=True, draw_buttons=True, draw_grid=True):
        
        if draw_background:
            screen.fill(BLACK)
            pass

        if draw_buttons:
            visToggleButton = Button(GREY, SCREEN_WIDTH/3, SCREEN_WIDTH + BUTTON_HEIGHT*2, SCREEN_WIDTH/3, BUTTON_HEIGHT, f"Visualise: {str(VISUALISE)}")
            dijkstraButton.draw(screen, (0,0,0))
            dfsButton.draw(screen, (0,0,0))
            bfsButton.draw(screen, (0,0,0))
            astarButton.draw(screen, (0,0,0))
            resetButton.draw(screen, (0,0,0))
            mazeButton.draw(screen, (0,0,0))
            altPrimButton.draw(screen, (0,0,0))
            recursiveMazeButton.draw(screen, (0,0,0))
            terrainButton.draw(screen, (0,0,0))
            visToggleButton.draw(screen, (0,0,0))

        if draw_grid:
            for row in range(ROWS):
                for column in range(ROWS):
                    color = grid[row][column].color
                    draw_square(row,column)

    update_gui()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()