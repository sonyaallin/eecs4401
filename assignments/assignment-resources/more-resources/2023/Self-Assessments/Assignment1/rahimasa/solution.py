#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

from dis import dis
import os  # for time functions
import math
from pstats import Stats
from collections import deque, defaultdict
from sqlalchemy import false, true  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

# SOKOBAN HEURISTICS
def heur_alternate(state):
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.
    """
    This herustic is basically a bfs from each box to the nearest sotrage while avoiding obstacles and boxes only if they cannot be moved,
    it also accounts for distance from nearest robot to the box.
    I tried many heurstics after this like updating the boxes we move, making only one box per location, boxes next to each other are bad
    And many more. They all seemed like they would perform better than this but they just don't so I stuck with this
    """
    index=0  
    robot_dist={}  
    l=[]  
    for robot in state.robots:  
        robot_dist[robot]=0  
        l.append(robot)  
    while index< len(l):  
        tile= l[index]  
        directions =[0,0,0,0]   
        directions[0]= tile[0],max(0,tile[1]-1)    
        directions[1]=tile[0],min(state.height-1, tile[1]+1)  
        directions[2]=max(0,tile[0]-1),tile[1]   
        directions[3]= min(state.width-1, tile[0]+1), tile[1]  
        for direction in directions:  
            if direction not in robot_dist:  
                l.append(direction)  
                robot_dist[direction]= robot_dist[tile]+1  
        index+=1   
    dist=[]  
    boxes_and_obstacles={}   
    for box in state.boxes:  
        boxes_and_obstacles[box]=1  
    for obstacle in state.obstacles:  
        boxes_and_obstacles[obstacle]=1  
    for box in state.boxes:  
        visited={box:[0,box]}  
        q=[box]  
        index=0  
        while index< len(q):  
            tile = q[index]    
            directions =[0,0,0,0]  
            if tile[1]!=state.height-1:  
                if (tile[0], tile[1]+1) in robot_dist:  
                    directions[0]= tile[0],max(0,tile[1]-1)  
                  
            if tile[1]!=0:  
                if (tile[0], tile[1]-1) in robot_dist:  
                    directions[1]=tile[0],min(state.height-1, tile[1]+1)  
            if tile[0]!= state.width-1:  
                if (tile[0]+1, tile[1]) in robot_dist:  
                    directions[2]=max(0,tile[0]-1),tile[1]  
            if tile[0]!=0:  
                if (tile[0]-1, tile[1]) in robot_dist:  
                    directions[3]= min(state.width-1, tile[0]+1), tile[1]  
            for direction in directions:  
                if direction not in visited and direction!=0:  
                    if direction not in boxes_and_obstacles:  
                        q.append(direction)  
                        visited[direction]=[visited[tile][0]+1]+ visited[tile][1:]+[direction]  
                    elif direction in state.boxes:  
                        sub_neighbours= [((direction[0]-1, direction[1]),(direction[0]+1, direction[1])), ( (direction[0], direction[1]+1),(direction[0], direction[1]-1))]  
                        for sub in sub_neighbours:  
                            if sub[0] in robot_dist and sub[1] in robot_dist and sub[0] not in boxes_and_obstacles and sub[1] not in boxes_and_obstacles:  
                                q.append(direction)  
                                visited[direction]=[visited[tile][0]+1+ robot_dist[sub[0]]]+ visited[tile][1:]+[direction]  
            index+=1  
        dist.append([float('inf'), box, box])    
        count=0  
        for location in state.storage:  
            if location in visited and visited[location][0]< dist[-1][0]:  
                dist[-1]= visited[location]  
            count+=1  
        boxes_and_obstacles.pop(box)  
        boxes_and_obstacles[dist[-1][-1]]=1  
    sum_dist=0   
    for d_path in dist:  
        if d_path[0]==0:  
            continue  
        if d_path[0]==float('inf'):  
            return d_path[0]  
        box= d_path[1]  
        pushed= d_path[2]  
        pushed_from =None  
        if pushed[1]== box[1]+1:  
            pushed_from= box[0], box[1]-1  
        elif pushed[1]== box[1]-1:  
            pushed_from = box[0], box[1]+1  
        elif pushed[0]== box[0]+1:  
            pushed_from= box[0]-1, box[1]  
        else:  
            pushed_from= box[0]+1, box[1]  
        sum_dist+= d_path[0]+ robot_dist[pushed_from]  
    return sum_dist  # CHANGE THIS


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
    sum_dist=0
    for box in state.boxes:
        closest = float('inf')
        for location in state.storage:
            dist = abs(box[0] -location[0]) + abs(box[1]-location[1])
            if dist< closest:
                closest=dist
        sum_dist+=closest
    return sum_dist  # CHANGE THIS

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + weight* sN.hval
    return 0 #CHANGE THIS

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    custon_search = SearchEngine('custom', 'full')
    wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 
    custon_search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    return custon_search.search(timebound)
    return None, None  # CHANGE THIS

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    end_search = os.times()[0]+timebound
    curr_weight = weight
    output = None, None
    optimal = float('inf')
    optimal_output= None,None
    custom_search = SearchEngine('custom', 'full')
    wrapped_fval_function = (lambda sN : fval_function(sN,curr_weight)) 
    custom_search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    while curr_weight>=0 and not custom_search.open.empty():
        # print(end_search- os.times()[0])
        if output[0] is None:
        
            output = custom_search.search(end_search- os.times()[0])
            if output[0] is not False:
                optimal= output[0].gval+ heur_fn(output[0])
            optimal_output=output
            
        else:
            hval = heur_fn(output[0])
            if (hval<optimal):
                optimal= hval
                optimal_output= output
            output = custom_search.search(end_search- os.times()[0],( float("inf"), float("inf"), optimal))
        if os.times()[0]> end_search:
            # print(output, optimal_output)
            return optimal_output
        curr_weight/=3
        custom_search.fval_function= (lambda sN : fval_function(sN,curr_weight)) 
    # print(output, optimal_output)
    return optimal_output
    return None, None #CHANGE THIS
