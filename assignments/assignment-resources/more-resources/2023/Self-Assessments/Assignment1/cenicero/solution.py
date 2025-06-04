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
    
    #You can read about my several failed attempts at the bottom
    #Anyway I've spent a long time whipping this up so here is the explanation:
    #Step 1: It is measuring "the difficulty" of each storage space (uses heuristics like if it is
    #   near other storages, or if it is hugging the wall), it is also checking to see which boxes
    #   are able to be put in that storage. So we can make sure we are pairing them correctly (ie not impossible)
    #Step 2: We assign each storage one box, which we call sol. We assign by first assigning to "hardest"
    #   storage the closest box, then the 2nd hardest storage to the next closest, and so on
    #Step 3: Some of the storages may already be solved. We go in order from the hardest storages to
    #   the easiest ones. The moment we see an unsolved storage, we will solve that one. We do this by
    #   computing (somewhat greedily) an exact path (and its estimate) from the assigned box to the storage.
    #Step 4: Using the exact path, we know where the robot must be in order to execute the plan, so we have
    #   another path computer to compute a path from the nearest robot to the spot where it needs to be
    #   (Ex: if the box should move left, the robot needs to be to the right of the box)
    #Step 5: Any other unsolved storage will have a default estimation of width*height. Basically just a
    #    big number because we want to make sure we are solving storages IN ORDER because the way we assign
    #    difficulty is an estimate that the other storages may not be solvable if the harder ones are not solved 1st. 

    storage_difficulties = {}
    for storage in state.storage:
        storage_difficulties[str(storage)] = {"diff":tricky_storage_scorer(state,storage),"pot_boxes":[]}

    for box in state.boxes:
        spots = possible_spots(state,box)
        possible_storages = list(filter(lambda s: s["box"] in state.storage,spots))
        for s in possible_storages:
            s["diff"] = storage_difficulties[str(s["box"])]["diff"]
            storage_difficulties[str(s["box"])]["pot_boxes"].append({"box":box,"score":s["score"]})
    
    for key in storage_difficulties:
        storage_difficulties[key]["pot_boxes"].sort(key=(lambda b: b["score"]),reverse=False)

    sol = get_solution_stor(state,storage_difficulties)
    if sol == (None, None):
        return math.inf

    sol[0].sort(key=(lambda s: s["storage"][0]+(s["storage"][1]/state.height)),reverse=False)
    sol[0].sort(key=(lambda s: s["diff"]),reverse=False)
    sol[0].reverse()
    true_estimation = 0

    found_need_to_solve = False
    for s in sol[0]:
        if s["score"] > 0 and found_need_to_solve is False:
            found_need_to_solve = True
            box_total,robot_total,robot_index = estimate_box_to_space(state,s["box"],s["storage"])
            true_estimation += box_total + robot_total
        elif found_need_to_solve is True:
            true_estimation += state.height * state.width

    return true_estimation




'''
def heur_alternate(state):
    Heuristic 2: We implement an "impossible box" checker, and try to rank
    how tricky a storage is to satisfy
    Failure: It only solved 9 / 20

    print(state.state_string())
    total_estimation_box = 0
    for box in state.boxes:
        #compute manhattan between a box and all storage spaces
        all_dists = map(lambda stor: abs(stor[0] - box[0]) + abs(stor[1] - box[1]), state.storage)
        #get the smallest one and add it to the total estimation
        best_est = min(all_dists)
        total_estimation_box += best_est
        if best_est > 0:
            if is_trapped_box(state,box):
                #print(state.state_string())
                return state.width*state.height*len(state.boxes) #idk i just want a big number


    total_estimation_storage = 0
    for stor in state.storage:
        if stor in state.boxes:
            continue #we good
        else:
            total_estimation_storage += tricky_storage_score(state,stor)

    return total_estimation_storage*total_estimation_box

def is_trapped_box(state,box):
    # check left of box
    open_left = box[0] > 0 and (box[0]-1,box[1]) not in state.obstacles
    open_right = box[0] < state.width-1 and (box[0]+1,box[1]) not in state.obstacles
    open_up = box[1] > 0 and (box[0],box[1]-1) not in state.obstacles
    open_down = box[1] < state.height-1 and (box[0],box[1]+1) not in state.obstacles
    can_be_pushed = (open_left and open_right) or (open_up and open_down)
    return not can_be_pushed

def tricky_storage_score(state,stor):
    hugging_vwall = stor[0] == 0 or stor[0] == state.width-1
    hugging_hwall = stor[1] == 0 or stor[1] == state.height-1
    open_left = stor[0] > 0 and (stor[0]-1,stor[1]) not in (state.obstacles & state.storage)
    open_right = stor[0] < state.width-1 and (stor[0]+1,stor[1]) not in (state.obstacles & state.storage)
    open_up = stor[1] > 0 and (stor[0],stor[1]-1) not in (state.obstacles & state.storage)
    open_down = stor[1] < state.height-1 and (stor[0],stor[1]+1) not in (state.obstacles & state.storage)
    s = 1
    if not open_left:
        s += 1
    if not open_down:
        s += 1
    if not open_up:
        s += 1
    if not open_right:
        s += 1
    if hugging_hwall is True:
        s += 2
    if hugging_vwall is True:
        s += 2
    return s
'''



