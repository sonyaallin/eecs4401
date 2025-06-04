"""
An AI player for Mancala.
"""

# Heuristic Explanation for compute_heuristic:
#-----------------------------------------------
# I kept the basic compute_utility part as a part of my heuristic and also added on the difference 
# in potential stones that could be captured. For each side, I find a pocket with some stones within it
# and then check each pocket to the right of it since stones are placed counterclockwise. For each pocket
# to the right, I check if it's empty and if the opposite side of the board has stones that can be taken.
# If there are stones then I add them to the a variable that keep track of the sum and mark that pocket
# as seen already to avoid duplication. I do the same process for the opponent and then take the difference
# in capture sums and finally add that onto the result from compute_utility.

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
    # Get the players stone count
    # Get opponents stone count
    # Get the difference between the counts and return
    p_stones = board.mancalas[side]
    o_stones = board.mancalas[(side-1) * -1]
    return p_stones - o_stones

def compute_heuristic(board, color):
    # IMPLEMENT!
    """
    Method to compute the heuristic value of a specific state of the board.
    INPUT: a game state, the player that is in control, the depth limit for the search
    OUTPUT: an integer that represents heuristic value
    """
    # p = player (color), o = opponent

    # Stones in mancalas
    p_stones = board.mancalas[color]
    o_stones = board.mancalas[(color-1) * -1]
    stone_diff = p_stones - o_stones

    p_pockets = board.pockets[color]
    o_pockets = board.pockets[(color-1) * -1]

    # Captures for player (color)
    p_captures = 0
    p_seen_captures = []
    last_pocket = len(p_pockets)-1
    for i in range(len(p_pockets)):
        if p_pockets[i] > 0:
            last_index = i + p_pockets[i]
            if last_index >= len(p_pockets):
                last_index = last_pocket
            for j in range(i+1, last_index+1):
                if p_pockets[j] == 0 and o_pockets[last_pocket-j] > 0 and last_pocket-j not in p_seen_captures:
                    p_captures = p_captures + o_pockets[last_pocket-j]
                    p_seen_captures.append(last_pocket-j)
    # Captures for opponent
    o_captures = 0
    o_seen_captures = []
    last_pocket = len(o_pockets)-1
    for i in range(len(o_pockets)):
        if o_pockets[i] > 0:
            last_index = i + o_pockets[i]
            if last_index >= len(o_pockets):
                last_index = last_pocket
            for j in range(i+1, last_index+1):
                if o_pockets[j] == 0 and p_pockets[last_pocket-j] > 0 and last_pocket-j not in o_seen_captures:
                    o_captures = o_captures + p_pockets[last_pocket-j]
                    o_seen_captures.append(last_pocket-j)
    
    captures_diff = p_captures - o_captures

    heuristic_val = stone_diff + captures_diff

    return heuristic_val

################### MINIMAX METHODS ####################
def select_move_minimax(board, color, limit=-1, caching = False):
    # IMPLEMENT!
    """
    Given a board and a player color, decide on a move using the MINIMAX ALGORITHM. The return value is 
    an integer i, where i is the pocket that the player on side 'color' should select.
    INPUT: a game state, the player that is in control, the depth limit for the search, and a boolean that determines whether state caching is on or not
    OUTPUT: an integer that represents a move
    """

    best_move = 0
    other_color = (color-1)*-1

    if caching and (board, color, True, limit) in cache:
        return cache[(board, color, True, limit)]

    moves = get_possible_moves(board, color)

    if not moves and caching:
        cache[(board, color, True, limit)] = compute_utility(board, color)

    val = None
    for move in moves:
        next_board = play_move(board, color, move)
        # Check if next_board in cache and assign next_val to it's value
        next_val = 0
        if caching and (next_board, other_color, False, limit-1) in cache:
            next_val = cache[(next_board, other_color, False, limit-1)]
        else:
            next_val = minimax_helper(next_board, other_color, False, limit)
        if val == None or next_val > val:
            val = next_val
            best_move = move

    if caching and val != None:
        cache[(board, color, True, limit)] = val

    return best_move

def minimax_helper(board, color, is_max, limit=-1, caching = False):
    if limit > 0:
        limit = limit - 1

    other_color = (color-1)*-1

    if caching and (board, color, is_max, limit) in cache:
        return cache[(board, color, is_max, limit)]
    
    # Return utility value if terminal state
    moves = get_possible_moves(board, color)
    if not moves or limit == 0:
        util = compute_utility(board, other_color)
        if caching:
            cache[(board, color, is_max, limit)] = util
        return util

    val = None
    for move in moves:
        next_board = play_move(board, color, move)
        next_val = 0
        # Check if in cache or recurse to find the value if it's npt
        if caching and (next_board, other_color, limit-1) in cache:
            next_val = cache[(next_board, other_color, not is_max, limit-1)]
        else:
            next_val = minimax_helper(next_board, other_color, not is_max, limit)
        if is_max and (val == None or next_val > val):
            val = next_val
        elif not is_max and (val == None or next_val < val):
            val = next_val

    if caching and val != None:
        cache[(board, color, is_max, limit)] = val

    return val

