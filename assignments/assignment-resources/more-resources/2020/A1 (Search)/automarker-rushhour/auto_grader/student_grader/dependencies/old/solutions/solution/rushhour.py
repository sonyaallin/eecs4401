#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete the warehouse domain.

'''
rushhour STATESPACE
'''
#   You may add only standard python imports---i.e., ones that are automatically
#   available on CDF.
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

from dependencies.search import *
from random import Random
from string import ascii_lowercase as names

random_object = Random()
random_object.seed("arbitrary seed to ensure all students use the same test cases")
randint = random_object.randint

##################################################
# The search space class 'rushhour'             #
# This class is a sub-class of 'StateSpace'      #
##################################################


class Vehicle(object):
    def __init__(self, name, loc, length, is_horizontal, is_goal):
        self.name = name
        self.loc = loc
        self.length = length
        self.is_horizontal = is_horizontal
        self.is_goal = is_goal

    def copy_and_update_loc(self, loc):
        copy_of_self = Vehicle(self.name, loc, self.length, self.is_horizontal, self.is_goal)
        return copy_of_self


class rushhour(StateSpace):
    def __init__(self, action, gval, parent, board_properties, vehicle_list):
        """Initialize a rushhour search state object."""
        StateSpace.__init__(self=self, action=action, gval=gval, parent=parent)
        self.board_properties = board_properties
        self.vehicle_list = vehicle_list

    def successors(self):
        '''Return list of rushhour objects that are the successors of the current object'''
        def get_occupancy_grid(board_size, vehicle_statuses):
            (m, n) = board_size
            board = [list([False] * n) for i in range(m)]
            for vs in vehicle_statuses:
                for i in range(vs[2]):  # vehicle length
                    if vs[3]:
                        # vehicle is horizontal
                        board[vs[1][1]][(vs[1][0] + i) % n] = True
                    else:
                        # vehicle is vertical
                        board[(vs[1][1] + i) % m][vs[1][0]] = True
            return board

        def get_north_succs(occupancy_grid, vehicle_list, board_properties):
            board_size = board_properties[0]
            states = list()
            for vehicle in vehicle_list:
                if vehicle.is_horizontal or (vehicle.length != board_size[0] and occupancy_grid[(vehicle.loc[1] - 1) % board_size[0]][vehicle.loc[0]]):
                    continue
                else:
                    new_vehicle = vehicle.copy_and_update_loc((vehicle.loc[0], (vehicle.loc[1] - 1) % board_size[0]))
                    new_vehicle_list = list(vehicle_list)
                    new_vehicle_list.remove(vehicle)
                    new_vehicle_list.append(new_vehicle)
                    states.append(rushhour(action='move_vehicle({}, N)'.format(vehicle.name),
                                           gval=self.gval + 1,
                                           parent=self,
                                           board_properties=board_properties,
                                           vehicle_list=new_vehicle_list))
            return states

        def get_south_succs(occupancy_grid, vehicle_list, board_properties):
            board_size = board_properties[0]
            states = list()
            for vehicle in vehicle_list:
                if vehicle.is_horizontal or (vehicle.length != board_size[0] and occupancy_grid[(vehicle.loc[1] + vehicle.length) % board_size[0]][vehicle.loc[0]]):
                    continue
                else:
                    new_vehicle = vehicle.copy_and_update_loc((vehicle.loc[0], (vehicle.loc[1] + 1) % board_size[0]))
                    new_vehicle_list = list(vehicle_list)
                    new_vehicle_list.remove(vehicle)
                    new_vehicle_list.append(new_vehicle)
                    states.append(rushhour(action='move_vehicle({}, S)'.format(vehicle.name),
                                           gval=self.gval + 1,
                                           parent=self,
                                           board_properties=board_properties,
                                           vehicle_list=new_vehicle_list))
            return states

        def get_west_succs(occupancy_grid, vehicle_list, board_properties):
            board_size = board_properties[0]
            states = list()
            for vehicle in vehicle_list:
                if not vehicle.is_horizontal or (vehicle.length != board_size[1] and occupancy_grid[vehicle.loc[1]][(vehicle.loc[0] - 1) % board_size[1]]):
                    continue
                else:
                    new_vehicle = vehicle.copy_and_update_loc(((vehicle.loc[0] - 1) % board_size[1], vehicle.loc[1]))
                    new_vehicle_list = list(vehicle_list)
                    new_vehicle_list.remove(vehicle)
                    new_vehicle_list.append(new_vehicle)
                    states.append(rushhour(action='move_vehicle({}, W)'.format(vehicle.name),
                                           gval=self.gval + 1,
                                           parent=self,
                                           board_properties=board_properties,
                                           vehicle_list=new_vehicle_list))
            return states

        def get_east_succs(occupancy_grid, vehicle_list, board_properties):
            board_size = board_properties[0]
            states = list()
            for vehicle in vehicle_list:
                if not vehicle.is_horizontal or (vehicle.length != board_size[1] and occupancy_grid[vehicle.loc[1]][(vehicle.loc[0] + vehicle.length) % board_size[1]]):
                    continue
                else:
                    new_vehicle = vehicle.copy_and_update_loc(((vehicle.loc[0] + 1) % board_size[1], vehicle.loc[1]))
                    new_vehicle_list = list(vehicle_list)
                    new_vehicle_list.remove(vehicle)
                    new_vehicle_list.append(new_vehicle)
                    states.append(rushhour(action='move_vehicle({}, E)'.format(vehicle.name),
                                           gval=self.gval + 1,
                                           parent=self,
                                           board_properties=board_properties,
                                           vehicle_list=new_vehicle_list))
            return states

        occupancy_grid = get_occupancy_grid(self.board_properties[0], self.get_vehicle_statuses())
        return list(get_north_succs(occupancy_grid, self.vehicle_list, self.board_properties)
                + get_south_succs(occupancy_grid, self.vehicle_list, self.board_properties)
                + get_east_succs(occupancy_grid, self.vehicle_list, self.board_properties)
                + get_west_succs(occupancy_grid, self.vehicle_list, self.board_properties))

    def hashable_state(self):
