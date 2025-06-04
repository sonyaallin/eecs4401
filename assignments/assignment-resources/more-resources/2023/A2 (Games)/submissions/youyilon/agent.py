"""
An AI player for Mancala.

The heuristic tries to make the program prefer states that allow capturing enemy pieces by moving to a blank slot,
and avoid states that allow the opponent to do so, determined by the max number of pieces that can be
captured in one step.
"""

# Some potentially helpful libraries
import random
import math
import time

# You can use the functions in mancala_game to write your AI. Import methods you need.
from mancala_game import Board, get_possible_moves, eprint, play_move, MCTS

cache={} # Use this variable for your state cache; Use it if caching is on

# Implement the below functions. You are allowed to define additional functions that you believe will come in handy.
def compute_utility(board, side):
    # IMPLEMENT!
    """
    Method to compute the utility value of board. This is equal to the number of stones of the mancala
    of a given player, minus the number of stones in the opposing player's mancala.
    INPUT: a game state, the player that is in control
    OUTPUT: an integer that represents utility
    """
    return board.mancalas[side] - board.mancalas[1 - side]


def compute_heuristic(board, color):
    # IMPLEMENT!
    """
    Method to compute the heuristic value of a specific state of the board.
    INPUT: a game state, the player that is in control, the depth limit for the search
    OUTPUT: an integer that represents heuristic value
    """
    heuristic = compute_utility(board, color)
    max_captured = 0
    for move in get_possible_moves(board, 1 - color):
        cc_opp = can_capture(board, 1 - color, move)
        if cc_opp[0] and cc_opp[1] > max_captured:
            max_captured = cc_opp[1]
        heuristic -= max_captured + 1
    max_capture = 0
    for move in get_possible_moves(board, color):
        cc_self = can_capture(board, color, move)
        if cc_self[0] and cc_self[1] > max_capture:
            max_capture = cc_self[1]
        heuristic += max_capture + 1
    return heuristic


def can_capture(board, color, move):
    num_pkts = len(board.pockets[1])
    circle_length = 2 * num_pkts + 1
    target_pkt = move + board[move]
    if target_pkt >= circle_length:
        target_pkt -= circle_length  # index after circling around the board
    if color == 0:
        target_pkt = num_pkts - 1 - target_pkt
    return (0 <= target_pkt < num_pkts and board.pockets[color][target_pkt] == 0
            and board.pockets[1 - color][target_pkt] > 0, board.pockets[1 - color][target_pkt])


################### MINIMAX METHODS ####################
def select_move_minimax(board, color, limit=-1, caching=False):
    # IMPLEMENT!
    """
    Given a board and a player color, decide on a move using the MINIMAX ALGORITHM. The return value is 
    an integer i, where i is the pocket that the player on side 'color' should select.
    INPUT: a game state, the player that is in control, the depth limit for the search, and a boolean that determines whether state caching is on or not
    OUTPUT: an integer that represents a move
    """
    move = minimax_helper(board, color, "max", limit, caching)
    return move[0]


def is_terminal(board: Board):
    """Checks whether the game is finished and return True if at least one player's pockets are all empty,
    return False otherwise.
    """
    return len(get_possible_moves(board, 0)) == 0 or len(get_possible_moves(board, 1)) == 0


def minimax_helper(board: Board, player: int, strat: str, limit: int, caching:bool) -> (int, int):
    """The minimax algorithm.
    @param board: a game state
    @param player: an integer representing the current player
    @param strat: represents the player strategy, can be "max" or "min"
    @param limit: the depth limit for the search
    @param caching: whether caching is used
    @return: a tuple of integers representing the best move and its utility according to strat.
    """
    if caching and (board, strat) in cache:
        return cache[(board, strat)]

    best_move = -1
    if limit == 0:
        util = compute_utility(board, player)
        return best_move, util
    if is_terminal(board):
        util = compute_utility(board, player)
        return best_move, util

    if strat == "max":
        maximum = -math.inf
        for i in get_possible_moves(board, player):
            util = minimax_helper(play_move(board, player, i), player, "min", limit - 1, caching)[1]
            if util > maximum:
                maximum = util
                best_move = i
        if caching and (board, strat) not in cache:
            cache[(board, strat)] = [best_move, maximum]
        return best_move, maximum
    elif strat == "min":
        minimum = math.inf
        for i in get_possible_moves(board, 1 - player):
            util = minimax_helper(play_move(board, 1 - player, i), player, "max", limit - 1, caching)[1]
            if util < minimum:
                minimum = util
                best_move = i
        if caching and (board, strat) not in cache:
            cache[(board, strat)] = [best_move, minimum]
        return best_move, minimum


################### ALPHA-BETA METHODS ####################
def select_move_alphabeta(board, color, limit=-1, caching=False):
    # IMPLEMENT!
    """
    Given a board and a player color, decide on a move using the ALPHABETA ALGORITHM. The return value is 
    an integer i, where i is the pocket that the player on side 'color' should select.
    INPUT: a game state, the player that is in control, the depth limit for the search, and a boolean that determines if state caching is on or not
    OUTPUT: an integer that represents a move
    """
    move = alphabeta_helper(board, color, -math.inf, math.inf, "max", limit, caching)[0]
    return move


def alphabeta_helper(board, color, alpha, beta, strat, limit, caching):
    if caching and (board, strat) in cache:
        return cache[(board, strat)]

    if limit == 0:
        return -1, compute_utility(board, color)
    if is_terminal(board):
        return -1, compute_utility(board, color)
    if strat == "max":
        util = -math.inf
        move = -1
        for i in get_possible_moves(board, color):
            result = alphabeta_helper(play_move(board, color, i), color, alpha, beta, "min", limit - 1, caching)[1]
            if util < result:
                util = result
                move = i
            if util > alpha:
                alpha = util
                if beta <= alpha:
                    break
        if caching and (board, strat) not in cache:
            cache[(board, strat)] = [move, util]
        return move, util
    elif strat == "min":
        util = math.inf
        move = -1
        for i in get_possible_moves(board, 1 - color):
            result = alphabeta_helper(play_move(board, 1 - color, i), color, alpha, beta, "max", limit - 1, caching)[1]
            if util > result:
                util = result
                move = i
            if util < beta:
                beta = util
                if beta <= alpha:
                    break
        if caching and (board, strat) not in cache:
            cache[(board, strat)] = [move, util]
        return move, util


################### MCTS METHODS ####################
def ucb_select(board, mcts_tree):
    # IMPLEMENT! This is the only function of MCTS that will be marked as a part of the assignment. Feel free to implement the others, but only if you like.
    """
    Given a board and its MCTS tree, select and return the successive state with the highest UCB
    INPUT: a board state and an MCTS tree
    OUTPUT: the successive state of the input board that corresponds with the max UCB value in the tree.
    """
    # Hint: You can encode this as follows:
    # 1. Cycle thru the successors of the given board.
    # 2. Calculate the UCB values for the successors, given the input tree
    # 3. Return the successor with the highest UCB value
    max_ucb = -1
    selected_board = None
    for successor in mcts_tree.successors[board]:
        if mcts_tree.counts[successor] == 0:
            ucb = math.inf
        else:
            ucb = mcts_tree.rewards[successor] + mcts_tree.weight * \
                  math.sqrt(math.log(mcts_tree.counts[board])/mcts_tree.counts[successor])
        if ucb > max_ucb:
            max_ucb = ucb
            selected_board = successor
    return selected_board

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
    