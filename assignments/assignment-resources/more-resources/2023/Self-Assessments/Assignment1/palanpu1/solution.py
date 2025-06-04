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
    # return 0  # CHANGE THIS

    estimate = 0

    boxes = set(state.boxes)
    obstacles = set(state.obstacles)
    storages = set(state.storage)
    robots = set(state.robots)
    height = state.height
    width = state.width

    # Description of heuristic: This heuristic is simply the manhattan heuristic with a few improvements in terms of
    # impossible to solve scenarios and improved storage distance calculations with along with taking into account bot
    # movements. The changes and explanations are listed in detail below:

    # (1) The first area of improvement is to check when boxes are stuck so we don't waste time going down that route
    # If there is a box that is stuck in a corner between map walls or obstacles, in these 4 scenarios
    # it would be impossible to finish the map unless the box was already in a storage
    # (i.e north and east, east and south, south and west, west and north)
    # So, we can check for these 4 scenarios (assuming the box is not stored)
    #
    # (i) #    (ii)  #   (iii) $#   (iv) #$
    #     $#        #$         #          #
    #
    # where # would represent an obstacle or a wall

    # (2) Another area to check for stuck unstored boxes are if they are up against a wall, and that wall
    # does not have a storage point along it, then we can automatically eliminate that possibility since
    # the box will never reach a storage
    #
    # (i) ########    (iii) ##   (iv) ##
    #     #  $   #           #        #
    #                       $#        #$
    # (ii) #   $  #          #        #
    #      ########         ##        ##
    #

    # (3) There could possibly be overhead work in terms of moves required if a bots spawn point is far away from
    # a box of interest and so, we should take into account the number of moves it would take for the bot to reach the
    # box before it can actually interact with it. Since a bot cannot be on the same tile as a box though, we will
    # consider the work as the manhattan distance between the unstored box and the nearest bot - 1.

    # (4) Since only one box can fit per storage, once we find a free storage via minimum manhattan distance for a box,
    # we remove that storage from the list of storages that other boxes should look at to get their closest storage.
    # This way, multiple boxes cannot have the same targeted storage since it does not make sense for them.

    for box in boxes:
        if box not in storages: # calculating positions NESW of box
            north = (box[0], box[1] - 1)
            east = (box[0] + 1, box[1])
            south = (box[0], box[1] + 1)
            west = (box[0] - 1, box[1])

            # check directional pairs to make sure box is not stuck in some sort of corner, whether it be of
            # the map boundaries or obstacle tiles
            # Cases 1 (i), (ii), (iii), (iv)
            if ((north in obstacles) or (north[1] < 0)) and ((east in obstacles) or (east[0] > width - 1)):
                return math.inf
            elif ((east in obstacles) or (east[0] > width - 1)) and ((south in obstacles) or (south[1] > height - 1)):
                return math.inf
            elif ((south in obstacles) or (south[1] > height - 1)) and ((west in obstacles) or (west[0] < 0)):
                return math.inf
            elif ((west in obstacles) or (west[0] < 0)) and ((north in obstacles) or (north[1] < 0)):
                return math.inf

            # likewise, if a box is against a wall but that wall does not have a storage, then we are also stuck
            # because the box cannot be moved into the map away from the wall, otherwise the bot would somehow be
            # out of the map
            # Cases 2 (i), (ii), (iii), (iv)
            if north[1] < 0:
                possibleStorage = False
                for storage in storages:
                    if storage not in boxes and storage[1] == box[1]:
                        possibleStorage = True
                if possibleStorage == False:
                    return math.inf

            if south[1] > height - 1:
                possibleStorage = False
                for storage in storages:
                    if storage not in boxes and storage[1] == box[1]:
                        possibleStorage = True
                if possibleStorage == False:
                    return math.inf

            if east[0] > width - 1:
                possibleStorage = False
                for storage in storages:
                    if storage not in boxes and storage[0] == box[0]:
                        possibleStorage = True
                if possibleStorage == False:
                    return math.inf

            if west[0] < 0:
                possibleStorage = False
                for storage in storages:
                    if storage not in boxes and storage[0] == box[0]:
                        possibleStorage = True
                if possibleStorage == False:
                    return math.inf

            # once the stuck checks are done, lets try and get a robot distance estimate for the unstored boxes
            # implementation of (3)
            closestDist = math.inf
            for bot in robots:
                xMoves = box[0] - bot[0]
                yMoves = box[1] - bot[1]
                # must subtract 1 because a bot moves the box at a distance of 1 away from it, and a bot cannot share
                # a tile with the box itself
                botDist = abs(xMoves) + abs(yMoves) - 1
                if botDist < closestDist:
                    closestDist = botDist
            estimate += closestDist



    for boxpos in boxes:
        if boxpos in storages:
            storages.remove(boxpos)
        elif boxpos not in storages:  # ignore boxes already stored
            singledist = math.inf
            closestStorage = (math.inf, math.inf)
            for storagepos in storages:
                if storagepos not in boxes:  # ignore storages already boxed
                    xdist = storagepos[0] - boxpos[0]
                    ydist = storagepos[1] - boxpos[1]
                    distanceOfBox = abs(xdist) + abs(ydist)
                    if distanceOfBox < singledist:
                        closestStorage = storagepos
                        singledist = distanceOfBox
            # we remove the storage we found for this box, so another box does not attempt to pick this storage again
            # incorporation of (4)
            storages.remove(closestStorage)
            estimate += singledist

    return estimate

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
    # return 0  # CHANGE THIS

    estimate = 0

    # for each box not in a spot already find the shortest manhattan distance storage point and sum it
    for boxpos in state.boxes:
        if boxpos not in state.storage: # ignore boxes already stored
            singledist = math.inf
            for storagepos in state.storage:
                if storagepos not in state.boxes: # ignore storages already boxed
                    xdist = storagepos[0] - boxpos[0]
                    ydist = storagepos[1] - boxpos[1]
                    singledist = min(singledist, abs(xdist) + abs(ydist))
            estimate += singledist

    return estimate


