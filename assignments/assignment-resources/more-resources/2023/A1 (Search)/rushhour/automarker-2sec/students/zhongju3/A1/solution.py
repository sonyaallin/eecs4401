#   Look for #IMPLEMENT tags in this file. These tags indicate what has        
#   to be implemented to complete the Rush Hour domain.        
        
#   You may add only standard python imports (numpy, itertools are both ok).        
#   You may not remove any imports.        
#   You may not import or otherwise source any of your own files.        
        
import os  # you will likely want this for timing functions        
import math # for infinity        
from search import *  # for search engines        
from rushhour import *        
        
# RUSH HOUR GOAL TEST        
def rushhour_goal_fn(state):         
    # IMPLEMENT        
    '''a Rush Hour Goal Test'''        
    '''INPUT: a parking state'''        
    '''OUTPUT: True, if satisfies the goal, else false.'''        
    '''[<name>, <loc>, <length>, <is_horizontal>, <is_goal>]'''        
    '''Return (board_size, goal_entrance, goal_direction)    
           where board_size = (m, n) is the dimensions of the board (m rows, n columns)    
                 goal_entrance = (x, y) is the location of the goal    
                 goal_direction is one of 'N', 'E', 'S' or 'W' indicating    
                                the orientation of the goal    
        '''        
    #cur_board = Rushhour(state)        
    cars = []        
    #print(state.vehicle_list)        
    for car in state.vehicle_list:        
        #print (car.loc)        
        if car.is_goal:        
            cars.append(car)        
    goal_info = state.board_properties      
    for i in cars:      
        if gcar_on_goal(i, goal_info):      
            return True      
    return False      
    # for gcar in cars:        
    #     if not gcar.is_horizontal and goal_info[-1] == "N":        
    #         if goal_info[1] == gcar.loc:        
    #             return True        
    #     if not gcar.is_horizontal and goal_info[-1] == "S":        
    #         coord = gcar.loc        
    #         coord = (coord[0], coord[1] + gcar.length-1) #implement wrap around        
    #         if goal_info[1] == coord:        
    #             return True        
    #     if gcar.is_horizontal and goal_info[-1] == "E":        
    #         coord = gcar.loc        
    #         coord = (coord[0]+gcar.length-1, coord[1]) #implement wrap around        
    #         if goal_info[1] == coord:        
    #             return True        
    #     if gcar.is_horizontal and goal_info[-1] == "W":        
    #         coord = gcar.loc        
    #         coord = (coord[0], coord[1]) #implement wrap around        
    #         if goal_info[1] == coord:        
    #             return True        
    return False        
        
# (N-1, M-1) is the bottom right corner !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
def gcar_on_goal(carloc: Vehicle, gloc: tuple): # returns true if the car is on the goal state        
    '''[<name>, <loc>, <length>, <is_horizontal>, <is_goal>]'''        
    '''Return (board_size, goal_entrance, goal_direction)    
           where board_size = (m, n) is the dimensions of the board (m rows, n columns)    
                 goal_entrance = (x, y) is the location of the goal    
                 goal_direction is one of 'N', 'E', 'S' or 'W' indicating    
                                the orientation of the goal    
        '''        
    #print(carloc.loc)      
    if gloc[-1] == "N" and not carloc.is_horizontal and carloc.is_goal and carloc.loc == gloc[1]:        
        return True        
                
    elif gloc[-1] == "S" and not carloc.is_horizontal and carloc.is_goal:        
        if carloc.loc[1]+carloc.length >= gloc[0][1]:        
            if (carloc.loc[0], (carloc.loc[1]+carloc.length - gloc[0][1])) == gloc[1]: #check wraparound        
                return True        
        else:        
            if carloc.loc[0] == gloc[1][0] and (gloc[1][1]>=carloc.loc[1] and gloc[1][1] <= (carloc.loc[1]+carloc.length)):        
                return True        
    elif gloc[-1] == "W" and carloc.is_horizontal and carloc.loc == gloc[1]:        
        return True        
    elif gloc[-1] == "E" and carloc.is_horizontal:        
        if carloc.loc[0]+carloc.length >= gloc[0][0]:        
            if (carloc.loc[0]+carloc.length-gloc[0][0] , carloc.loc[1]) == gloc[1]:        
                return True        
        else:        
            if carloc.loc[1] == gloc[1][1] and (gloc[1][0] >= carloc.loc[0] and gloc[1][0] <= (carloc.loc[0]+carloc.length)):        
                return True        
    return False        
        
