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

"""
*************************************
Of 20 initial problems, 9 were solved in less than 2 seconds by this solver.
Of the 9 problems that were solved, the cost of 9 matched or outperformed the benchmark.
Problems that remain unsolved in the set are Problems: [5, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19]
The manhattan distance implementation solved 7 out of the 20 practice problems given 2 seconds.
The better implementation solved 14 out of the 20 practice problems given 2 seconds.
*************************************


"""

def heur_alternate(state):
#IMPLEMENT
    '''a better sokoban heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''        
    #heur_manhattan_distance has flaws.   
    #Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    #Your function should return a numeric value for the estimate of the distance to the goal.


    val = 0

    box_on_right = False
    box_on_left = False
    box_on_up = False
    box_on_down = False

    stor_on_right = False
    stor_on_left = False
    stor_on_up = False
    stor_on_down = False


    for box_x, box_y in state.boxes:
        # If a box is in a corner, it's in a state that can't get to the goal, so return inf
        if box_x == 0 and box_y == 0 and (box_x, box_y) not in state.storage:
            return float('inf')
        if box_x == 0 and box_y == state.height and (box_x, box_y) not in state.storage:
            return float('inf')
        if box_x == state.width and box_y == 0 and (box_x, box_y) not in state.storage:
            return float('inf')
        if box_x == state.width and state.height and (box_x, box_y) not in state.storage:
            return float('inf')


        # Checking if a box is on one of the walls
        if box_x == 0:
            box_on_left = True
        if box_x == state.width:
            box_on_right = True
        if box_y == 0:
            box_on_up = True
        if box_y == state.height:
            box_on_down = True
        
        # Manhattan distance between boxes and storages
        min_distance = float('inf')
        for stor_x, stor_y in state.storage:
            if stor_x == 0:
                stor_on_left = True
            if stor_x == state.width:
                stor_on_right = True
            if stor_y == 0:
                stor_on_up = True
            if stor_y == state.height:
                stor_on_down = True
            distance = abs(box_x - stor_x) + abs(box_y - stor_y)
            if distance < min_distance:
                min_distance = distance
        val += min_distance

        # If a box is on a wall, but there isn't a storage on that wall, return inf
        if (box_on_down and not stor_on_down) or (box_on_left and not stor_on_left) or (box_on_right and not stor_on_right) or (box_on_up and not stor_on_up):
            return float('inf')        

    # Add Manhattan distance between boxes to storages and robots to boxes
    return val + dist_robot_to_box(state)

def dist_robot_to_box(state):

    val = 0
    for robot_x, robot_y in state.robots:
        min_distance = float('inf')
        for box_x, box_y in state.boxes:
            distance = abs(robot_x - box_x) + abs(robot_y - box_y)
            if distance < min_distance:
                min_distance = distance
        val += min_distance
    return val 

def box_beside_obstace(state):
    val = 0

    for box in state.boxes:
        if( (box[0]+1, box[1]) in state.obstacles):
            #print("beside ob1")
            val += 1
        if( (box[0]-1, box[1]) in state.obstacles):
            #print("beside ob2")
            val += 1
        if( (box[0], box[1]+1) in state.obstacles):
            #print("beside ob3")
            val += 1
        if( (box[0]-1, box[1]-1) in state.obstacles):
            #print("beside ob4")
            val += 1


    return val

def dist_box_to_obstancle(state):

    val = 0
    for box_x, box_y in state.boxes:
        min_distance = float('inf')
        for ob_x, ob_y in state.obstacles:
            distance = abs(box_x - ob_x) + abs(box_y - ob_y)
            if distance < min_distance:
                min_distance = distance
        val += min_distance
    return val 

def dist_robot_to_obstancle(state):

    val = 0
    for robot_x, robot_y in state.robots:
        min_distance = float('inf')
        for ob_x, ob_y in state.obstacles:
            distance = abs(robot_x - ob_x) + abs(robot_y - ob_y)
            if distance < min_distance:
                min_distance = distance
        val += min_distance
    return val 

def stuck(state):

    box_on_right = False
    box_on_left = False
    box_on_up = False
    box_on_down = False

    stor_on_right = False
    stor_on_left = False
    stor_on_up = False
    stor_on_down = False

    for box_x, box_y in state.boxes:
        if box_x == 0 and box_y == 0 and (box_x, box_y) not in state.storage:
            return True
        if box_x == 0 and box_y == state.height and (box_x, box_y) not in state.storage:
            return True
        if box_x == state.width and box_y == 0 and (box_x, box_y) not in state.storage:
            return True
        if box_x == state.width and state.height and (box_x, box_y) not in state.storage:
            return True


        if box_x == 0:
            box_on_left = True
        if box_x == state.width:
            box_on_right = True
        if box_y == 0:
            box_on_up = True
        if box_y == state.height:
            box_on_down = True

        for stor_x, stor_y in state.storage:
            if stor_x == 0:
                stor_on_left = True
            if stor_x == state.width:
                stor_on_right = True
            if stor_y == 0:
                stor_on_up = True
            if stor_y == state.height:
                stor_on_down = True


    return (box_on_down and not stor_on_down) or (box_on_left and not stor_on_left) or (box_on_right and not stor_on_right) or (box_on_left and not stor_on_left)


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
    val = 0
    for box_x, box_y in state.boxes:
        min_distance = float('inf')
        for stor_x, stor_y in state.storage:
            distance = abs(box_x - stor_x) + abs(box_y - stor_y)
            if distance < min_distance:
                min_distance = distance
        val += min_distance

    return val  # CHANGE THIS

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + weight * sN.hval #CHANGE THIS

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''

    se = SearchEngine('custom')
    wrapped_fval_function = (lambda sN : fval_function(sN, weight)) 

    se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=wrapped_fval_function)
    state, stats = se.search(timebound=timebound)

    if(state == False):
        return False, stats


    return state, stats  # CHANGE THIS



def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''


    first_iter = True

    se = SearchEngine('custom')
    wrapped_fval_function = (lambda sN : fval_function(sN, weight)) 

    se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=wrapped_fval_function)

    opt_state = -1
    cur_state = -1
    stats = -1
    opt_costbound = float('inf')
    cur_costbound = -1
    next_min = float('inf')

    while(timebound > 0):
        if first_iter:
            #print("a")

            opt_state, stats = se.search(timebound=timebound,  costbound=(float('inf'), float('inf'), float('inf')))
            cur_state = opt_state

            if opt_state != False:
                opt_costbound = opt_state.gval + heur_fn(opt_state)
                cur_costbound = opt_costbound

            first_iter = False

        else:

            cur_state, stats = se.search(timebound=timebound, costbound=(float('inf'), float('inf'), opt_costbound))

            if(cur_state != False):
                cur_costbound = cur_state.gval + heur_fn(cur_state)
                if(cur_costbound < opt_costbound):
                    opt_state = cur_state
                    opt_costbound = cur_costbound
                else:
                    if(cur_costbound < next_min):
                        next_min = cur_costbound

            else:
                opt_costbound = next_min

     
        timebound -= os.times()[0] - se.search_start_time
        weight -= 0.75


    return opt_state, stats #CHANGE THIS

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''

    first_iter = True

    se = SearchEngine('best_first')

    se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn)

    opt_state = -1
    cur_state = -1
    stats = -1
    opt_costbound = -1
    cur_costbound = -1

    while(timebound > 0):
        if first_iter:
            opt_state, stats = se.search(timebound=timebound)
            cur_state = opt_state

            if opt_state != False:
                opt_costbound = opt_state.gval + heur_fn(opt_state)
                cur_costbound = opt_costbound

            first_iter = False
        else:
            cur_state, stats = se.search(timebound=timebound, costbound=(opt_costbound, float('inf'), float('inf')))

            if(cur_state != False):
                cur_costbound = cur_state.gval
                if(cur_costbound <= opt_costbound):
                    opt_state = cur_state
                    opt_costbound = cur_costbound


        
        timebound -= os.times()[0] - se.search_start_time



    return opt_state, stats



