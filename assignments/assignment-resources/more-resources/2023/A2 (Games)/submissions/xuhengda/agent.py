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
#steps={} # test for recursition steps

# Implement the below functions. You are allowed to define additional functions that you believe will come in handy.
def compute_utility(board, side):
    # IMPLEMENT!
    """
    Method to compute the utility value of board. This is equal to the number of stones of the mancala
    of a given player, minus the number of stones in the opposing player's mancala.
    INPUT: a game state, the player that is in control
    OUTPUT: an integer that represents utility
    """
    return board.mancalas[side] - board.mancalas[(side + 1) % 2]

def compute_heuristic(board, color):
    # IMPLEMENT!
    """
    Method to compute the heuristic value of a specific state of the board.
    INPUT: a game state, the player that is in control, the depth limit for the search
    OUTPUT: an integer that represents heuristic value
    """
    # Initiate variables
    direction = False
    if color == 1:
        direction = True
        
    mancalas_A = board.mancalas[1]
    mancalas_B = board.mancalas[0]
    pockets_A = board.pockets[1]
    pockets_B = board.pockets[0]

    # color is player A
    if direction:
        # Find the empty block
        max_capture = 0
        for i in range(len(pockets_A) - 1):
            # Possible capture
            if pockets_A[i + 1] == 0 and pockets_A[i] != 0:
                # if i + 1 on B sides has stones
                # Check how many stones we can capture. This is because we
                # only have one move. We want to maximum the profit
                if pockets_B[i + 1] != 0 and pockets_B[i + 1] > max_capture:
                    max_capture = pockets_B[i + 1]
    # color is player B
    else:
        # Find the empty block
        max_capture = 0
        for i in range(len(pockets_B) - 1, 0, -1):
            # Possible capture
            if pockets_B[i - 1] == 0 and pockets_B[i] != 0:
                # if i - 1 on A sides has stones
                # Check how many stones we can capture. This is because we
                # only have one move. We want to maximum the profit
                if pockets_A[i - 1] != 0 and pockets_A[i - 1] > max_capture:
                    max_capture = pockets_A[i - 1]

    if color == 1:
        return (mancalas_A + max_capture) - (mancalas_B + max_capture)
    else:
        return (mancalas_B + max_capture) - (mancalas_A + max_capture)

################### MINIMAX METHODS ####################
def select_move_minimax(board, color, limit=-1, caching = False):
    # IMPLEMENT!
    """
    Given a board and a player color, decide on a move using the MINIMAX ALGORITHM. The return value is 
    an integer i, where i is the pocket that the player on side 'color' should select.
    INPUT: a game state, the player that is in control, the depth limit for the search, and a boolean that determines whether state caching is on or not
    OUTPUT: an integer that represents a move
    """

    def DFMax(board, color, limit, caching):
        """
        Recursion Helper for max-player.(MinMax)
        """
        # If board is Terminal or reaching the limit bound
        if len(get_possible_moves(board, color)) == 0 or limit == 0:
            return None, compute_utility(board, color)
        
        # If the game allows caching.
        if caching:
            # Test recursive steps
            # steps["cache"] += 1
            # If the game board with one player already in the cache
            if cache.get((board, color)):
                # Return the stored pocket # and utility
                return cache[(board, color)]
        # Test recursive steps
        # else:
            #steps["Non-cache"] += 1
        
        # The pocket with max utility
        best_p = None
        # The max utility
        max_utility = float("-inf")
        for p in get_possible_moves(board, color):
            # Apply Player's moves to get successor states
            child_board = play_move(board, color, p)

            # Get in to next level, min player gains control
            # Get the utility from the DFS search
            u = DFMin(child_board, (color + 1) % 2, limit - 1, caching)[1]

            # Find the maximum utility
            if u > max_utility:
                best_p = p
                max_utility = u

        # If the game allows caching, record the maximum utility with pocket #
        if caching:
            cache[(board, color)] = (best_p, max_utility)

        # Return maximum of DFMin(c, min_player)
        return best_p, max_utility

    
    def DFMin(board, color, limit, caching):
        """
        Recursion Helper for min-player.(MinMax)
        """

        # If board is Terminal or reaching the limit bound
        if len(get_possible_moves(board, color)) == 0 or limit == 0:
            return None, compute_utility(board, (color + 1) % 2)

        
        # If the game allows caching.
        if caching:
            # Test recursive steps
            # steps["cache"] += 1
            # If the game board with one player already in the cache
            if cache.get((board, color)):
                # Return the stored pocket # and utility
                return cache[(board, color)]
        # Test recursive steps
        # else:
            #steps["Non-cache"] += 1
    
        # The pocket with min utility
        best_p = None
        # The min utility
        min_utility = float("inf")
        for p in get_possible_moves(board, color):
            # Apply Player's moves to get successor states
            child_board = play_move(board, color, p)
            
            # Get in to next level, max player gains control
            # Get the utility from the DFS search
            u = DFMax(child_board, (color + 1) % 2, limit - 1, caching)[1]

            # Find the minimum utility
            if u < min_utility:
                best_p = p
                min_utility = u

        # If the game allows caching, record the minimum utility with pocket #
        if caching:
            cache[(board, color)] = (best_p, min_utility)

        # Return minimum of DFMax(c, min_player)
        return best_p, min_utility
    
    # Test for recursive steps
    # steps["cache"], steps["Non-cache"] = 0 , 0
    # Get the pocket # with the maximum utility of player color
    pocket = DFMax(board, color, limit, caching)[0] 
    # Test for recursive steps
    #if caching:
    #    print("Recursive steps with caching:" + str(steps["cache"]) + "\n")
    #else:
    #    print("Recursive steps without caching:" + str(steps["Non-cache"]) + "\n")
    #steps.clear()
    # Clear the cache
    cache.clear()
    return pocket

        
