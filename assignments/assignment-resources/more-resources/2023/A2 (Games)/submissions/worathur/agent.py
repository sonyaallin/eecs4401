"""
An AI player for Mancala.
"""

# Some potentially helpful libraries
import random
import math
import time

# You can use the functions in mancala_game to write your AI. Import methods you need.
from mancala_game import Board, get_possible_moves, eprint, play_move, MCTS, end_game

cache={} # Use this variable for your state cache; Use it if caching is on

# Implement the below functions. You are allowed to define additional functions that you believe will come in handy.
def compute_utility(board, side):
    """
    Method to compute the utility value of board. This is equal to the number of stones of the mancala
    of a given player, minus the number of stones in the opposing player's mancala.
    INPUT: a game state, the player that is in control
    OUTPUT: an integer that represents utility
    """
    return (board.mancalas[side] - board.mancalas[abs(side - 1)])

def compute_heuristic(board, side):
    """
    Method to compute the heuristic value of a specific state of the board.
    INPUT: a game state, the player that is in control, the depth limit for the search
    OUTPUT: an integer that represents heuristic value

    State Features:
    x_1: Number of stones in current player's mancala store minus number of stones in opponent's mancala store
    x_2: Number of captures which can be made by current player
    x_3: Number of captures which can be made by opposing player

    heur_val = x_1 + 0.25 * x_2 - 0.5 * x_3

    Reasoning: The amount of stones in one's own Mancala store compared to the opponent's Mancala store is
    highly correlated with the utility of a state. The player should also play to maximize the number of captures
    they can make while minimizing the number of captures the opponent can make. We weigh the possible captures the
    opponent can make more heavily as it has been determined through experimentation that playing defensively leads
    to more wins.

    """
    num_pockets = len(board.pockets[0])
    curr_score = compute_utility(board, side)

    p0_captures = 0

    # compute player 0's capture opportunities
    for i in range(num_pockets - 1, 0, -1):
        if board.pockets[0][i] == 1 and board.pockets[0][i - 1] == 0:
            p0_captures += 1

    p1_captures = 0
    # compute player 1's capture opportunities
    for i in range(0, num_pockets -1):
        if board.pockets[1][i] == 1 and board.pockets[1][i + 1] == 0:
            p1_captures += 1

    if side == 0:
        heur_val = curr_score  - 0.25 * p1_captures # + 0.50 * p0_captures
    else:
        heur_val = curr_score - 0.25 *  p0_captures # + 0.50 * p1_captures

    return heur_val

################### MINIMAX METHODS ####################
def minimax_max(board, side, limit, caching):
    """
    Compute the utility value of a max node using the minimax strategy.
    """

    poss_moves = get_possible_moves(board, side)
    opt_move, total_explored = -1, 1

    cache_key = (board, 1) # 1 cache the minimax value from perspective of MAX
    if caching and cache_key in cache:
        return (opt_move, total_explored, cache[cache_key])

    if poss_moves == [] or limit == 0:


        ut_val = compute_utility(board, side)
        res = (opt_move, total_explored, ut_val)
        return res

    ut_val = float('-inf')

    for move in poss_moves:
        successor = play_move(board, side, move)
        explored, val = minimax_min(successor, side, limit - 1, caching)[1:]
        total_explored += explored
        if val > ut_val:
            opt_move, ut_val = move, val

    if caching and cache_key not in cache:
        cache[cache_key] = ut_val

    return opt_move, total_explored, ut_val

def minimax_min(board, side, limit, caching):
    """
    Compute the utility value of a min node using the minimax strtagey
    """

    opponent = 0 if side == 1 else 1

    poss_moves = get_possible_moves(board, opponent)
    opt_move, total_explored = -1, 1

    cache_key = (board, 0)

    if caching and cache_key in cache:
        return (opt_move, total_explored, cache[cache_key])

    if poss_moves == [] or limit == 0:

        ut_val = compute_utility(board, side)
        res = (opt_move, total_explored, ut_val)
        return res

    ut_val = float('inf')

    for move in poss_moves:
        successor = play_move(board, opponent, move)
        explored, val = minimax_max(successor, side, limit - 1, caching)[1:]
        total_explored += explored
        if val < ut_val:
            opt_move, ut_val = move, val

    if caching and cache_key not in cache:
        cache[cache_key] = ut_val

    return opt_move, total_explored, ut_val