#IMPLEMENT
        '''Return a data item that can be used as a dictionary key to UNIQUELY represent the state.'''
        return tuple(sorted([tuple(status) for status in self.get_vehicle_statuses()]))

    def print_state(self):
        #DO NOT CHANGE THIS FUNCTION---it will be used in auto marking
        #and in generating sample trace output.
        #Note that if you implement the "get" routines
        #(rushhour.get_vehicle_statuses() and rushhour.get_board_size())
        #properly, this function should work irrespective of how you represent
        #your state.

        if self.parent:
            print("Action= \"{}\", S{}, g-value = {}, (From S{})".format(self.action, self.index, self.gval, self.parent.index))
        else:
            print("Action= \"{}\", S{}, g-value = {}, (Initial State)".format(self.action, self.index, self.gval))

        print("Vehicle Statuses")
        for vs in sorted(self.get_vehicle_statuses()):
            print("    {} is at ({}, {})".format(vs[0], vs[1][0], vs[1][1]), end="")
        board = get_board(self.get_vehicle_statuses(), self.get_board_properties())
        print('\n')
        print('\n'.join([''.join(board[i]) for i in range(len(board))]))

#Data accessor routines.

    def get_vehicle_statuses(self):
#IMPLEMENT
        '''Return list containing the status of each vehicle
           This list has to be in the format: [vs_1, vs_2, ..., vs_k]
           with one status list for each vehicle in the state.
           Each vehicle status item vs_i is itself a list in the format:
                 [<name>, <loc>, <length>, <is_horizontal>, <is_goal>]
           Where <name> is the name of the robot (a string)
                 <loc> is a location (a pair (x,y)) indicating the front of the vehicle,
                       i.e., its length is counted in the positive x- or y-direction
                       from this point
                 <length> is the length of that vehicle
                 <is_horizontal> is true iff the vehicle is oriented horizontally
                 <is_goal> is true iff the vehicle is a goal vehicle
        '''
        statuses = list()
        for vehicle in self.vehicle_list:
            statuses.append([vehicle.name, vehicle.loc, vehicle.length, vehicle.is_horizontal, vehicle.is_goal])
        return statuses

    def get_board_properties(self):
#IMPLEMENT
        '''Return (board_size, goal_entrance, goal_direction)
           where board_size = (m, n) is the dimensions of the board (m rows, n columns)
                 goal_entrance = (x, y) is the location of the goal
                 goal_direction is one of 'N', 'E', 'S' or 'W' indicating
                                the orientation of the goal
        '''
        return self.board_properties

#############################################
# heuristics                                #
#############################################


def heur_zero(state):
    '''Zero Heuristic use to make A* search perform uniform cost search'''
    return 0