def gbfs_f_val(sN):
    return sN.hval
def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    custom_search = SearchEngine('best_first', 'full')
    custom_search.init_search(initial_state, sokoban_goal_state, heur_fn, gbfs_f_val)
    end_search = os.times()[0]+timebound
    output= None, None
    optimal = float('inf')
    optimal_output= None, None
    while not custom_search.open.empty():
        if output[0] is None:
            output = custom_search.search(end_search- os.times()[0])
            optimal_output= output
        else:
            if output[0] is not False and output[0].gval< optimal:
                optimal= output[0].gval
                optimal_output= output
            output = custom_search.search(end_search- os.times()[0],( optimal, float('inf'), float('inf')))
        if os.times()[0]> end_search:
            return optimal_output
    return optimal_output #CHANGE THIS



"""
NOTE: EVERYTHING AFTER THIS POINT IS AN OLD SOLUTION. I PUT IT HERE SO YOU COULD SEE THE THOUGHT PROCESS BUT NOT NECCESARRY AT ALL
"""
def robot_distance(state, boxes):
    index =0
    l=[]
    robot_dist={}
    for robot in state.robots:
        l.append(robot)
        robot_dist[robot]=0
    while index< len(l):  
            tile= l[index]  
            directions =[0,0,0,0]  
            # if tile[1]!=state.height-1:  
            directions[0]= tile[0],max(0,tile[1]-1)  
            # if tile[1]!=0:  
            directions[1]=tile[0],min(state.height-1, tile[1]+1)  
            # if tile[0]!= state.width-1:  
            directions[2]=max(0,tile[0]-1),tile[1]  
            # if tile[0]!=0:  
            directions[3]= min(state.width-1, tile[0]+1), tile[1]  
            for direction in directions: 
                if direction not in robot_dist and direction not in state.obstacles and direction not in boxes:  
                    robot_dist[direction]= robot_dist[tile]+1  
                    l.append(direction) 
                # elif direction not in robot_dist and direction in state.boxes:

            index+=1 
    return robot_dist 
def heur_alternate_smart(state):
    index=0  
    robot_dist={}  
    l=[]  
    for robot in state.robots:  
        robot_dist[robot]=0  
        l.append(robot)  
    boxes=[]
    completed=[]
    box_storages={}
    for box in state.boxes:   
        boxes.append((box[0], box[1]))
        box_storages[box]=[]
    robot_distance(state, state.boxes)
    val=0
    flag= False
    for i in range(len(boxes)):
        # print(i)
        tmp= find_storage(state, robot_dist, i, completed, boxes, box_storages)
        boxes=tmp[2]
        # for box in state.boxes:   
        #     boxes.append((box[0], box[1]))
        val+=tmp[0]
        if not tmp[1]:
            flag= True
    l=[]
    print(val, flag)
    print(state.state_string())
    if flag:
       
        G={"S":{}}
        for box in state.boxes:
            G["S"][box]=1
            G[box]={}
        for storage in state.storage:
            G[storage]= {"T":1}
        for box in box_storages.keys():
            for location in box_storages[box]:
                # if box not in G:
                #     print(box_storages[box])
                #     G[box]= {location[0]:1}
                # else:
                # print(location)
                G[box][location[0]]=1
        # print(G)
        # print(state.state_string())
        # for key, item in box_storages.items():
        #     print(key, item)
        # print(box_storages)
        f =ford_fulkerson(G, "S", "T", l)
        val =0
        dist =0
        for edge in f.keys():
            if edge[0] ==0:
                val+=f[edge]
                # print(edge)
        # print("matching", tmp)
        # print(val, len(state.boxes))
        if val != len(state.boxes):
            return float('inf')
        
        print(l)
    return val