################### ALPHA-BETA METHODS ####################
def select_move_alphabeta(board, color, limit=-1, caching = False):
    # IMPLEMENT!
    """
    Given a board and a player color, decide on a move using the ALPHABETA ALGORITHM. The return value is 
    an integer i, where i is the pocket that the player on side 'color' should select.
    INPUT: a game state, the player that is in control, the depth limit for the search, and a boolean that determines if state caching is on or not
    OUTPUT: an integer that represents a move
    """
    
    def alphabeta_max(board, color, alpha, beta, limit, caching):
        """
        Recursion Helper for max-player.(alphabeta)
        """
        # If board is Terminal or reaching the limit bound
        if len(get_possible_moves(board, color)) == 0 or limit == 0:
            return None, compute_utility(board, color)

        # If the game allows caching.
        if caching:
            # Test recursive steps
            #steps["cache"] += 1
            # If the game board with one player already in the cache
            if cache.get((board, color)):
                # Return the stored pocket # and utility
                return cache[(board, color)]
        # Test recursive steps
        #else:
        #   steps["Non-cache"] += 1

        # Record the alpha
        curr_alpha = alpha
        # The pocket with max_utval
        best_p = None
        max_utval = float("-inf")
        for p in get_possible_moves(board, color):
            # Apply Player's moves to get successor states
            child_board = play_move(board, color, p)

            # Get in to next level, min player gains control
            # Get the utility from the DFS search
            u = alphabeta_min(child_board, (color + 1) % 2, curr_alpha, beta, limit - 1, caching)[1]

            # Find the max utval
            max_utval = max(max_utval, u)

            # alpha cut
            if curr_alpha < max_utval:
                curr_alpha = max_utval
                best_p = p
                if beta <= curr_alpha:
                    break
        
        # If the game allows caching, record the maximum utility with pocket #
        if caching:
            cache[(board, color)] = (best_p, max_utval)
            
        return best_p, max_utval
    
    def alphabeta_min(board, color, alpha, beta, limit, caching):
        """
        Recursion Helper for min-player.(alphabeta)
        """
        # If board is Terminal or reaching limit bound
        if len(get_possible_moves(board, color)) == 0 or limit == 0:
            return None, compute_utility(board, (color + 1) % 2)
        
        # If the game allows caching.
        if caching:
            # Test recursive steps
            #steps["cache"] += 1
            # If the game board with one player already in the cache
            if cache.get((board, color)):
                # Return the stored pocket # and utility
                return cache[(board, color)]
        # Test recursive steps
        #else:
        #   steps["Non-cache"] += 1

        # Record the alpha
        curr_beta = beta
        # The packet # with minimum utval
        best_p = None
        min_utval = float("inf")
        for p in get_possible_moves(board, color):
            # Apply Player's moves to get successor states
            child_board = play_move(board, color, p)
            
            # Get in to next level, max player gains control
            # Find the utility of next player's possbile move
            u = alphabeta_max(child_board, (color + 1) % 2, alpha, curr_beta, limit - 1, caching)[1]

            # Find the min utval
            min_utval = min(min_utval, u)

            # Beta cut
            if curr_beta > min_utval:
                curr_beta = min_utval
                best_p = p
                if curr_beta <= alpha:
                    break
        
        # If the game allows caching, record the minimum utility with pocket #
        if caching:
            cache[(board, color)] = (best_p, min_utval)
            
        return best_p, min_utval
    
    # Initialize the alpha, beta
    a, b = float("-inf"), float("inf")
    # Test for recursive steps
    #steps["cache"], steps["Non-cache"] = 0 , 0
    # Get the pocket # with the maximum utility of player color
    pocket = alphabeta_max(board, color, a, b, limit, caching)[0]
    # Test for recursive steps
    #if caching:
    #    print("Recursive steps with caching:" + str(steps["cache"]) + "\n")
    #else:
    #    print("Recursive steps without caching:" + str(steps["Non-cache"]) + "\n")
    #steps.clear()
    # Clear the cache
    cache.clear()
    return pocket


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
    total_Sn_parent = mcts_tree.counts[board]
    w = mcts_tree.weight

    best_child = None
    best_p = None
    ucb = float("-inf")
    for child in mcts_tree.successors[board]:
        child_board = child[0]
        reward_child = mcts_tree.rewards[child_board]
        total_child = mcts_tree.counts[child_board]
        
        curr = reward_child/total_child + w * math.sqrt(math.log(total_Sn_parent)/total_child)

        if curr > ucb:
            ucb = curr
            best_child = child_board
            best_p = child[1]

    return best_child, best_p
    #return best_child, max_ucb


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
    