def select_move_minimax(board, side, limit=-1, caching = False):
    # IMPLEMENT!
    """
    Given a board and a player color, decide on a move using the MINIMAX ALGORITHM. The return value is 
    an integer i, where i is the pocket that the player on side 'color' should select.
    INPUT: a game state, the player that is in control, the depth limit for the search, and a boolean that determines whether state caching is on or not
    OUTPUT: an integer that represents a move
    """
    global cache
    cache = {}
    opt_move, total_explored, ut_val = minimax_max(board, side, limit, caching)
    # print("SIDE: {} UT_VAL: {} MOVE: {}".format(side, ut_val, opt_move))
    return opt_move

################### ALPHA-BETA METHODS ####################
def alphabeta_max(board, side, limit, caching, alpha=float('-inf'), beta=float('inf')):

    key = (board, 1)
    opt_move, total_cuts = -1, 0

    if caching and key in cache:
        return (opt_move, total_cuts, cache[key])

    poss_moves = get_possible_moves(board, side)

    if poss_moves == [] or limit == 0:
        ut_val = compute_utility(board, side)
        res = (opt_move, total_cuts, ut_val)
        return res

    ut_val = float('-inf')

    for i, move in enumerate(poss_moves):

        successor = play_move(board, side, move)
        cuts, val = alphabeta_min(successor, side, limit - 1, caching, alpha, beta)[1:]
        total_cuts += cuts

        if val > ut_val:
            opt_move, ut_val = move, val

        alpha = max(alpha, ut_val)

        if beta <= alpha:
            total_cuts += 1
            break

    if caching:
        cache[key] = ut_val

    return opt_move, total_cuts, ut_val

def alphabeta_min(board, side, limit, caching, alpha, beta):

    opponent = 0 if side == 1 else 1

    key = (board, 0)
    opt_move, total_cuts = -1, 0

    if caching and key in cache:
        return (opt_move, total_cuts, cache[key])

    poss_moves = get_possible_moves(board, opponent)

    if poss_moves == [] or limit == 0:

        ut_val = compute_utility(board, side)
        res = (opt_move, total_cuts, ut_val)
        return res

    ut_val = float('inf')

    for i, move in enumerate(poss_moves):

        successor = play_move(board, opponent, move)
        cuts, val = alphabeta_max(successor, side, limit - 1, caching, alpha, beta)[1:]
        total_cuts  += cuts

        if val < ut_val:
            opt_move, ut_val = move, val

        beta = min(beta, ut_val)

        if beta <= alpha:
            total_cuts += 1
            break

    if caching:
        cache[key] = ut_val

    return opt_move, total_cuts, ut_val

def select_move_alphabeta(board, side, limit=-1, caching = False):
    # IMPLEMENT!
    """
    Given a board and a player color, decide on a move using the ALPHA BETA ALGORITHM. The return value 
    is a tuple (integer i, integer j) where i is the pocket that the player on side 'color' should 
    select j is the TOTAL NUMBER OF ALPHA BETA CUTS that were made during the course of the search.
    INPUT: a game state, the player that is in control, the depth limit for the search, and a boolean that determines if state caching is on or not
    OUTPUT: a tuple (integer i, integer j) where i represents a move and j the number of AB cuts that took place while searching
    """
    global cache
    cache = {}
    opt_move, total_cuts, ut_val = alphabeta_max(board, side, limit, caching)

    return opt_move


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

    # A leaf node is a node for which none of its successors have been visited

    ucb_max, best_successor = float('-inf'), None


    for (successor,  move) in mcts_tree.successors[board]:
        if successor not in mcts_tree.successors:
            return (successor, move) # ucb value has not been calculated and is infinite

        value_est = mcts_tree.rewards[successor] / mcts_tree.counts[successor]
        explore_value = math.sqrt(math.log(mcts_tree.counts[board]) / mcts_tree.counts[successor])

        ucb_val = value_est + mcts_tree.weight * explore_value

        if ucb_val > ucb_max:
            ucb_max, best_successor = ucb_val, (successor, move)

    return best_successor

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
    algorithm = int(arguments[3])  # Minimax, Alpha Beta, or MCTS

    if (algorithm == 2): # Implement this only if you really want to!!
        eprint("Running MCTS")
        limit = -1  # Limit is irrelevant to MCTS!!
    elif (algorithm == 1):
        eprint("Running ALPHA-BETA")
    else:
        eprint("Running MINIMAX")

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
                move = select_move_alphabeta(board, color, limit)
            else:
                move = select_move_minimax(board, color, limit)

            print("{}".format(move))


if __name__ == "__main__":
    run_ai()
    