################### ALPHA-BETA METHODS ####################
def select_move_alphabeta(board, color, limit=-1, caching = False):
    # IMPLEMENT!
    """
    Given a board and a player color, decide on a move using the ALPHABETA ALGORITHM. The return value is 
    an integer i, where i is the pocket that the player on side 'color' should select.
    INPUT: a game state, the player that is in control, the depth limit for the search, and a boolean that determines if state caching is on or not
    OUTPUT: an integer that represents a move
    """

    best_move = 0
    alpha = -float(math.inf)
    beta = float(math.inf)

    if caching and (board, color, True, limit, alpha, beta) in cache:
        return cache[(board, color, True, limit, alpha, beta)]

    moves = get_possible_moves(board, color)

    if not moves and caching:
        cache[(board, color, True, limit, alpha, beta)] = compute_utility(board, color)

    ut_val = -float(math.inf)
    for move in moves:
        next_board = play_move(board, color, move)
        other_color = (color-1)*-1
        if caching and (next_board, other_color, False, limit-1, alpha, beta) in cache:
            ut_val = max(ut_val, cache[(next_board, other_color, False, limit-1, alpha, beta)])
        else:
            ut_val = max(ut_val, alphabeta_helper(next_board, other_color, False, alpha, beta, limit, caching))
        if alpha < ut_val:
            alpha = ut_val
            best_move = move
            if beta <= alpha:
                break
    
    if caching and moves and (board, color, True, limit, alpha, beta) not in cache:
        cache[(board, color, True, limit, alpha, beta)] = ut_val

    return best_move

def alphabeta_helper(board, color, is_max, alpha, beta, limit, caching = False):
    if limit > 0:
        limit = limit - 1

    other_color = (color-1)*-1

    if caching and (board, color, is_max, limit, alpha, beta) in cache:
        return cache[(board, color, is_max, limit, alpha, beta)]

    # Terminal state when no moves can be made anymore
    moves = get_possible_moves(board, color)
    if not moves or limit == 0:
        util = compute_utility(board, other_color)
        if caching:
            cache[(board, color, is_max, limit, alpha, beta)] = util
        return util

    if is_max:
        ut_val = -float(math.inf)
        for move in moves:
            next_board = play_move(board, color, move)
            # Check if in cache otherwise recurse
            if caching and (next_board, other_color, not is_max, limit-1, alpha, beta) in cache:
                ut_val = max(ut_val, cache[(next_board, other_color, not is_max, limit-1, alpha, beta)])
            else:
                ut_val = max(ut_val, alphabeta_helper(next_board, other_color, False, alpha, beta, limit, caching))
            if alpha < ut_val:
                alpha = ut_val
                if beta <= alpha:
                    break
        if caching:
            cache[(board, color, is_max, limit, alpha, beta)] = ut_val

        return ut_val
    else:
        ut_val = float(math.inf)
        for move in moves:
            next_board = play_move(board, color, move)
            # Check if in cache otherwise recurse
            if caching and (next_board, other_color, not is_max, limit-1, alpha, beta) in cache:
                ut_val = min(ut_val, cache[(next_board, other_color, not is_max, limit-1, alpha, beta)])
            else:
                ut_val = min(ut_val, alphabeta_helper(next_board, other_color, True, alpha, beta, limit, caching))
            if beta > ut_val:
                beta = ut_val
                if beta <= alpha:
                    break
        if caching:
            cache[(board, color, is_max, limit, alpha, beta)] = ut_val

        return ut_val

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

    ret_succ = None
    if mcts_tree.successors:
        ret_succ = mcts_tree.successors[board][0]
    highest_ucb = -float(math.inf)

    successors = mcts_tree.successors[board]
    for successor in successors:
        succ_board, succ_move = successor

        # Calculate ucb value for the successor
        ucb = (mcts_tree.rewards[succ_board] / mcts_tree.counts[succ_board]) + (mcts_tree.weight * math.sqrt(math.log(mcts_tree.counts[board]) / mcts_tree.counts[succ_board]))

        # Update max when new max found
        if ucb > highest_ucb:
            highest_ucb = ucb
            ret_succ = successor

    return ret_succ

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
    