#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

# SOKOBAN HEURISTICS
def heur_alternate(state):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.

    '''This heuristics function uses multiple modifications on the manhattan distance. Each modification
    will be explained in it's code part'''
    width = state.width
    height = state.height
    
    '''Doom map'''
    '''mark locations where if a box existed, the puzzle becomes unsolvable.
    Any location where a box is blocked on atleast 1 side from both horizontal
    and vertical directions'''
    obstacleMap = [[0]*(height+2) for _ in range(width+2)] #map to represent the board
    doomMap = [[0]*(height) for _ in range(width)] #map to mark doom location
    #mark Obstacles
    for obstacle in state.obstacles:                                  
        obstacleMap[obstacle[0]+1][obstacle[1]+1] = 1
    #mark Boxes
    for box in state.boxes:     
        obstacleMap[box[0]+1][box[1]+1] = 2
    #mark Walls
    obstacleMap[0] = [1]*(height+2)     
    obstacleMap[width+1]= [1]*(height+2)
    for i in range(width+2): 
        obstacleMap[i][0]= 1
        obstacleMap[i][height+1]= 1
    '''Check normal obstacle blocking'''
    '''a value of 1 will mean blocked in vertical direction
    a value of 2 will mean block in horizontal direction
    The are cummulative, so 3 will mean blocked in both directions'''
    for i in range(width):
        for j in range(height):
            if (obstacleMap[i+1][j] == 1 or obstacleMap[i+1][j+2] == 1):
                doomMap[i][j] += 1
            if (obstacleMap[i][j+1] == 1 or obstacleMap[i+2][j+1] == 1):
                doomMap[i][j] += 2
    '''check boxes blocking eachother'''
    '''If a box b is blocked in 1 direction by an obstacle, and another direction
    by another box c, then block b cannot move until block c is moved, so it counts
    as an obstical for the purposes of doomed'''
    for i in range(width):
        for j in range(height):
            vertical = False
            horizontal = False
            if ((obstacleMap[i+1][j] == 2) and (doomMap[i][j-1] >= 2)):
                    vertical = True
            if ((obstacleMap[i+1][j+2] == 2) and (doomMap[i][j+1] >= 2)):
                    vertical = True
            if ((obstacleMap[i][j+1] == 2) and (doomMap[i-1][j] == 1 or doomMap[i-1][j] == 3)):
                    horizontal = True
            if ((obstacleMap[i+2][j+1] == 2) and (doomMap[i+1][j] == 1 or doomMap[i+1][j] == 3)):
                    horizontal = True
            if (vertical):
                doomMap[i][j] += 1
            if (horizontal):
                doomMap[i][j] += 2
    '''Manhatten distance modifications'''
    '''Same distance as Manhatten distance, but each storage can only be assigned to
    one box.Use findMin() recursive function to find box storage associations with
    smallest total path'''
    '''boxStorage = {}''' #list of paths and distances
    boxStorage = [[0]*(len(state.storage)) for _ in range(len(state.boxes))]
    boxcount = 0
    for box in state.boxes:
        storagecount = 0
        for storage in state.storage:
            cost = abs(box[0]-storage[0])+abs(box[1]-storage[1]) #Normal manhattan distance
            # Check if placing box in this location is a doomed state
            if (doomMap[box[0]][box[1]] == 3 and 0 != cost):
                cost = math.inf
            else:
                '''If a box is on an edge, and the storage is not on the same edge, it's impossible
                for that box to reach that storage location'''
                '''If any objects are blocking the way of the box thats on an edge, it is also
                impossible for that box to reach the storage'''
                if (box[0] == 0 or box[0] == width-1):
                    if (storage[0] != box[0]):
                        cost = math.inf
                    else:
                        a = min(box[1], storage[1])
                        b = max(box[1], storage[1])
                        for i in range(a+1,b):
                            if (obstacleMap[box[0]+1][i+1] > 0):
                                cost = math.inf
                if (box[1] == 0 or box[1] == height-1):
                    if (storage[1] != box[1]):
                       cost = math.inf
                    else:
                        a = min(box[0], storage[0])
                        b = max(box[0], storage[0])
                        for i in range(a+1,b):
                            if (obstacleMap[i+1][box[1]+1] > 0):
                                cost = math.inf
            boxStorage[boxcount][storagecount] = cost
            storagecount += 1
        boxcount += 1
    leftlist = list(range(0,len(state.boxes)))
    return findMin(boxStorage,leftlist)

'''Finds smallest combination of boxes and storage'''
def findMin(matrix, left):
    if (len(left) == 1):
        return matrix[0][left[0]]
    smallest = math.inf
    newMatrix = matrix[1:]
    for i in left:
        newLeft = left.copy()
        newLeft.remove(i)
        if (matrix[0][i] != math.inf):
            smallest = min(matrix[0][i] + findMin(newMatrix, newLeft), smallest)
    return smallest

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def heur_manhattan_distance(state):
    # IMPLEMENT
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must never overestimate the cost to get from the current state to the goal.
    # The sum of the Manhattan distances between each box that has yet to be stored and the storage point nearest to it is such a heuristic.
    # When calculating distances, assume there are no obstacles on the grid.
    # You should implement this heuristic function exactly, even if it is tempting to improve it.
    # Your function should return a numeric value; this is the estimate of the distance to the goal.
    manDist = 0
    for box in state.boxes:
        shortestDist = math.inf
        for storage in state.storage:
            dist = abs(box[0]-storage[0])+abs(box[1]-storage[1])
            if (shortestDist > dist):
                shortestDist = dist
        manDist += shortestDist
    return manDist 

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + weight*sN.hval

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 
    was = SearchEngine('custom', 'default')
    was.init_search(initState = initial_state,goal_fn=sokoban_goal_state,heur_fn = heur_fn, fval_function = wrapped_fval_function)
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    return was.search(timebound = timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    weight = 30
    timeleft = timebound
    costmax = (math.inf,math.inf,math.inf)
    final = False
    stats = None
    out = (final, stats)
    was = SearchEngine('custom', 'default')
    while timeleft > 0:
        was.init_search(initState = initial_state, goal_fn = sokoban_goal_state,heur_fn = heur_fn, fval_function = (lambda sN : fval_function(sN,weight)))
        final, stats = was.search(timebound = timeleft, costbound = costmax)
        if final:
            out = (final, stats)
            costmax = (final.gval,final.gval,final.gval)
            weight = max(1,weight//10)
            timeleft = timeleft - stats.total_time
        else:
            timeleft = 0
    return out

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    timeleft = timebound
    costmax = (math.inf,math.inf,math.inf)
    final = False
    stats = None
    out = (final, stats)
    was = SearchEngine('best_first', 'default')
    while timeleft > 0:
        was.init_search(initState = initial_state, goal_fn = sokoban_goal_state,heur_fn = heur_fn, fval_function = (lambda sN : fval_function(sN,weight)))
        final, stats = was.search(timebound = timeleft, costbound = costmax)
        if final:
            out = (final, stats)
            costmax = (final.gval,math.inf,math.inf)
            timeleft = timeleft - stats.total_time
        else:
            timeleft = 0
    return out