def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    # from assignment page: f(node) = g(node) + w * h(node)
    return sN.gval + weight * sN.hval

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    # return None, None  # CHANGE THIS

    # from assignment page
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    customEngine = SearchEngine(strategy='custom', cc_level='full')
    customEngine.init_search(initState=initial_state, heur_fn=heur_fn, goal_fn=sokoban_goal_state,
                             fval_function=wrapped_fval_function)
    searchResults = customEngine.search(timebound)
    # search results are already formatted as needed from the search return
    return searchResults


def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    timeStarted = os.times()[0]

    # First search iteration
    customEngine = SearchEngine(strategy='custom', cc_level='full')
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    customEngine.init_search(initState=initial_state, heur_fn=heur_fn, goal_fn=sokoban_goal_state,
                             fval_function=wrapped_fval_function)
    customEngine.search(timeStarted + timebound - os.times()[0], (math.inf, math.inf, math.inf))

    result, stats = customEngine.search(timeStarted + timebound - os.times()[0], (math.inf, math.inf, math.inf))
    if not result:
        return result, stats

    price = result.gval
    newCost = (result.gval, result.gval, result.gval)

    # In subsequent iterations, look at generated node values g + h and check if its more than the existing cost
    # Also decrease weight
    while timeStarted + timebound > os.times()[0]:
        weight = weight*0.9
        newResult, newStats = customEngine.search(timeStarted + timebound - os.times()[0], newCost)
        if newResult:
            newPrice = newResult.gval + heur_fn(newResult)
            if newPrice < price:
                newCost = (newPrice, newPrice, newPrice)
                result, stats = newResult, newStats
                price = newPrice

    return result, stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    # return None, None #CHANGE THIS

    timeStarted = os.times()[0]

    # First search iteration
    customEngine = SearchEngine(strategy='best_first', cc_level='full')

    customEngine.init_search(initState=initial_state, heur_fn=heur_fn, goal_fn=sokoban_goal_state)
    customEngine.search(timeStarted + timebound - os.times()[0], (math.inf, math.inf, math.inf))

    result, stats = customEngine.search(timeStarted + timebound - os.times()[0], (math.inf, math.inf, math.inf))
    if not result:
        return result, stats

    price = result.gval
    newCost = (result.gval, result.gval, result.gval)

    while timeStarted + timebound > os.times()[0]:

        newResult, newStats = customEngine.search(timeStarted + timebound - os.times()[0], newCost)
        if newResult and newResult.gval < price:
            newCost = (newResult.gval, newResult.gval, newResult.gval)
            price = newResult.gval
    return result, stats