def gcar_on_goal_loose(car: Vehicle, gloc: tuple): # returns true if the car is on the goal state        
    '''[<name>, <loc>, <length>, <is_horizontal>, <is_goal>]'''        
    '''Return (board_size, goal_entrance, goal_direction)    
        '''        
    temp=[]      
    if car.is_horizontal:      
        #if (car.loc[0]+car.length)<gloc[0][0]: # no wraparound      
        for i in range(0,car.length+1):      
                if car.loc[0]+i >= gloc[0][0]: #warparound      
                     temp.append((car.loc[0]+i-gloc[0][0]-1, car.loc[1]))      
                else:      
                    temp.append((car.loc[0]+i, car.loc[1]))      
        return gloc[1] in temp      
      
    if not car.is_horizontal:      
        for i in range(0,car.length+1):      
                if car.loc[1]+i >= gloc[0][1]: #warparound      
                    temp.append((car.loc[0], car.loc[1]+i-gloc[0][1]-1))      
                else:      
                    temp.append((car.loc[0], car.loc[1]+i))      
        return gloc[1] in temp      
      
            # for i in range(0,car.length+1):      
            #     temp.append(car.loc[0]+i, car.loc[1])      
            # return gloc[1] in temp      
        # else:      
        #     for i in range(0,car.length+1):      
        #         if car.loc[0]+i >= gloc[0][0]: #warparound      
        #             temp.append(car.loc[0]+i-gloc[0][0]-1, car.loc[1])      
        #         else:      
        #             temp.append(car.loc[0]+i, car.loc[1])      
        #     return gloc[1] in temp      
# RUSH HOUR HEURISTICS        
def heur_alternate(state): #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
    # IMPLEMENT        
    '''a better heuristic'''        
    '''INPUT: a tokyo parking state'''        
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''        
    # heur_min_moves has obvious flaws.        
    # Write a heuristic function that improves upon heur_min_moves to estimate distance between the current state and the goal.        
    # Your function should return a numeric value for the estimate of the distance to the goal.        
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.        
            
    #cur_board = Rushhour(state)        
    gcars = []        
    moves = []        
    obstacles = []        
    for car in state.vehicle_list:        
        if car.is_goal:        
            gcars.append(car)        
        else:        
            obstacles.append(car)        
    ginfo = state.board_properties        
    gx = ginfo[1][0]        
    gy = ginfo[1][1]        
    for car in gcars:      
        dist = 0        
        if gcar_on_goal(car, ginfo):      
            return 0      
        dist = dist_simple(car, ginfo)      
        cx = car.loc[0]        
        cy = car.loc[1]        
        for obstc in obstacles:        
            ox = obstc.loc[0]        
            oy = obstc.loc[1]      
            if not car.is_horizontal:       
                if gx == cx:        
                    if (oy > cy and oy<gy) or (oy < cy and oy>gy):      
                        dist+=1      
            else:      
                if gy == cy:      
                    if (ox>cx and ox < gx) or (ox<cx and ox>gx):      
                        dist+=1      
            moves.append(dist)      
    return min(moves)       
        
def dist_simple(car: list, goal: tuple):  #distance from car to goal with wrapaound i think      
    temp = car        
    goal_info = goal        
    moves1 = []        
    moves2 = []        
    if temp.loc[0] == goal_info[1][0] and not temp.is_horizontal:        
        if goal_info[1][1] >= temp.loc[1]: # when goal is below the car        
            moves1.append(abs(goal_info[1][1] - temp.loc[1])) # consider length of the car?        
            moves2.append(abs(temp.loc[1]+ goal_info[0][0]- goal_info[1][1])) # wrapping around going up        
        else: # when goal is above the car        
            moves1.append(abs(goal_info[1][1]-temp.loc[1]))        
            moves2.append(abs(goal_info[0][0]-temp.loc[1]+goal_info[1][1]))        
        
    elif temp.loc[1] == goal_info[1][1] and temp.is_horizontal:        
        if goal_info[1][0] >= temp.loc[0]: # when goal is to the right of the car      
                #print(abs(temp.loc[0] + goal_info[0][0] - goal_info[1][0]))      
                #print(abs(goal_info[1][0] - temp.loc[0]))      
            moves1.append(abs(goal_info[1][0] - temp.loc[0]))        
            moves2.append(abs(temp.loc[0] + goal_info[0][1] - goal_info[1][0]))      
            # print(goal_info[0])      
            # print(temp.loc[0])      
            # print(goal_info[0][0])      
            # print(goal_info[1][0])      
        else: # when goal is to the left of the car        
            moves1.append(abs(temp.loc[0] - goal_info[1][0]))        
            moves2.append(abs(goal_info[1][0]+goal_info[0][1]-temp.loc[0]))        
    return min(moves1+moves2)        
        
