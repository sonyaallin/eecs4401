import os  # for time functions
import math  # for infinity

from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

import numpy


# Global Directions
UP = Direction("up", (0, -1))
DOWN = Direction("down", (0, 1))
LEFT = Direction("left", (-1, 0))
RIGHT = Direction("right", (1, 0))


# HELPER FUNCTIONS
def is_obstacle_or_wall(state, location):
    """Determines whether the given location is an obstacle/wall in the given state."""
    # if location is an obstacle
    if location in state.obstacles:
        return True

    # if location is a wall
    if location[0] == -1 or location[1] == -1 or location[0] == state.width or location[1] == state.height:
        return True

    return False


def edge_reverser(graph):
    """
    Reverses the edges of a given graph.

    Based on code given in CSC373.
    """
    reversed_graph = [set() for _ in range(len(graph))]

    for u in range(len(graph)):
        for v in graph[u]:
            reversed_graph[v].add(u)

    return reversed_graph


def get_augmenting_path(graph, reversed_graph, s, t, flow):
    """
    Gets an augmenting path using BFS.

    Based on code given in CSC373.
    """
    tree = {s: None}
    queue = deque([s])
    min_on_path = {s: math.inf}

    def process(capacity, n1, n2):
        if n2 in tree or capacity <= 0:
            return

        min_on_path[n2] = min(min_on_path[n1], capacity)
        queue.append(n2)
        tree[v] = n1

    while queue:
        u = queue.popleft()

        if u == t:
            return tree, min_on_path[t]

        for v in graph[u]:
            # forward edges
            process(1 - flow.get((u, v), 0), u, v)

        for v in reversed_graph[u]:
            # backward edges
            process(flow.get((v, u), 0), u, v)

    # no augmenting path found
    return None, 0


def ford_fulkerson(costs, s, t, flow):
    """
    Solves the max flow problem using the Ford-Fulkerson algorithm.
    Used in the Hungarian algorithm to select a feasible assignment.

    Based on code given in CSC373.
    """
    # construct a graph using the costs matrix
    graph = []

    for i in range(costs.shape[0]):
        graph += [set(numpy.nonzero(costs[i, :] == 0)[0] + costs.shape[0])]

    for i in range(costs.shape[0], s):
        graph += [{t}]

    graph += [set(numpy.arange(costs.shape[0]))]
    graph += [set()]

    reversed_graph = edge_reverser(graph)

    while True:
        tree, capacity = get_augmenting_path(graph, reversed_graph, s, t, flow)

        if capacity == 0:
            # no more augmenting paths
            return flow

        # start augmentation
        u = t

        # backtrack to s
        while u != s:
            # shift one step
            u, v = tree[u], u
            if v in graph[u]:
                # forward edge
                flow[u, v] = flow.get((u, v), 0) + capacity
            else:
                # backward edge
                flow[v, u] = flow.get((v, u), 0) - capacity


def get_optimal_assignment(costs):
    """Gets the optimal assignment for the given cost matrix."""
    s = costs.shape[0] + costs.shape[1]
    t = s + 1

    # start with trivial assignment
    flow = {}
    column_assigned = numpy.full(costs.shape[1], False)

    for i in range(costs.shape[0]):
        for j in numpy.nonzero(~column_assigned)[0]:
            if not costs[i, j]:
                flow[(i, j + costs.shape[0])] = 1
                column_assigned[j] = True
                break

    for u, v in flow.copy():
        flow[s, u] = 1
        flow[v, t] = 1

    # finalize assignment
    ford_fulkerson(costs, s, t, flow)

    row_assignments = numpy.full(costs.shape[0], -1)
    column_assigned = numpy.full(costs.shape[1], False)

    for i in range(costs.shape[0]):
        for j in numpy.nonzero(~column_assigned)[0]:
            if flow.get((i, j + costs.shape[0]), 0):
                row_assignments[i] = j
                column_assigned[j] = True
                break

    return row_assignments


def hungarian_algorithm(costs):
    """
    Solves the assignment problem using the Hungarian and Ford-Fulkerson algorithms.

    References:
    CSC373 (for Ford-Fulkerson)
    https://en.wikipedia.org/wiki/Hungarian_algorithm#Matrix_interpretation
    https://brilliant.org/wiki/hungarian-matching/#the-hungarian-algorithm-using-an-adjacency-matrix
    """
    costs = costs.copy()

    # steps 1 and 2
    costs = (costs.T - costs.min(1)).T
    costs -= costs.min(0)

    while True:
        row_assignments = get_optimal_assignment(costs)

        if numpy.count_nonzero(row_assignments != -1) == costs.shape[0]:
            return numpy.arange(costs.shape[0]), row_assignments

        # step 3
        zeros = costs == 0
        rows = row_assignments == -1
        columns = numpy.full(costs.shape[1], False)
        old_rows = numpy.full(costs.shape[0], False)
        old_columns = numpy.full(costs.shape[1], False)

        while not numpy.array_equal(rows, old_rows):
            prev_rows = rows.copy()
            prev_columns = columns.copy()

            for i in (rows & ~old_rows).nonzero()[0]:
                columns |= zeros[i, :]

            for i in (columns & ~old_columns).nonzero()[0]:
                rows[numpy.nonzero(row_assignments == i)[0]] = True

            old_rows = prev_rows
            old_columns = prev_columns

        if (numpy.count_nonzero(columns) + numpy.count_nonzero(~rows)) < costs.shape[0]:
            # step 4
            min_non_covered = numpy.min(costs[:, numpy.nonzero(~columns)[0]][numpy.nonzero(rows)[0], :])
            costs[:, numpy.nonzero(columns)[0]] += min_non_covered
            costs[numpy.nonzero(rows)[0], :] -= min_non_covered