'''
def heur_alternate(state):
    Heuristic 1: We do the same as manhattan distance between boxes and storage spaces.
    If the total distance is more than 0 (implying boxes are not on storages) then
    we also compute total manhattan distance between robots and boxes, and add the two totals.
    Failure: It only solved 9 / 20

    total_estimation_box = 0
    for box in state.boxes:
        #compute manhattan between a box and all storage spaces
        all_dists = map(lambda stor: abs(stor[0] - box[0]) + abs(stor[1] - box[1]), state.storage)
        #get the smallest one and add it to the total estimation
        best_est = min(all_dists)
        total_estimation_box += best_est

    total_estimation_robot = 0
    if total_estimation_box > 0:
        for robot in state.robots:
            #compute manhattan between a robot and all boxes
            all_dists = map(lambda box: abs(box[0] - robot[0]) + abs(box[1] - robot[1]), state.boxes)
            #get the smallest one and add it to the total estimation
            best_est = min(all_dists)
            total_estimation_robot += best_est

    return total_estimation_box+total_estimation_robot
'''

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
    
    total_estimation = 0
    for box in state.boxes:
        #compute manhattan between a box and all storage spaces
        all_dists = map(lambda stor: abs(stor[0] - box[0]) + abs(stor[1] - box[1]), state.storage)
        #get the smallest one and add it to the total estimation
        best_est = min(all_dists)
        total_estimation += best_est
    return total_estimation

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
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''

    searchEngine = SearchEngine("custom","default")
    searchEngine.init_search(initial_state,sokoban_goal_state,heur_fn,(lambda sN: fval_function(sN, weight)))
    return searchEngine.search(timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    rem_timebound = timebound
    best_result = False, None
    while rem_timebound > 0:
        costbound = None
        if best_result[0] is not False:
            costbound = best_result[0].gval-1,math.inf,math.inf
        searchEngine = SearchEngine("custom","default")
        searchEngine.init_search(initial_state,sokoban_goal_state,heur_fn,(lambda sN: fval_function(sN, weight)))
        result = searchEngine.search(rem_timebound,costbound)
        if result[0] is False:
            rem_timebound = 0
        else:
            rem_timebound = rem_timebound - result[1].total_time - 0.08
            best_result = result
            weight = max(1 + (math.floor((weight-1)*4)-1)/8,1)
            if weight == 1:
                return best_result
    if best_result[0] is False:
        return result
    else:
        return best_result




def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    rem_timebound = timebound
    best_result = False, None
    while rem_timebound > 0:
        costbound = None
        if best_result[0] is not False:
            costbound = math.inf,best_result[0].gval-1,math.inf
        searchEngine = SearchEngine("custom","default")
        searchEngine.init_search(initial_state,sokoban_goal_state,heur_fn,(lambda sN: sN.hval))
        result = searchEngine.search(rem_timebound,costbound)
        if result[0] is False:
            rem_timebound = 0
        else:
            rem_timebound = rem_timebound - result[1].total_time - 0.08
            best_result = result
    if best_result[0] is False:
        return result
    else:
        return best_result

# HELPER FOR REAL

def possible_spots(state,box):
    #print(path)
    all_coords = []
    frontier = [{"box":box,"score":0,"path":""}]
    while len(frontier) > 0:
        new_frontier = []
        while len(frontier) > 0:
            #print(str(len(all_coords)), str(len(frontier)))
            frontier.sort(key=(lambda f: f["score"]),reverse=True)
            popped = frontier.pop()
            all_coords.append(popped)
            box = popped["box"]
            path = popped["path"]
            left = get_left(box),'<',0
            right = get_right(box),'>',0
            up = get_up(box),'^',0
            down = get_down(box),'v',0
            if not is_obstacle(state,left[0]) and not is_obstacle(state,right[0]):
                while not is_obstacle(state,left[0]):
                    full_score = popped["score"] + left[2] + 1
                    full_path = path + left[1]
                    new_path = left[1] + left[1][-1]
                    new_score = left[2] + 1
                    if len(full_path) > 1 and full_path[-1] != full_path[-2]:
                        full_score += 2
                        new_score += 2
                    if len(list(filter(lambda s: s["box"] == left[0],all_coords + frontier + new_frontier))) == 0:
                        new_frontier.append({"box":left[0],"score":full_score,"path":full_path})
                    left = get_left(left[0]),new_path,new_score
                while not is_obstacle(state,right[0]):
                    full_score = popped["score"] + right[2] + 1
                    full_path = path + right[1]
                    new_path = right[1] + right[1][-1]
                    new_score = right[2] + 1
                    if len(full_path) > 1 and full_path[-1] != full_path[-2]:
                        full_score += 2
                        new_score += 2
                    if len(list(filter(lambda s: s["box"] == right[0],all_coords + frontier + new_frontier))) == 0:
                        new_frontier.append({"box":right[0],"score":full_score,"path":full_path})
                    right = get_right(right[0]),new_path,new_score
            if not is_obstacle(state,up[0]) and not is_obstacle(state,down[0]):
                while not is_obstacle(state,up[0]):
                    full_score = popped["score"] + up[2] + 1
                    full_path = path + up[1]
                    new_path = up[1] + up[1][-1]
                    new_score = up[2] + 1
                    if len(full_path) > 1 and full_path[-1] != full_path[-2]:
                        full_score += 2
                        new_score += 2
                    if len(list(filter(lambda s: s["box"] == up[0],all_coords + frontier + new_frontier))) == 0:
                        new_frontier.append({"box":up[0],"score":full_score,"path":full_path})
                    up = get_up(up[0]),new_path,new_score
                while not is_obstacle(state,down[0]):
                    full_score = popped["score"] + down[2] + 1
                    full_path = path + down[1]
                    new_path = down[1] + down[1][-1]
                    new_score = down[2] + 1
                    if len(full_path) > 1 and full_path[-1] != full_path[-2]:
                        full_score += 2
                        new_score += 2
                    if len(list(filter(lambda s: s["box"] == down[0],all_coords + frontier + new_frontier))) == 0:
                        new_frontier.append({"box":down[0],"score":full_score,"path":full_path})
                    down = get_down(down[0]),new_path,new_score
            while len(new_frontier) > 0:
                t = new_frontier.pop()
                frontier.append(t)
    return all_coords

def get_solution_stor(state,storage_diffs):
    #storage_diffs is an object with storages coords as keys, and values as {diff: , pot_boxes: []}
    #where pot_boxes is the listed of "box"es and their respective "h" value.
    build_a_list = list(filter(lambda s: str(s) in storage_diffs,state.storage))
    build_a_list.sort(key=(lambda stor: stor[0]+(stor[1]/state.height)),reverse=False)
    build_a_list.sort(key=(lambda stor: storage_diffs[str(stor)]["diff"]),reverse=False)
    if(len(build_a_list) == 0):
        return [],0
    popped = build_a_list.pop()
    storage_vals = storage_diffs[str(popped)]
    storage_vals["pot_boxes"].sort(key=(lambda b: b["score"]),reverse=False)
    for i in range(len(storage_vals["pot_boxes"])):
        box = storage_vals["pot_boxes"][i]
        matching = {"box":box["box"], "storage":popped, "score": box["score"], "diff": storage_vals["diff"]}
        new_storage_diffs = {}
        for s in build_a_list:
            new_storage_diffs[str(s)] = {"diff": storage_diffs[str(s)]["diff"], "pot_boxes": list(filter(lambda b: b["box"] != box["box"],storage_diffs[str(s)]["pot_boxes"]))}
        t = get_solution_stor(state, new_storage_diffs)
        if t != (None, None):
            t[0].append(matching)
            x = (t[0], t[1] + matching["score"])
            return x
    return (None, None)

def estimate_box_to_space(state,box,storage):
    path_to_storage = box_path_from(state,box,storage)
    total = path_to_storage["score"]
    if total == math.inf:
        return math.inf,math.inf,0
    path = path_to_storage["path"]
    robot_pos = box
    if path[0] == "v":
        robot_pos = get_up(box)
    if path[0] == "^":
        robot_pos = get_down(box)
    if path[0] == "<":
        robot_pos = get_right(box)
    if path[0] == ">":
        robot_pos = get_left(box)
    best_index = 0
    best_guess = math.inf
    for i in range(len(state.robots)):
        est = robot_path_from2(state,state.robots[i],robot_pos)
        if best_guess > est:
            best_guess = est
            best_index = i
    return total,best_guess,best_index

def box_path_from(state,box,storage):
    #print(path)
    all_coords = []
    frontier = [{"box":box,"score":0,"path":""}]
    while len(frontier) > 0:
        new_frontier = []
        while len(frontier) > 0:
            frontier.sort(key=(lambda f: f["score"]),reverse=True)
            popped = frontier.pop()
            all_coords.append(popped)
            box = popped["box"]
            path = popped["path"]
            if box == storage:
                return popped
            left = get_left(box),'<',0
            right = get_right(box),'>',0
            up = get_up(box),'^',0
            down = get_down(box),'v',0
            if not is_obstacle(state,left[0]) and not is_obstacle(state,right[0]):
                while not is_obstacle(state,left[0]):
                    full_score = popped["score"] + left[2] + 1
                    full_path = path + left[1]
                    new_path = left[1] + left[1][-1]
                    new_score = left[2] + 1
                    if len(full_path) > 1 and full_path[-1] != full_path[-2]:
                        full_score += 2
                        new_score += 2
                    if len(list(filter(lambda s: s["box"] == left[0],all_coords + frontier + new_frontier))) == 0:
                        new_frontier.append({"box":left[0],"score":full_score,"path":full_path})
                    left = get_left(left[0]),new_path,new_score
                while not is_obstacle(state,right[0]):
                    full_score = popped["score"] + right[2] + 1
                    full_path = path + right[1]
                    new_path = right[1] + right[1][-1]
                    new_score = right[2] + 1
                    if len(full_path) > 1 and full_path[-1] != full_path[-2]:
                        full_score += 2
                        new_score += 2
                    if len(list(filter(lambda s: s["box"] == right[0],all_coords + frontier + new_frontier))) == 0:
                        new_frontier.append({"box":right[0],"score":full_score,"path":full_path})
                    right = get_right(right[0]),new_path,new_score
            if not is_obstacle(state,up[0]) and not is_obstacle(state,down[0]):
                while not is_obstacle(state,up[0]):
                    full_score = popped["score"] + up[2] + 1
                    full_path = path + up[1]
                    new_path = up[1] + up[1][-1]
                    new_score = up[2] + 1
                    if len(full_path) > 1 and full_path[-1] != full_path[-2]:
                        full_score += 2
                        new_score += 2
                    if len(list(filter(lambda s: s["box"] == up[0],all_coords + frontier + new_frontier))) == 0:
                        new_frontier.append({"box":up[0],"score":full_score,"path":full_path})
                    up = get_up(up[0]),new_path,new_score
                while not is_obstacle(state,down[0]):
                    full_score = popped["score"] + down[2] + 1
                    full_path = path + down[1]
                    new_path = down[1] + down[1][-1]
                    new_score = down[2] + 1
                    if len(full_path) > 1 and full_path[-1] != full_path[-2]:
                        full_score += 2
                        new_score += 2
                    if len(list(filter(lambda s: s["box"] == down[0],all_coords + frontier + new_frontier))) == 0:
                        new_frontier.append({"box":down[0],"score":full_score,"path":full_path})
                    down = get_down(down[0]),new_path,new_score
            while len(new_frontier) > 0:
                t = new_frontier.pop()
                frontier.append(t)
    return None

def robot_path_from2(state,robot,spot):
    all_spots = []
    frontier = [robot]
    moves = 0
    while len(frontier) > 0:
        new_frontier = []
        while len(frontier) > 0:
            popped = frontier.pop() #coords
            if popped == spot:
                return moves
            all_spots.append(popped)
            possible = [get_up(popped),get_left(popped),get_down(popped),get_right(popped)]
            for p in possible:
                if (p in state.robots and p != robot) or is_obstacle(state,p) is True or p in state.boxes or p in all_spots or p in new_frontier:
                    continue
                new_frontier.append(p)
        moves += 1
        for f in new_frontier:
            frontier.append(f)
    return math.inf




# HELPER FUNCTIONS FOR ALTERNATE HEURISTICS (most are failed so are unused :(  )

def is_trapped_box(state,box):
    # check left of box
    open_left = box[0] > 0 and (box[0]-1,box[1]) not in state.obstacles
    open_right = box[0] < state.width-1 and (box[0]+1,box[1]) not in state.obstacles
    open_up = box[1] > 0 and (box[0],box[1]+1) not in state.obstacles
    open_down = box[1] < state.height-1 and (box[0],box[1]-1) not in state.obstacles
    can_be_pushed = (open_left and open_right) or (open_up and open_down)
    return not can_be_pushed

def tricky_storage_solver(state):
    #list_of_scores = map(lambda stor: {score: tricky_storage_scorer(state,stor), stor:stor},state.storage)
    list_of_scores = []
    for stor in state.storage:
        list_of_scores.append({"stor":stor, "score": tricky_storage_scorer(state,stor)})
    list_of_scores.sort(key = (lambda s: s["score"]), reverse = True)
    max_score = list_of_scores[0]["score"]
    for s in list_of_scores:
        if s["stor"] not in state.boxes:
            return s["score"]/max_score
    return 0

def tricky_storage_scorer(state,stor):
    score = 1
    if is_obstacle(state,get_left(stor)):
        score += 2
    elif is_storage(state,get_left(stor)):
        score += 1
    if is_obstacle(state,get_right(stor)):
        score += 2
    elif is_storage(state,get_right(stor)):
        score += 1
    if is_obstacle(state,get_up(stor)):
        score += 2
    elif is_storage(state,get_up(stor)):
        score += 1
    if is_obstacle(state,get_down(stor)):
        score += 2
    elif is_storage(state,get_down(stor)):
        score += 1
    return score

def box_scorer(state):
    #compute manhattan between a box and all storage spaces
    total_estimation_box = 0
    for box in state.boxes:
        all_dists = map(lambda stor: abs(stor[0] - box[0]) + abs(stor[1] - box[1]), state.storage)
        #get the smallest one and add it to the total estimation
        best_est = min(all_dists)
        total_estimation_box += best_est
    return total_estimation_box

def robot_scorer(state):
    total_estimation_robot = 0
    unsolved_boxes = list(filter(lambda box: box not in state.storage,state.boxes))
    if len(unsolved_boxes) == 0:
        return 0
    for robot in state.robots:
        #compute manhattan between a robot and all boxes
        all_dists = map(lambda box: abs(box[0] - robot[0]) + abs(box[1] - robot[1]), unsolved_boxes)
        #get the smallest one and add it to the total estimation
        best_est = min(all_dists)
        total_estimation_robot += best_est
    return total_estimation_robot

def get_left(coords):
    return (coords[0]-1,coords[1])

def get_right(coords):
    return (coords[0]+1,coords[1])

def get_up(coords):
    return (coords[0],coords[1]-1)

def get_down(coords):
    return (coords[0],coords[1]+1)

def is_obstacle(state,coords):
    return coords[0] < 0 or coords[1] < 0 or coords[0] >= state.width or coords[1] >= state.height or coords in state.obstacles

def is_storage(state,coords):
    return coords in state.storage
