"""
An AI player for Mancala.
"""

import random
import pickle
import math
import time

# You can use the functions in mancala_game to write your AI
from mancala_game import Board, get_possible_moves, eprint, play_move, MCTS

cache={} #use this for your state cache, if caching is on

#FOR DEBUGGING
counter = 0
CUTOFF = float('inf')
#CUTOFF = 25 <- use this for debugging

# Method to compute utility value of board
def compute_utility(board, side):
    return board.mancalas[1] - board.mancalas[0] if side == 1 else board.mancalas[0] - board.mancalas[1]

# Method to heuristic value of board, to be used if we are at a depth limit
def compute_heuristic(board, side):  # not implemented
    return board.mancalas[1] - board.mancalas[0] if side == 0 else board.mancalas[0] - board.mancalas[1]


################### MINIMAX METHODS ####################
def minimax_selection(board, color, MAX, limit, caching = False):

    #for debugging
    global counter
    if counter > CUTOFF: return None, compute_utility(board, MAX) #for debugging
    counter += 1

    opponent = 0 if color == 1 else 1

    # Get the allowed moves
    all_moves = get_possible_moves(board, color)

    # If there are no moves left, return the utility
    if len(all_moves) == 0 or limit == 0:  # If s is TERMINAL
        return None, compute_utility(board, MAX)  # Return terminal state's utility according to MAX

    # Else if there are moves, get their utility and return the min
    ut_val = float("-Inf") if color == MAX else float("Inf")
    move, best_move = None, None
    limit -= 1

    # Get the utility of all the moves
    for each in all_moves:  # ChildList = s.Successors(Player)

        # Get the next board from that move and add the moves to the list
        next_board = play_move(board, color, each)

        #if already in the cache, use the value
        if caching and (next_board, color) in cache:
            move, value = cache[(next_board, color)]
            #eprint("Saw the same state twice")
        else:
            move, value = minimax_selection(next_board, opponent, MAX, limit, caching)
            cache[(next_board, color)] = (move, value)

        #move, value = minimax_selection(next_board, opponent, MAX, limit)
        if (CUTOFF < float('inf')): eprint("each, move choice, value, ut_val -> {}, {} {} {}".format(each, move, value, ut_val))

        if color == MAX and value > ut_val:
            if (CUTOFF < float('inf')): eprint("in MAX update, best move is {}".format(each))
            ut_val = value
            best_move = each
        elif color != MAX and value < ut_val:
            if (CUTOFF < float('inf')): eprint("in MIN update")
            ut_val = value
            best_move = each

    if (CUTOFF < float('inf')): eprint("{} board -> {} {}, color {}, moves {}, move selected {} value {}. Currently at limit {}".format(counter, board.mancalas, board.pockets, color, all_moves, best_move, ut_val, limit))
    return best_move, ut_val

def select_move_minimax(board, color, limit=-1, caching = False):
    #eprint("in minimax, maximizer is {}".format(color))

    # Get the best move according to the max utility
    move, utility = minimax_selection(board, color, color, limit, caching)

    return move

################### ALPHA-BETA METHODS ####################
def alphabeta_selection(board, color, MAX, alpha, beta, limit, caching = False):

    #for debugging
    global counter
    if counter > CUTOFF:
        return None, compute_utility(board, MAX)
    counter += 1

    opponent = 0 if color == 1 else 1

    # Get the allowed moves
    all_moves = get_possible_moves(board, color)

    # If there are no moves left, return the utility
    if len(all_moves) == 0 or limit == 0:  # If s is TERMINAL
        return None, compute_utility(board, MAX), 0  # Return terminal state's utility according to MAX

    # Else if there are moves, get their utility and return the min
    ut_val = float("-Inf") if color == MAX else float("Inf")
    move, best_move = None, None
    limit -= 1

    # Get the utility of all the moves
    numcuts = 0
    for each in all_moves:  # ChildList = s.Successors(Player)
        # Get the next board from that move and add the moves to the list
        next_board = play_move(board, color, each)

        #if already in the cache, use the value
        if caching and (next_board, color) in cache:
            move, value = cache[(next_board, color)]
        else:
            move, value, cuts = alphabeta_selection(next_board, opponent, MAX, alpha, beta, limit, caching)
            numcuts += cuts
            cache[(next_board, color)] = (move, value)

        if (CUTOFF < float('inf')): eprint("each, move choice, value, ut_val -> {}, {} {} {} {} {}".format(each, move, value, ut_val, alpha, beta))

        if color == MAX and value > ut_val:
            if (CUTOFF < float('inf')): eprint("in MAX update, best move is {}".format(each))
            ut_val = value
            best_move = each
            if alpha < ut_val:
                numcuts += 1
                alpha = ut_val
                if beta <= alpha: break
        if color != MAX and value < ut_val:
            if (CUTOFF < float('inf')): eprint("in MIN update")
            ut_val = value
            best_move = each
            if beta > ut_val:
                numcuts += 1
                beta = ut_val
                if beta <= alpha: break

    if (CUTOFF < float('inf')): eprint("{} board -> {} {}, color {}, moves {}, move selected {} value {}. Currently at limit {}, alpha {} beta {}".format(counter, board.mancalas, board.pockets, color, all_moves, best_move, ut_val, limit, alpha, beta))
    return best_move, ut_val, numcuts