def search(state, queue, robot_dist, visited):
    index=0
    blocked=[]
    print(queue[0], visited)
    while index< len(queue):  
        # print(queue[index])
        tile = queue[index][0]
        boxes= queue[index][1] 
        # print(boxes)
        robot_dist= robot_distance(state, boxes)
        print(robot_dist)
        # print(tile)  
        directions =[0,0,0,0]  
        if tile[1]!=state.height-1:  
            if (tile[0], tile[1]+1) in robot_dist:  
                directions[0]= tile[0],max(0,tile[1]-1)  
                
        if tile[1]!=0:  
            if (tile[0], tile[1]-1) in robot_dist:  
                directions[1]=tile[0],min(state.height-1, tile[1]+1)  
        if tile[0]!= state.width-1:  
            if (tile[0]+1, tile[1]) in robot_dist:  
                directions[2]=max(0,tile[0]-1),tile[1]  
        if tile[0]!=0:  
            if (tile[0]-1, tile[1]) in robot_dist:  
                directions[3]= min(state.width-1, tile[0]+1), tile[1]  
        # if tile in state.boxes:
        #     print(directions)
        for direction in directions:  
            if direction not in visited and direction!=0:  
                i = boxes.index(tile)
                # if direction not in state.obstacles and direction not in state.boxes:  
                if direction not in state.obstacles and direction not in boxes:
                    # queue.append(direction)
                    queue.append((direction, boxes[:i]+ [direction]+ boxes[i+1:]))  
                    # print(visited[tile])
                    visited[direction]=[visited[tile][0]+1]+ [visited[tile][1]+[direction]]  +[boxes[:i]+ [direction]+ boxes[i+1:]]
                    # print("H", visited[direction], len(visited[direction]))
                elif direction in boxes: 
                    # print(direction,tile, state.boxes)
                    up=(direction[0], direction[1]-1)
                    down= (direction[0], direction[1]+1)
                    left= (direction[0]-1, direction[1])
                    right = (direction[0]+1, direction[1])
                    # print("left {} right {} up {} down {}".format(left, right, up, down))
                    # print(up in robot_dist, down not in state.obstacles, down not in state.boxes,down[1]< state.height)
                    # print(down in robot_dist , up not in state.obstacles , up not in state.boxes , up[1]>=0)
                    # print(left in robot_dist , right not in state.obstacles , right not in state.boxes , right[0]< state.width)
                    # print(right in robot_dist , left not in state.obstacles , left not in state.boxes , left[0]>=0)
                    
                    
                    if len(visited[tile][1])!=1:
                        print(visited[tile])
                        print(visited[tile][1])
                        print(visited[visited[tile][1][-2]])
                        boxes=visited[visited[tile][1][-2]][-1]
                        robot_dist = robot_distance(state, visited[visited[tile][1][-2]][-1])
                    up_safe= up not in state.obstacles and up not in boxes and up[1]>=0
                    down_safe = down not in state.obstacles and down not in boxes and down[1]< state.height
                    left_safe =left not in state.obstacles and left not in boxes and left[0]>=0
                    right_safe= right not in state.obstacles and right not in boxes and right[0]< state.width
                    print(up_safe, down_safe, left_safe, right_safe)
                    print(robot_dist)
                    if up_safe and down_safe and (up in robot_dist or down in robot_dist):
                        choice = up
                        if choice not in robot_dist:
                            choice = down
                        # print("pushing down")
                        # print("before delete ", direction,choice,boxes)
                        
                        d= boxes.index(direction)
                        # print(i, d, boxes[:i], boxes[:d], boxes[i+1:], boxes[d+1:])
                        b= boxes[:i]+ [direction]+ boxes[i+1:]
                        # print(b,b[:d] ,b[d+1:])
                        b= b[:d]+ [down]+ b[d+1:]
                        # print("post delete", b)
                        visited[direction]=[visited[tile][0]+1+ 0.5*robot_dist[choice]]+ [visited[tile][1]+[direction]] +[b]
                        blocked.append((direction, b))
                    # elif down not in state.obstacles and down not in state.boxes and up not in state.obstacles and up not in state.boxes and up[1]>=0:
                    #     print("pushing up")
                    #     visited[direction]=[visited[tile][0]+1+ 0.5*robot_dist[down]]+ visited[tile][1:]+[direction] 
                    #     blocked.append(direction)
                    elif left_safe and right_safe and (left in robot_dist or right in robot_dist):
                        print("pushing right")
                        choice = right
                        if choice not in robot_dist:
                            choice = left
                        # print("before delete ", direction,choice,boxes)
                        d= boxes.index(direction)
                        # print(i, d, boxes[:i], boxes[:d], boxes[i+1:], boxes[d+1:])
                        b= boxes[:i]+ [direction]+ boxes[i+1:]
                        # print(b,b[:d] ,b[d+1:])
                        b= b[:d]+ [right]+ b[d+1:]
                        # print("post delete", b)
                        visited[direction]=[visited[tile][0]+1+ 0.5*robot_dist[choice]]+ [visited[tile][1]+[direction]] +[b]
                        blocked.append((direction,b))
                    # elif right in robot_dist and left not in state.obstacles and left not in state.boxes and left[0]>=0:
                    #     print("pushing left")
                    #     visited[direction]=[visited[tile][0]+1+ 0.5*robot_dist[right]]+ visited[tile][1:]+[direction] 
                    #     blocked.append(direction)
        index+=1
    # print(queue)
    if blocked!=[]:
        print("blocked")
        search(state, blocked, robot_dist, visited)
    print('done box')
    
    