def heur_min_moves(state):
#IMPLEMENT
    '''rushhour heuristic'''
    #We want an admissible heuristic. Getting to the goal requires
    #one move for each tile of distance.
    #Since the board wraps around, there are two different
    #directions that lead to the goal.
    #NOTE that we want an estimate of the number of ADDITIONAL
    #     moves required from our current state
    #1. Proceeding in the first direction, let MOVES1 =
    #   number of moves required to get to the goal if it were unobstructed
    #2. Proceeding in the second direction, let MOVES2 =
    #   number of moves required to get to the goal if it were unobstructed
    #
    #Our heuristic value is the minimum of MOVES1 and MOVES2 over all goal vehicles.
    #You should implement this heuristic function exactly, even if it is
    #tempting to improve it.
    distances = list()
    (board_size, goal_entrance, goal_direction) = state.board_properties
    for vehicle in state.vehicle_list:
        if vehicle.is_goal:
            # check if can reach goal
            if (vehicle.is_horizontal and
               (goal_direction == 'W' or
                goal_direction == 'E') and
                vehicle.loc[1] == goal_entrance[1]):
                if goal_direction == 'W':
                    # positive direction
                    distances.append((goal_entrance[0] - vehicle.loc[0]) % board_size[1])
                    # negative direction
                    distances.append((vehicle.loc[0] - goal_entrance[0]) % board_size[1])
                elif goal_direction == 'E':
                    # positive direction
                    distances.append((goal_entrance[0] - (vehicle.loc[0] + vehicle.length - 1)) % board_size[1])
                    # negative direction
                    distances.append(((vehicle.loc[0] + vehicle.length - 1) - goal_entrance[0]) % board_size[1])
                assert distances
            elif (not vehicle.is_horizontal and
               (goal_direction == 'N' or
                goal_direction == 'S') and
                vehicle.loc[0] == goal_entrance[0]):
                if goal_direction == 'N':
                    # positive direction
                    distances.append((goal_entrance[1] - vehicle.loc[1]) % board_size[0])
                    # negative direction
                    distances.append((vehicle.loc[1] - goal_entrance[1]) % board_size[0])
                elif goal_direction == 'S':
                    # positive direction
                    distances.append((goal_entrance[1] - (vehicle.loc[1] + vehicle.length - 1)) % board_size[0])
                    # negative direction
                    distances.append(((vehicle.loc[1] + vehicle.length - 1) - goal_entrance[1]) % board_size[0])
                assert distances
    return min(distances)


def rushhour_goal_fn(state):
#IMPLEMENT
    '''Have we reached a goal state'''
    if state.board_properties[2] == 'N':
        for vehicle in state.vehicle_list:
            if (vehicle.is_goal and not vehicle.is_horizontal
                and vehicle.loc[0] == state.board_properties[1][0]
                and vehicle.loc[1] == state.board_properties[1][1]):
                return True
        return False
    elif state.board_properties[2] == 'S':
        for vehicle in state.vehicle_list:
            if (vehicle.is_goal and not vehicle.is_horizontal
                and vehicle.loc[0] == state.board_properties[1][0]
                and (vehicle.loc[1] + vehicle.length - 1) % state.board_properties[0][0] == state.board_properties[1][1]):
                return True
        return False
    elif state.board_properties[2] == 'W':
        for vehicle in state.vehicle_list:
            if (vehicle.is_goal and vehicle.is_horizontal
                and vehicle.loc[0] == state.board_properties[1][0]
                and vehicle.loc[1] == state.board_properties[1][1]):
                return True
        return False
    elif state.board_properties[2] == 'E':
        for vehicle in state.vehicle_list:
            if (vehicle.is_goal and vehicle.is_horizontal
                and (vehicle.loc[0] + vehicle.length - 1) % state.board_properties[0][1] == state.board_properties[1][0]
                and vehicle.loc[1] == state.board_properties[1][1]):
                return True
        return False
    else:
        raise Exception('invalid goal orientation')


def make_init_state(board_size, vehicle_list, goal_entrance, goal_direction):
#IMPLEMENT
    '''Input the following items which specify a state and return a rushhour object
       representing this initial state.
         The state's its g-value is zero
         The state's parent is None
         The state's action is the dummy action "START"
       board_size = (m, n)
          m is the number of rows in the board
          n is the number of columns in the board
       vehicle_list = [v1, v2, ..., vk]
          a list of vehicles. Each vehicle vi is itself a list
          vi = [vehicle_name, (x, y), length, is_horizontal, is_goal] where
              vehicle_name is the name of the vehicle (string)
              (x,y) is the location of that vehicle (int, int)
              length is the length of that vehicle (int)
              is_horizontal is whether the vehicle is horizontal (Boolean)
              is_goal is whether the vehicle is a goal vehicle (Boolean)
      goal_entrance is the coordinates of the entrance tile to the goal and
      goal_direction is the orientation of the goal ('N', 'E', 'S', 'W')

   NOTE: for simplicity you may assume that
         (a) no vehicle name is repeated
         (b) all locations are integer pairs (x,y) where 0<=x<=n-1 and 0<=y<=m-1
         (c) vehicle lengths are positive integers
    '''
    return rushhour('START', 0, None, [board_size, goal_entrance, goal_direction],
        [Vehicle(*v) for v in vehicle_list])

