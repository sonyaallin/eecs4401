"""
An AI player for Mancala.
"""
# Explanation for my heuristic:
# My heuristic takes into account at the very leaf node when there are no more available moves for
# one player when their side has all empty pockets, the stones on the other side of the pocket 
# will be claimed by the other player.

# Some potentially helpful libraries
import random
import math
import time

# You can use the functions in mancala_game to write your AI. Import methods you need.
from mancala_game import Board, get_possible_moves, eprint, play_move, MCTS, end_game

cache={} # Use this variable for your state cache; Use it if caching is on

# Implement the below functions. You are allowed to define additional functions that you believe will come in handy.
def compute_utility(board, side):
    # IMPLEMENT! DONE
    """
    Method to compute the utility value of board. This is equal to the number of stones of the mancala
    of a given player, minus the number of stones in the opposing player's mancala.
    INPUT: a game state, the player that is in control
    OUTPUT: an integer that represents utility
    """
    mancalas = board.mancalas
    return mancalas[side] - mancalas[1 - side]

def compute_heuristic(board, color):
    # IMPLEMENT! DONE
    """
    Method to compute the heuristic value of a specific state of the board.
    INPUT: a game state, the player that is in control, the depth limit for the search
    OUTPUT: an integer that represents heuristic value
    """
    mancalas = board.mancalas
    pockets = board.pockets
    if (sum(pockets[color]) == 0) or (sum(pockets[1 - color]) == 0):
        return (mancalas[color] + sum(pockets[color])) - (mancalas[1 - color] + sum(pockets[1 - color]))
    return mancalas[color] - mancalas[1 - color]

################### MINIMAX METHODS ####################
def select_move_minimax(board, color, limit=-1, caching = False):
    # IMPLEMENT! DONE
    """
    Given a board and a player color, decide on a move using the MINIMAX ALGORITHM. The return value is 
    an integer i, where i is the pocket that the player on side 'color' should select.
    INPUT: a game state, the player that is in control, the depth limit for the search, and a boolean that determines whether state caching is on or not
    OUTPUT: an integer that represents a move
    """
    move, util = select_max(board, color, limit, caching)
    return move

def select_max(board, color, limit, caching):
    if caching and ((hash(board), color, limit, "max") in cache):
        return cache[(hash(board), color, limit, "max")]
    moves = get_possible_moves(board, color)
    if (not moves) or (limit == 0):
        return None, compute_utility(board, 1 - color)
    max_util = None
    for move in moves:
        m, util = select_min(play_move(board, color, move), 1 - color, limit - 1, caching)
        if (max_util is None) or (util > max_util):
            max_util = util
            max_move = move
    if caching:
        cache[(hash(board), color, limit, "max")] = max_move, max_util
    return max_move, max_util
    
def select_min(board, color, limit, caching):
    if caching and ((hash(board), color, limit, "min") in cache):
        return cache[(hash(board), color, limit, "min")]
    moves = get_possible_moves(board, color)
    if (not moves) or (limit == 0):
        return None, compute_utility(board, 1 - color)
    min_util = None
    for move in moves:
        m, util = select_max(play_move(board, color, move), 1 - color, limit - 1, caching)
        if (min_util is None) or (util < min_util):
            min_util = util
            min_move = move
    if caching:
        cache[(hash(board), color, limit, "min")] = min_move, min_util
    return min_move, min_util

################### ALPHA-BETA METHODS ####################
def select_move_alphabeta(board, color, limit=-1, caching = False):
    # IMPLEMENT! DONE
    """
    Given a board and a player color, decide on a move using the ALPHABETA ALGORITHM. The return value is 
    an integer i, where i is the pocket that the player on side 'color' should select.
    INPUT: a game state, the player that is in control, the depth limit for the search, and a boolean that determines if state caching is on or not
    OUTPUT: an integer that represents a move
    """
    move, util = select_max_prune(board, color, limit, caching, None)
    return move

def select_min_prune(board, color, limit, caching, curr_max):
    if caching and ((hash(board), color, limit, "min") in cache):
        return cache[(hash(board), color, limit, "min")]
    moves = get_possible_moves(board, color)
    if (not moves) or (limit == 0):
        return None, compute_utility(board, 1 - color)
    min_util = None
    for move in moves:
        m, util = select_max_prune(play_move(board, color, move), 1 - color, limit - 1, caching, min_util)
        if (min_util is None) or (util < min_util):
            min_util = util
            min_move = move
        if (curr_max is not None) and (min_util <= curr_max):
            return min_move, min_util
    if caching:
        cache[(hash(board), color, limit, "min")] = min_move, min_util
    return min_move, min_util

