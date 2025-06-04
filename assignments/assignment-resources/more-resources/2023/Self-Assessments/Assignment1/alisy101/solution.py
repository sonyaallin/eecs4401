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
    storeset = set(state.storage) 
    fsum = 0    
    upwall = set()
    leftwall = set()
    downwall = set()
    rightwall = set()
    for i in range(0, state.height): 
        leftwall.add((0, i))
        rightwall.add((state.width-1, i))
    for y in range(0, state.width):
        upwall.add((y, 0))
        downwall.add((y, state.height-1))
    walls = [upwall, leftwall, downwall, rightwall] #all coordinates along wall. Used to check wall edge cases
    for box in state.boxes: 
        up = (box[0], box[1]-1)
        down = (box[0], box[1]+1)
        left = (box[0]-1, box[1])  #getting all coords around each box
        right = (box[0]+1, box[1])
        topright = (box[0]+1, box[1]-1)
        topleft = (box[0]-1, box[1]-1)
        bottomleft = (box[0]-1, box[1]+1)
        bottomright = (box[1]+1, box[1]+1)
        if (box not in state.storage):
            if ((up in state.obstacles or down in state.obstacles or up[1] < 0 or down[1] >= state.height)
             and (left in state.obstacles or right in state.obstacles or left[0]<0 or right[0]>=state.width)): #Edge cases such as getting the boxes stuck in corners or between obstacles
                return float('inf')
        
        if (box not in state.storage) and check_stuck(box, walls, state.storage, state.obstacles, state.boxes):
            #this function checks if a box is along a wall. If so, it then checks if that wall has a storage. If not
            #then this is a bad state and we return infinity. If there is a storage it then checks if the storage 
            # and box have an obstacle in between them. If so, its a bad state and we return infinity. 
            return float('inf')
        if (box not in state.storage):
            if (((up in state.boxes or up in state.obstacles or up[1] < 0) and
             (topright in state.boxes or topright in state.obstacles or topright[1] < 0 or topright[0] >= state.width )
              and (left in state.boxes or left in state.obstacles or left[0] < 0))  or ((left in state.boxes or left in state.obstacles or left[0] < 0) and (up in state.boxes or up in state.obstacles or up[1]<0) and
               (topleft in state.boxes or topleft in state.obstacles or topleft[1]<0 or topleft[0]<0)) or ((left in state.boxes or left in state.obstacles or left[0] < 0) and (down in state.boxes or down in state.obstacles or down[1] >= state.height) and
                (bottomleft in state.boxes or bottomleft in state.obstacles or bottomleft[1] >= state.height or bottomleft[1] < 0)) or ((down in state.boxes or down in state.obstacles or down[1]>=state.height) and (right in state.boxes or right in state.obstacles or right[0]>=state.width) and
                 (bottomright in state.boxes or bottomright in state.obstacles or bottomright[1]>=state.height or bottomright[0]>=state.width))):
                 #checks if theres a square of boxes/obstacles/walls with the current box we are iterating on. If so this is a bad state and we return infinity.
                return float('inf')


        curmhd = float('inf')
        toremove = None
        for store in storeset: #check distance from box to closest storage
            mhd = (abs(box[0] - store[0])) + (abs(box[1] - store[1]))
            if mhd < curmhd:
                curmhd = mhd
                toremove = store  
        storeset.remove(toremove) #One box per storage
        fsum += curmhd

    for box in state.boxes: #check distance from boxes to robots
        currmhd = float('inf')
        for robot in state.robots:
            mhd2 = (abs(robot[0] - box[0])) + (abs(robot[1] - box[1]))
            if mhd2 <= currmhd:
                currmhd = mhd2
        fsum += currmhd 
    return fsum

def obstacleinway(box, storage, obstacles, dir, boxes): #checks for obstacle between storage and box
    otherboxes = boxes.difference(set([box]))
    if storage in otherboxes:  #if another box has already taken the storage, then we cant put this box on that storage.
        return float('inf')
    while box != storage:
        if dir == 'up':
            box = (box[0], box[1] - 1)
        elif dir == 'down':
            box = (box[0], box[1] + 1)
        elif dir == 'left':
            box = (box[0]-1, box[1])
        elif dir == 'right':
            box = (box[0]+1, box[1])
        if box in obstacles:
            return float('inf')
    
    return 0