def heur_min_dist(state):        
    #IMPLEMENT        
    '''admissible tokyo parking puzzle heuristic'''        
    '''INPUT: a tokyo parking state'''        
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''        
    # We want an admissible heuristic, which is an optimistic heuristic.        
    # It must never overestimate the cost to get from the current state to the goal.        
    # Getting to the goal requires one move for each tile of distance.        
    # Since the board wraps around, there will be two different directions that lead to a goal.        
    # NOTE that we want an estimate of the number of moves required from our current state        
    # 1. Proceeding in the first direction, let MOVES1 =        
    #    number of moves required to get to the goal if it were unobstructed and if we ignore the orientation of the goal        
    # 2. Proceeding in the second direction, let MOVES2 =        
    #    number of moves required to get to the goal if it were unobstructed and if we ignore the orientation of the goal        
    #        
    # Our heuristic value is the minimum of MOVES1 and MOVES2 over all goal vehicles.        
    # You should implement this heuristic function exactly, and you can improve upon it in your heur_alternate         
    '''[<name>, <loc>, <length>, <is_horizontal>, <is_goal>]'''        
    '''Return (board_size, goal_entrance, goal_direction)    
           where board_size = (m, n) is the dimensions of the board (m rows, n columns)    
                 goal_entrance = (x, y) is the location of the goal    
                 goal_direction is one of 'N', 'E', 'S' or 'W' indicating    
                                the orientation of the goal    
        '''        
    #cur_board = Rushhour(state)        
    gcars = []        
    for car in state.vehicle_list:        
        if car.is_goal:        
            gcars.append(car)        
    goal_info = state.board_properties        
    moves1 = []        
    moves2 = []        
    for temp in gcars:      
        if gcar_on_goal_loose(temp, goal_info):      
            moves1.append(0)      
        elif temp.loc[0] == goal_info[1][0] and not temp.is_horizontal:        
            if goal_info[1][1] >= temp.loc[1]: # when goal is below the car        
                moves1.append(abs(goal_info[1][1] - temp.loc[1])) # consider length of the car?        
                moves2.append(abs(temp.loc[1]+ goal_info[0][0]- goal_info[1][1])) # wrapping around going up        
            else: # when goal is above the car        
                moves1.append(abs(goal_info[1][1]-temp.loc[1]))        
                moves2.append(abs(goal_info[0][0]-temp.loc[1]+goal_info[1][1]))        
        
        elif temp.loc[1] == goal_info[1][1] and temp.is_horizontal:        
            if goal_info[1][0] >= temp.loc[0]: # when goal is to the right of the car      
                #print(abs(temp.loc[0] + goal_info[0][0] - goal_info[1][0]))      
                #print(abs(goal_info[1][0] - temp.loc[0]))      
                moves1.append(abs(goal_info[1][0] - temp.loc[0]))        
                moves2.append(abs(temp.loc[0] + goal_info[0][1] - goal_info[1][0]))      
                # print(goal_info[0])      
                # print(temp.loc[0])      
                # print(goal_info[0][0])      
                # print(goal_info[1][0])      
            else: # when goal is to the left of the car        
                moves1.append(abs(temp.loc[0] - goal_info[1][0]))        
                moves2.append(abs(goal_info[1][0]+goal_info[0][1]-temp.loc[0]))        
    return min(moves1+moves2)        
        
        
        
def heur_zero(state):        
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''        
    return 0        
        
def fval_function(sN, weight):        
    # IMPLEMENT        
    """    
    Provide a custom formula for f-value computation for Weighted A star.    
    Returns the fval of the state contained in the sNode.    
    
    @param sNode sN: A search node (containing a SokobanState)    
    @param float weight: Weight given by Weighted A star    
    @rtype: float    
    """        
    fv = sN.gval + weight * sN.hval        
    return fv   
        
def fval_function_XUP(sN, weight):        
    #IMPLEMENT        
    """    
    Another custom formula for f-value computation for Weighted A star.    
    Returns the fval of the state contained in the sNode.    
    XUP causes the best-first search to explore near-optimal paths near the end of a path.    
    
    @param sNode sN: A search node (containing a RushHour State)    
    @param float weight: Weight given by Weighted A star    
    @rtype: float    
    """      
    #fv = (weight/2) * (sN.gval + sN.hval + math.sqrt((sN.gval+sN.hval))*2 + 4*weight*(weight-1)*sN.hval*2)      
          
    fv= (1/(weight*2)) * (sN.gval + sN.hval + math.sqrt((sN.gval+sN.hval)**2 + 4 * weight * (weight-1)*sN.hval**2))      
    return fv      
        