# SOKOBAN HEURISTICS
def heur_alternate(state: SokobanState):
    """
    a better heuristic
    INPUT: a sokoban state
    OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.
    """
    # first, check if any of the boxes are in corners (instant fail)... very sad :(
    for box in state.boxes:
        if box in state.storage:
            continue

        up = is_obstacle_or_wall(state, UP.move(box))
        down = is_obstacle_or_wall(state, DOWN.move(box))
        left = is_obstacle_or_wall(state, LEFT.move(box))
        right = is_obstacle_or_wall(state, RIGHT.move(box))

        if (left and up) or (up and right) or (right and down) or (down and left):
            # this box is in a corner, return inf
            return math.inf

    # now, calculate the manhattan distance for each box to each storage
    costs = numpy.array([
        [abs(box[0] - storage[0]) + abs(box[1] - storage[1]) for storage in state.storage] for box in state.boxes
    ])

    # finally, solve the balanced assignment problem using the Hungarian algorithm
    assignments = hungarian_algorithm(costs)

    # this is just like heur_manhattan_distance, but only one box can be in any given storage location
    return numpy.sum(costs[assignments[0], assignments[1]])


def heur_zero(state):
    """Zero Heuristic can be used to make A* search perform uniform cost search."""
    return 0


def heur_manhattan_distance(state):
    """
    admissible sokoban puzzle heuristic: manhattan distance
    INPUT: a sokoban state
    OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.
    """
    total_distance = 0

    for box in state.boxes:
        total_distance += min([abs(box[0] - storage[0]) + abs(box[1] - storage[1]) for storage in state.storage])

    return total_distance


def fval_function(sN, weight):
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + weight * sN.hval


# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    """
    Provides an implementation of weighted a-star, as described in the HW1 handout
    INPUT: a sokoban state that represents the start state and a timebound (number of seconds)
    OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object
    implementation of weighted astar algorithm
    """
    se = SearchEngine('custom')
    se.init_search(initial_state, sokoban_goal_state, heur_fn, lambda sN: fval_function(sN, weight))
    return se.search(timebound)


def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):
    """
    Provides an implementation of realtime a-star, as described in the HW1 handout
    INPUT: a sokoban state that represents the start state and a timebound (number of seconds)
    OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object
    implementation of iterative astar algorithm
    """
    original_timebound = timebound
    se = SearchEngine('custom')
    final, stats = False, SearchStats(0, 0, 0, 0, 0)
    se.init_search(initial_state, sokoban_goal_state, heur_fn, lambda sN: fval_function(sN, weight))

    while timebound > 0 and weight >= 0:
        if not final:
            final, stats = se.search(timebound)
        else:
            new_final, stats = se.search(timebound, (math.inf, math.inf, final.gval))

            if new_final:
                final = new_final

        timebound -= stats.total_time
        weight *= 1 - (stats.total_time / original_timebound)

    return final, SearchStats(stats.states_expanded,
                              stats.states_generated,
                              stats.states_pruned_cycles,
                              stats.states_pruned_cost,
                              original_timebound - timebound)


def iterative_gbfs(initial_state, heur_fn, timebound=5):
    """
    Provides an implementation of anytime greedy best-first search, as described in the HW1 handout
    INPUT: a sokoban state that represents the start state and a timebound (number of seconds)
    OUTPUT: A goal state (if a goal is found), else False
    implementation of iterative gbfs algorithm
    """
    original_timebound = timebound
    se = SearchEngine('best_first')
    final, stats = False, SearchStats(0, 0, 0, 0, 0)
    se.init_search(initial_state, sokoban_goal_state, heur_fn)

    while timebound > 0:
        if not final:
            final, stats = se.search(timebound)
        else:
            new_final, stats = se.search(timebound, (final.gval, math.inf, math.inf))

            if new_final:
                final = new_final

        timebound -= stats.total_time

    return final, SearchStats(stats.states_expanded,
                              stats.states_generated,
                              stats.states_pruned_cycles,
                              stats.states_pruned_cost,
                              original_timebound - timebound)