########################################################
#   Functions provided so that you can more easily     #
#   Test your implementation                           #
########################################################


def get_board(vehicle_statuses, board_properties):
    #DO NOT CHANGE THIS FUNCTION---it will be used in auto marking
    #and in generating sample trace output.
    #Note that if you implement the "get" routines
    #(rushhour.get_vehicle_statuses() and rushhour.get_board_size())
    #properly, this function should work irrespective of how you represent
    #your state.
    (m, n) = board_properties[0]
    board = [list(['.'] * n) for i in range(m)]
    for vs in vehicle_statuses:
        for i in range(vs[2]):  # vehicle length
            if vs[3]:
                # vehicle is horizontal
                board[vs[1][1]][(vs[1][0] + i) % n] = vs[0][0]
                # represent vehicle as first character of its name
            else:
                # vehicle is vertical
                board[(vs[1][1] + i) % m][vs[1][0]] = vs[0][0]
                # represent vehicle as first character of its name
    # print goal
    board[board_properties[1][1]][board_properties[1][0]] = board_properties[2]
    return board


def make_rand_init_state(nvehicles, board_size, ngoal_vehicles=1):
    '''Generate a random initial state containing
       nvehicles = number of vehicles
       board_size = (m,n) size of board
       Warning: may take a long time if the vehicles nearly
       fill the entire board. May run forever if finding
       a configuration is infeasible. Also will not work any
       vehicle name starts with a period.

       You may want to expand this function to create test cases.
    '''

    (m, n) = board_size
    vehicle_list = []
    board_properties = [board_size, None, None]
    for i in range(nvehicles):
        if i == 0:
            # make the goal vehicle and goal
            x = randint(0, n - 1)
            y = randint(0, m - 1)
            is_horizontal = True if randint(0, 1) else False
            vehicle_list.append(['gv', (x, y), 2, is_horizontal, True])
            if is_horizontal:
                board_properties[1] = ((x + n // 2 + 1) % n, y)
                board_properties[2] = 'W' if randint(0, 1) else 'E'
            else:
                board_properties[1] = (x, (y + m // 2 + 1) % m)
                board_properties[2] = 'N' if randint(0, 1) else 'S'
        elif i < ngoal_vehicles:
            # make another goal vehicle
            board = get_board(vehicle_list, board_properties)
            if vehicle_list[0][3]: # goal vehicles are horizontal
                y = vehicle_list[0][1][1]
                conflict = True
                while conflict:
                    x = randint(0, n-1)
                    length = randint(2, n - vehicle_list[0][2] - 1)
                    conflict = False
                    for j in range(length):
                        if board[y][(x+j) % n] != '.':
                            conflict = True
                            break
                vehicle_list.append([names[i],(x,y),length,True,True])
            else:
                x = vehicle_list[0][1][0]
                conflict = True
                while conflict:
                    y = randint(0, m-1)
                    length = randint(2, n - vehicle_list[0][2] - 1)
                    conflict = False
                    for j in range(length):
                        if board[y][(x+j) % n] != '.':
                            conflict = True
                            break
                vehicle_list.append([names[i],(x,y),length,False,True])
        else:
            board = get_board(vehicle_list, board_properties)
            conflict = True
            while conflict:
                x = randint(0, n - 1)
                y = randint(0, m - 1)
                is_horizontal = True if randint(0, 1) else False
                length = randint(2, 3)
                if is_horizontal:
                    length = randint(2, n-1)
                else:
                    length = randint(2, m-1)
                conflict = False
                for j in range(length):  # vehicle length
                    if is_horizontal:
                        if board[y][(x + j) % n] != '.':
                            conflict = True
                            break
                    else:
                        if board[(y + j) % m][x] != '.':
                            conflict = True
                            break
            vehicle_list.append([str(i), (x, y), length, is_horizontal, False])

    return make_init_state(board_size, vehicle_list, board_properties[1], board_properties[2])


def test(nvehicles, board_size):
    s0 = make_rand_init_state(nvehicles, board_size)
    se = SearchEngine('astar', 'full')
    #se.trace_on(2)
    final = se.search(s0, rushhour_goal_fn, heur_min_moves)