def fval_function_XDP(sN, weight):        
    #IMPLEMENT        
    """    
    A third custom formula for f-value computation for Weighted A star.    
    Returns the fval of the state contained in the sNode.    
    XDP causes the best-first search to explore near-optimal paths near the start of a path.     
    
    @param sNode sN: A search node (containing a RushHour State)    
    @param float weight: Weight given by Weighted A star    
    @rtype: float    
    """      
    #fv = (weight/2) *(sN.gval + (2*weight-1)*sN.hval + math.sqrt((sN.gval-sN.hval)*2 + 4 * weight * sN.gval * sN.hval))      
          
    fv = (1/weight/2)*(sN.gval+(2*weight-1)*sN.hval + math.sqrt((sN.gval-sN.hval)**2+4*weight*sN.gval*sN.hval))      
    return fv      

def fval_gbfs(sN):
    return sN.hval


# SEARCH ALGORITHMS        
def weighted_astar(initial_state, heur_fn, weight, timebound, costbound = (float(math.inf), float(math.inf), float(math.inf))):        
    # IMPLEMENT            
    """    
    Provides an implementation of weighted a-star, as described in the HW1 handout'''    
    INPUT: a rushhour state that represents the start state and a timebound (number of seconds)    
    OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object    
    implementation of weighted astar algorithm    
    
    @param initial_state: A RushHour State    
    @param heur_fn: The heuristic to use    
    @param weight: The weight to use    
    @param timebound: The timebound to enforce    
    @param costbound: The costbound to enforce, if any    
    @rtype: (Rushour State, SearchStats) if solution is found, else (False, SearchStats)    
    """    
    #fval_function(initial_state., weight)    
    wrapped_fval_function = (lambda sN : fval_function(sN,weight))  
    search_eng = SearchEngine('custom', "none")  
    search_eng.init_search(initial_state, rushhour_goal_fn, heur_fn, wrapped_fval_function)
    #print(costbound)
    return search_eng.search(timebound, costbound)  
            
        
def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search        
    # IMPLEMENT        
    """    
    Provides an implementation of iterative a-star, as described in the HW1 handout    
    INPUT: a rushhour state that represents the start state and a timebound (number of seconds)    
    OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object    
    implementation of weighted astar algorithm    
        
    @param initial_state: A RushHour State    
    @param heur_fn: The heuristic to use    
    @param weight: The weight to begin with during the first iteration (this should change)    
    @param timebound: The timebound to enforce    
    @rtype: (Rushour State, SearchStats) if solution is found, else (False, SearchStats)    
    """      
    #wrapped_fval_function = (lambda sN : fval_function(sN,weight))
    start_time = os.times()[0]
    cur_time = os.times()[0]
    result = None
    result_stats = None
    res_f = float(math.inf)

    while cur_time - start_time < timebound:
        final, stats = weighted_astar(initial_state, heur_fn = heur_alternate, weight=1, timebound=5, costbound = (float(math.inf), float(math.inf), float(math.inf)))
        if final != False:
            if final.gval + heur_alternate(final) < res_f:
                res_f = final.gval + heur_alternate(final)
                result = final
                result_stats = stats
            if weight>0.1:
                weight-=0.1
            initial_state = final
        else:
            return False, stats
        cur_time = os.times()[0]
    #print(result)
    return result, result_stats
    #return False, None #REPLACE THIS!!        

def greedy_bfs_help(initial_state, heur_fn, timebound, costbound = (float(math.inf), float(math.inf), float(math.inf))):
    wrapped_fval_function = (lambda sN : fval_gbfs(sN))  
    search_eng = SearchEngine('custom', "none")  
    search_eng.init_search(initial_state, rushhour_goal_fn, heur_fn, wrapped_fval_function)
    
    return search_eng.search(timebound, costbound)

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)        
    # IMPLEMENT        
    """    
    Provides an implementation of anytime greedy best-first search, as described in the HW1 handout    
    INPUT: a rush hour state that represents the start state and a timebound (number of seconds)    
    OUTPUT: A goal state (if a goal is found), else False    
    
    @param initial_state: A RushHour State    
    @param heur_fn: The heuristic to use    
    @param timebound: The timebound to enforce    
    @rtype: (Rushour State, SearchStats) if solution is found, else (False, SearchStats)    
    """   
    start_time = os.times()[0]
    cur_time = os.times()[0]
    result = None
    result_stats = None
    res_f = float(math.inf)

    while cur_time - start_time < timebound:
        state, stats = greedy_bfs_help(initial_state, heur_fn = heur_alternate, timebound=1, costbound = (float(math.inf), float(math.inf), float(math.inf)))
        if state != False:
            if heur_alternate(state) < res_f:
                res_f = heur_alternate(state)
                result = state
                result_stats = stats
            # if weight>0.1:
            #     weight-=0.1
            initial_state = state
        else:
            return False, stats
        cur_time = os.times()[0]
    #print(result)
    if result:
        return result, result_stats
    return False       
    #return False, None #REPLACE THIS!!        