def find_storage(state, robot_dist, box_index, completed, boxes, box_storages, move=False):
    # print(boxes)
    box= boxes[box_index][0], boxes[box_index][1]
    q= [(box, boxes)]
  
    visited={box:[0, [box],boxes]}
    search(state, q, robot_dist, visited)
    # dist.append([float('inf'), box, box])  
    # boxes_to_storages.append({})  
    dist=float('inf')
    flag= False
    count=0  
    completed.append(None)
    for location in state.storage:  
        if location in visited:
            box_storages[box].append((location, visited[location]))
        if location in visited and visited[location][0]< dist and location not in completed:  
            dist= visited[location][0]
            flag= True
            # print(location)
            # boxes[box_index][0]= location[0]
            # boxes[box_index][1]= location[1]
            completed[-1]= location
            boxes= visited[location][-1]
        # if location in visited:  
        #     boxes_to_storages[-1][box]= visited[location]  
        #     # print(distances[location])
        #     distances[box].append(visited[location])
        count+=1 
    # print(completed)
    if completed is None:
        completed.pop()
    print(dist)
    return dist, flag, boxes
def heur_alternate1(state):
    box_top_left=0
    box_top_right=0
    box_bot_left=0
    box_bot_right=0
    storage_bot_left=0
    storage_bot_right=0
    storage_top_left=0
    storage_top_right=0
    for box in state.boxes:
        box_top_left+= box[0]+box[1]
        box_top_right+=state.width-1-box[0]+box[1]
        box_bot_left+=box[0]+ state.height-1-box[1]
        box_bot_right+=state.width-1-box[0]+ state.height-1-box[1]
    for storage in state.storage:
        storage_top_left+= storage[0]+storage[1]
        storage_top_right+=state.width-1-storage[0]+storage[1]
        storage_bot_left+=storage[0]+ state.height-1-storage[1]
        storage_bot_right+=state.width-1-storage[0]+ state.height-1-storage[1]
    
    val= abs(box_top_left-storage_top_left)+ abs(box_top_right-storage_top_right)+abs(box_bot_left-storage_bot_left)+abs(box_bot_right-storage_bot_right)
    print("val: {} top left {} {} top right {} {} bot left {} {} bot right {} {}".format(val, box_top_left,  
    storage_top_left, box_top_right,  storage_top_right, box_bot_left, storage_top_left, box_bot_right, storage_top_right))
    return val