def select_max_prune(board, color, limit, caching, curr_min):
    if caching and ((hash(board), color, limit, "max") in cache):
        return cache[(hash(board), color, limit, "max")]
    moves = get_possible_moves(board, color)
    if (not moves) or (limit == 0):
        return None, compute_utility(board, 1 - color)
    max_util = None
    for move in moves:
        m, util = select_min_prune(play_move(board, color, move), 1 - color, limit - 1, caching, max_util)
        if (max_util is None) or (util > max_util):
            max_util = util
            max_move = move
        if (curr_min is not None) and (curr_min <= max_util):
            return max_move, max_util
    if caching:
        cache[(hash(board), color, limit, "max")] = max_move, max_util
    return max_move, max_util

################### MCTS METHODS ####################
def ucb_select(board, mcts_tree):
    # IMPLEMENT! This is the only function of MCTS that will be marked as a part of the assignment. Feel free to implement the others, but only if you like.
    # DONE
    """
    Given a board and its MCTS tree, select and return the successive state with the highest UCB
    INPUT: a board state and an MCTS tree
    OUTPUT: the successive state of the input board that corresponds with the max UCB value in the tree.
    """
    # Hint: You can encode this as follows:
    # 1. Cycle thru the successors of the given board.
    # 2. Calculate the UCB values for the successors, given the input tree
    # 3. Return the successor with the highest UCB value
    max_ucb_val = None
    result = None
    successors = mcts_tree.successors[board]
    for successor in successors:
        successor_board = successor[0]
        if successor_board in mcts_tree.counts:
            ucb_val = mcts_tree.rewards[successor_board] + mcts_tree.weight * math.sqrt(math.log(mcts_tree.counts[board]) / mcts_tree.counts[successor_board])
        else:
            ucb_val = math.inf
        if (max_ucb_val is None) or (ucb_val > max_ucb_val):
            max_ucb_val = ucb_val
            result = successor
    return result

#######################################################################
#######################################################################
####### IMPLEMENTATION OF ALL MCTS METHODS BELOW IS OPTIONAL ###############
#######################################################################
#######################################################################

def choose_move(board, color, mcts_tree):
    # IMPLEMENT! (OPTIONAL)
    '''choose a move'''
    '''INPUT: a game state, the player that is in control and an MCTS tree'''
    '''OUTPUT: a number representing a move for the player tat is in control'''
    # Encoding this method is OPTIONAL.  You will want it to
    # 1. See if a given game state is in the MCTS tree.
    # 2. If yes, return the move that is associated with the highest average reward in the tree (from the perspective of the player 'color')
    # 3. If no, return a random move
    raise RuntimeError("Method not implemented") # Replace this line!


def rollout(board, color, mcts_tree):
    # IMPLEMENT! (OPTIONAL)
    '''rollout the tree!'''
    '''INPUT: a game state that will be at the start of the path, the player that is in control and an MCTS tree (see class def in mancala_game)'''
    '''OUTPUT: nothing!  Just adjust the MCTS tree statistics as you roll out.'''
    # You will want it to:
    # 1. Find a path from the root of the tree to a leaf based on ucs stats (use select_path(board, color, mctsree))
    # 2. Expand the last state in that path and add all the successors to the tree (use expand_leaf(board, color, mctsree))
    # 3. Simulate game play from the final state to a terminal and derive the reward
    # 4. Back-propagate the reward all the way from the terminal to the root of the MCTS tree
    raise RuntimeError("Method not implemented") # Replace this line!


def select_path(board, color, mcts_tree):
    # IMPLEMENT! (OPTIONAL)
    '''Find a path from the root of the tree to a leaf based on ucs stats'''
    '''INPUT: a game state that will be at the start of the path, the player that is in control and an MCTS tree (see class def in mancala_game)'''
    '''OUTPUT: A list of states that leads from the root of the MCTS tree to a leaf.'''
    # You will want it to return a path from the board provided to a
    # leaf of the MCTS tree based on ucs stats (select_path(board, mctsree)). You can encode this as follows:
    # Repeat:
    # 1. Add the state to the path
    # 2. Check to see if the state is a terminal.  If yes, return the path.
    # 3. If no, check to see if any successor of the state is a terminal.  If yes, add any unexplored terminal to the path and return.
    # 5. If no, descend the MCTS tree a level to select a new state based on the UCT criteria.
    raise RuntimeError("Method not implemented") # Replace this line!