def select_move_alphabeta(board, color, limit=-1, caching = False):

    alpha = float("-Inf")
    beta = float("Inf")
    move, utility, num_cuts = alphabeta_selection(board, color, color, alpha, beta, limit, caching)
    return move, num_cuts

################### MCTS METHODS ####################
def choose_move(board, color, mctsree):
    all_moves = get_possible_moves(board, color)
    if len(all_moves) == 0: raise RuntimeError(f"choose called on terminal node {board}")

    if board not in mctsree.successors:
        move = random.choice(all_moves)
        return move

    def score(n):
        if mctsree.counts[n] == 0:
            return float("-inf")  # avoid unseen moves
        return mctsree.rewards[n] / mctsree.counts[n]  # average reward

    node = max(mctsree.successors[board], key=score)
    return node[1]

def rollout(board, color, mctsree):
    path = select_path(board[0], mctsree)
    #eprint("path")
    #eprint(path)
    leaf = extract_leaf(path)
    #eprint("leaf")
    #eprint(leaf)
    #eprint("before expanding leaf mctsree.successors")
    #eprint(mctsree.successors)
    expand_leaf(leaf, color, mctsree)
    reward = simulate(leaf, color)
    backprop(path, reward, mctsree)

def select_path(board, mctsree):
    path = []
    while True:
        path.append(board)
        #eprint(board)
        if board not in mctsree.successors or not mctsree.successors[board]:
            # node is either unexplored or terminal
            return path
        unexplored = []
        for node in mctsree.successors[board]:
            if node[0] not in mctsree.successors.keys():
                unexplored.append(node[0])
        if unexplored:
            #eprint("unexplored")
            #eprint(unexplored)
            n = unexplored.pop()
            path.append(n)
            return path
        board, move = uct_select(board, mctsree)  #descend a layer deeper

def extract_leaf(path):
    return path[-1]

def expand_leaf(board, color, mctsree):
    if board in mctsree.successors:
        return  # already expanded
    mctsree.successors[board] = find_children(board, color)
    #eprint("after expansion of {} mctsree.successors".format(board))
    #eprint(mctsree.successors)

def simulate(board, color):
    invert_reward = True
    while True:
        all_moves = get_possible_moves(board, color)
        if len(all_moves) == 0:
            reward = compute_utility(board, color)
            return 1 - reward if invert_reward else reward
        move = random.choice(all_moves)
        board = play_move(board, color, move)
        invert_reward = not invert_reward
        color = abs(color - 1)  # flip color

def backprop(path, reward, mctstree):
    #eprint(len(path))
    for board in reversed(path):
        mctstree.counts[board] += 1
        mctstree.rewards[board] += reward
        reward = 1 - reward

    #eprint("counts and rewards")
    #eprint(mctstree.counts)
    #eprint(mctstree.rewards)

def ucb_select(board, mcts):

    log_N_vertex = math.log(mcts.counts[board])

    def uct(n):
        n = n[0]
        "Upper confidence bound for trees"
        return mcts.rewards[n] / mcts.counts[n] + mcts.weight * math.sqrt(log_N_vertex / mcts.counts[n])

    return max(mcts.successors[board], key=uct)

def find_children(board, color):
    all_moves = get_possible_moves(board, color)
    if len(all_moves) == 0: return set()
    new_boards = []
    #eprint("all_moves {}".format(all_moves))
    for each in all_moves:
        new_boards.append((play_move(board, color, each), each))
    #eprint("new boards {}".format(new_boards))
    return new_boards

def select_move_mcts(board, color, weight=1):
    #successors = find_children(board, color)
    mctsree = MCTS(weight)
    for i in range(5): #sample the tree N times
        #eprint("rollout: " + str(i))
        #eprint(mctsree.successors.keys())
        rollout((board, -1), color, mctsree)
        #eprint(mctsree.successors.keys())
    #eprint(mctsree.successors[board])
    #eprint(successors)
    return choose_move(board, color, mctsree) #select a move

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Mancala AI")  # First line is the name of this AI
    arguments = input().split(",")

    color = int(arguments[0])  # Player color
    limit = int(arguments[1])  # Depth limit
    caching = int(arguments[2])  # Depth limit
    if (caching == 1): caching = True
    else: caching = False
    algorithm = int(arguments[3])  # Minimax, alpha beta, or MCTS

    if (algorithm == 2):
        eprint("Running MCTS")
        limit = -1  # limit is irrelevant to MCTS
        caching = False  # caching is irrelevant to MCTS
    elif (algorithm == 1):
        eprint("Running ALPHA-BETA")
    else:
        eprint("Running MINIMAX")

    if (limit == -1):
        eprint("Depth Limit is OFF")
    else:
        eprint("Depth Limit is ", limit)

    if (caching):
        eprint("Caching is ON")
    else:
        eprint("Caching is OFF")

    while True:  # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()

        if status == "FINAL":  # Game is over.
            print
        else:
            pockets = eval(input())  # Read in the input and turn it into an object
            mancalas = eval(input())  # Read in the input and turn it into an object
            board = Board(pockets, mancalas)

            # Select the move and send it to the manager
            if (algorithm == 2):
                move = select_move_mcts(board, color)
            elif (algorithm == 1):
                move, cuts = select_move_alphabeta(board, color, limit, caching)
            else:
                move = select_move_minimax(board, color, limit, caching)

            print("{}".format(move))


if __name__ == "__main__":
    run_ai()