def heur_alternate2(state):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.
    # print(state.state_string())
    d={}
    l= []
    box_set={}
    count=0
    for box in state.boxes:
        box_set[(box[0], box[1])]= 1
        count+=1
    for storage in state.storage:
        # if (storage[0], storage[1]) in box_set:
        #     print(storage[0], storage[1], "how")
        #     count-=1
        d[(storage[0], storage[1])]=0
        if (storage[0], storage[1]) in box_set:
            count-=1
        # neighbours=[]
        # if storage[0]!=0:
        #     neighbours.append((storage[0]+1, storage[1]))
        # if storage[0]!= state.width-1:
        #     neighbours.append((storage[0]-1, storage[1]))
        # if storage[1]!=0:
        #     neighbours.append( (storage[0], storage[1]+1))
        # if storage[1]!= state.height-1:
        #     neighbours.append( (storage[0], storage[1]-1))
        neighbours = [(storage[0]+1, storage[1]), (storage[0]-1, storage[1]), (storage[0], storage[1]+1),(storage[0], storage[1]-1)]
        for x,y in neighbours:
            if 0<= x and x< state.width and 0<=y and y<state.height and (x,y) not in d and (x,y) not in state.storage:
                l.append((x, y, 1))
                d[(x,y)]=1
        # print(l)
        # print(d)
    for obstacle in state.obstacles:
        d[obstacle[0], obstacle[1]]= float('inf')
    index =0
    while index< len(l) and index< state.height* state.width and count>0:
        space= l[index]
        # print(space)
        # print(d)
        # print(l)
        if (space[0], space[1]) in box_set:
            # print(space[0], space[1], len(l))
            count-=1
        # if space[0]==0:
        #     if (space[0], space[1]-1) not in d or (space[0], space[1]+1) not in d:
        #         d[(space[0], space[1])]= float('inf')
        d[(space[0], space[1])]= space[2]
        # neighbours=[]
        # if space[0]!=0:
        #     neighbours.append((space[0]+1, space[1]))
        # if space[0]!= state.width-1:
        #     neighbours.append((space[0]-1, space[1]))
        # if space[1]!=0:
        #     neighbours.append( (space[0], space[1]+1))
        # if space[1]!= state.height-1:
        #     neighbours.append( (space[0], space[1]-1))
        # neighbours= [(space[0]+1, space[1]), (space[0]-1, space[1]), (space[0], space[1]+1),(space[0], space[1]-1)]
        for x,y in neighbours:
            if (x,y) not in d and 0<= x and x< state.width and 0<=y and y<state.height:
                l.append((x, y, space[2]+1))
                d[(x,y)]= space[2]+1
            # l.append((space[0]+1, space[1],space[2]+1))
            # l.append((space[0]-1, space[1],space[2]+1))
            # l.append((space[0], space[1]+1,space[2]+1))
            # l.append((space[0], space[1]-1,space[2]+1))
        index+=1
    cost=0
    # print(state.width, state.height)
    # for o in state.obstacles:
    #     print(o[0], o[1])
    # print(state.obstacles)
    # print(box_set, count)
    # print(l)
    for box in state.boxes:
        if box in d:
            cost+=d[box]
        else:
            print(state.state_string())
            print(box)
            return float('inf')
    # print(cost)
    
    return cost

def tr(G):  # Transpose (reverse edges of) G
  GT = {}  # GT is transpose of G
  for u in G:
    if u not in GT:
      GT[u] = set()
    for v in G[u]:
      if v not in GT:
        GT[v] = set()
      GT[v].add(u)  # Add reverse edge
  return GT

def bfs_aug(G, GT, s, t, flow):
  tree = {s: None}  # BFS tree
  Q = deque([s])
  min_on_path = {s: float('inf')}  # residual capacity of path ending at each vertex

  def process(capacity, u, v):  # consider (u, v) for tree
    if v in tree or capacity <= 0:
      return
    min_on_path[v] = min(min_on_path[u], capacity)
    tree[v] = u  # store predecessor of v
    Q.append(v)

  while Q:
    u = Q.popleft()
    if u == t:
      return tree, min_on_path[t]
    for v in G[u]:
      process(G[u][v]-flow[u,v], u, v)  # forward edges
    for v in GT[u]:
      process(flow[v,u], u, v)  # backward edges
  return None, 0 # No augmenting path found

def ford_fulkerson(G, s, t, paths,aug=bfs_aug):
  GT = tr(G)  # transpose of G
  flow = defaultdict(int)
  while True:
    tree, capacity = aug(G, GT, s, t, flow)
    if capacity == 0:  # no more augmenting paths
      return flow
    u = t  # Start augmentation
    while u != s:  # Backtrack to s
      u, v = tree[u], u  # Shift one step
      if v in G[u]: # forward edge
        flow[u,v] += capacity
        paths.append((u,v))
      else:  # backward edge
        flow[v,u] -= capacity