def check_stuck(box, walls, storages, obstacles, boxes):
    check = float('inf')
    if (box in walls[1]): #Edge case, if a box is right beside a wall, the only way
        #it can reach a storage is if the storage is also beside that wall. (given there are no obstacles)
        wallstorages = walls[1].intersection(storages)
        if len(wallstorages) == 0:
            return float('inf')
        else:
            for storage in wallstorages:
                if storage[1] > box[1]:
                    check *= obstacleinway(box, storage, obstacles, 'down', boxes)
                else:
                    check *= obstacleinway(box, storage, obstacles, 'up', boxes)
            if (check == float('inf')):
                return check
    if (box in walls[3]):
        wallstorages = walls[3].intersection(storages)
        if len(wallstorages) == 0:
            return float('inf')
        else:
            for storage in wallstorages:
                if storage[1] > box[1]:
                    check *= obstacleinway(box, storage, obstacles, 'down', boxes)
                else:
                    check *= obstacleinway(box, storage, obstacles, 'up', boxes)
            if (check == float('inf')):
                return check
    if (box in walls[0]):
        wallstorages = walls[0].intersection(storages)
        if len(wallstorages) == 0:
            return float('inf')
        else:
            for storage in wallstorages:
                if storage[0] > box[0]:
                    check *= obstacleinway(box, storage, obstacles, 'right', boxes)
                else:
                    check *= obstacleinway(box, storage, obstacles, 'left', boxes)
            if (check==float('inf')):
                return check
    if (box in walls[2]):
        wallstorages = walls[2].intersection(storages)
        if len(wallstorages) == 0:
            return float('inf')
        else:
            for storage in wallstorages:
                if storage[0] > box[0]:
                    check *= obstacleinway(box, storage, obstacles, 'right', boxes)
                else:
                    check *= obstacleinway(box, storage, obstacles, 'left', boxes)
            if (check==float('inf')):
                return check

    return 0
     # CHANGE THIS

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
    fsum = 0   
    for box in state.boxes:
        curmhd = float('inf')
        for store in state.storage:
            mhd = (abs(box[0] - store[0])) + (abs(box[1] - store[1]))
            if mhd < curmhd:
                curmhd = mhd
        fsum += curmhd
    return fsum


def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + (weight * sN.hval)

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    wrapped_fval_function = (lambda sN : fval_function(sN,weight))
    se = SearchEngine('custom')
    se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    return se.search(timebound=timebound)
    return None, None  # CHANGE THIS

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    w = 10
    costbound = (float('inf'), float('inf'), float('inf'))
    answer = (False, None)
    prev = (False, None)
    while timebound > 0:
        prev = answer
        wrapped_fval_function = (lambda sN : fval_function(sN,w))
        se = SearchEngine('custom', cc_level="full")
        se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
        answer = se.search(timebound=timebound, costbound=costbound)
        if answer[0]:
            hval = heur_fn(answer[0])
            costbound = (float('inf'), float('inf'), answer[0].gval + hval)
            w = w//2
            if (w < 1):
                w = 1
            timebound -= answer[1].total_time
        else:
            return prev
    

        
    
    return answer #CHANGE THIS

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    costbound = (float('inf'), float('inf'), float('inf'))
    answer = (False, None)
    prev = (False, None)
    se = SearchEngine('best_first', cc_level="full")
    se.init_search(initial_state, sokoban_goal_state, heur_fn)
    while timebound > 0:
        prev = answer
        answer = se.search(timebound=timebound, costbound=costbound)
        if answer[0]:
            costbound = (answer[0].gval, float('inf'), float('inf'))
            timebound -= answer[1].total_time
        else:
            return prev
    

        
    
    return answer #CHANGE THIS