def expand_leaf(board, color, mcts_tree):
    # IMPLEMENT! (OPTIONAL)
    '''Expand a leaf in the mcts tree'''
    '''INPUT: a game state that will be at the start of the path, the player that is in control and an MCTS tree (see class def in mancala_game)'''
    '''OUTPUT: nothing!  Just adjust the MCTS tree statistics as you roll out.'''
    # If the given state already exists in the tree, do nothing
    # Else, add the successors of the state to the tree.
    raise RuntimeError("Method not implemented") # Replace this line!


def simulate(board, color):
    # IMPLEMENT! (OPTIONAL)
    '''simulate game play from a state to a leaf'''
    '''INPUT: a game state, the player that is in control'''
    '''OUTPUT: a reward that the controller of the tree can hope to get from this state!'''
    # You can encode this as follows:
    # 1. Get all the possible moves from the state. If there are none, return the reward that the player in control can expect to get from the state.
    # 2. Select a moves at random, and play it to generate a new state
    # 3. Repeat.
    # Remember:
    #  -- the reward the controlling player receives at one level will be the OPPOSITE of the reward at the next level!
    #  -- at one level the player in control will play a move, and at the next his or her opponent will play a move!
    raise RuntimeError("Method not implemented") # Replace this line!

def backprop(path, reward, mcts_tree):
    # IMPLEMENT! (OPTIONAL)
    '''backpropagate rewards a leaf to the root of the tree'''
    '''INPUT: the path leading from a state to a terminal, the reward to propagate, and an MCTS tree'''
    '''OUTPUT: nothing!  Just adjust the MCTS tree statistics as you roll out.'''
    # You can encode this as follows:
    # FROM THE BACK TO THE FRONT OF THE PATH:
    # 1. Update the number of times you've seen a given state in the MCTS tree
    # 2. Update the reward associated with that state in the MCTS tree
    # 3. Continue
    # Remember:
    #  -- the reward one level will be the OPPOSITE of the reward at the next level!  Make sure to update the rewards accordingly
    raise RuntimeError("Method not implemented") # Replace this line!

def select_move_mcts(board, color, weight=1, numsamples = 50):
    # IMPLEMENT! (OPTIONAL)
    mcts_tree = MCTS(weight) # Initialize your MCTS tree
    for _ in range(numsamples): # Sample the tree numsamples times
        # In here you'll want to encode a 'rollout' for each iteration
        # store the results of each rollout in the MCTS tree (mcts_tree)
        pass # Replace this line!

    # Then, at the end of your iterations, choose the best move, according to your tree (ie choose_move(board, color, mcts_tree))
    raise RuntimeError("Method not implemented") # Replace this line!

#######################################################################
#######################################################################
################### END OF OPTIONAL FUNCTIONS #########################
#######################################################################
#######################################################################

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
    CACHING = int(arguments[2]) # caching or no?
    algorithm = int(arguments[3])  # Minimax, Alpha Beta, or MCTS

    if (algorithm == 2): # Implement this only if you really want to!!
        eprint("Running MCTS")
        limit = -1  # Limit is irrelevant to MCTS!!
    elif (algorithm == 1):
        eprint("Running ALPHA-BETA")
    else:
        eprint("Running MINIMAX")

    if (CACHING == 1):
        eprint("Caching is ON")
    else:
        eprint("Caching is OFF")

    if (limit == -1):
        eprint("Depth Limit is OFF")
    else:
        eprint("Depth Limit is ", limit)

    while True:  # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()

        if status == "FINAL":  # Game is over.
            print
        else:
            pockets = eval(input())  # Read in the pockets on the board
            mancalas = eval(input())  # Read in the mancalas on the board
            board = Board(pockets, mancalas) #turn info into an object

            # Select the move and send it to the manager
            if (algorithm == 2):
                move = select_move_mcts(board, color, numsamples=50) #50 samples per iteration by default
            elif (algorithm == 1):
                move = select_move_alphabeta(board, color, limit, bool(CACHING))
            else:
                move = select_move_minimax(board, color, limit, bool(CACHING))

            print("{}".format(move))


if __name__ == "__main__":
    run_ai()
    
