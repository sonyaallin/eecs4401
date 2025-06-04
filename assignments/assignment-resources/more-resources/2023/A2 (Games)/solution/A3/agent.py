"""
An AI player for Mancala.
"""

# Some potentially helpful libraries
import random
import math
import time

# You can use the functions in mancala_game to write your AI.  Import any methods you need.
from mancala_game import Board, get_possible_moves, eprint, play_move, MCTS

cache={} #use this for your state cache; use it if caching is on

def compute_utility(board, side):
    """
    Method to compute the utility value of board.  This is equal to the number of
    stones the the mancala of a given player, minus the number of stones in the opposing player's mancala
    INPUT: a game state, the player that is in control
    OUTPUT: an integer that represents utility
    """
    raise RuntimeError("Method not implemented") #replace this line!

def compute_heuristic(board, color):  # not implemented
    """
    Method to compute the heuristic value of board.
    INPUT: a game state, the player that is in control, the depth limit for the search
    OUTPUT: an integer that represents heuristic value
    """
    raise RuntimeError("Method not implemented") #replace this line!

################### MINIMAX METHODS ####################
def select_move_minimax(board, color, limit=-1, caching = False):
    """
    Given a board and a player color, decide on a move using the MINIMAX ALGORITHM
    The return value is an integer, where
    i is the pocket that the player on side 'color' should select.
    INPUT: a game state, the player that is in control, the depth limit for the search, and a boolean that determines if state caching is on or not
    OUTPUT: an integer that represents a move
    """
    raise RuntimeError("Method not implemented") #replace this line!

################### ALPHA-BETA METHODS ####################
def select_move_alphabeta(board, color, limit=-1, caching = False):
    """
    Given a board and a player color, decide on a move using the ALPHA BETA ALGORITHM
    The return value is a tuple (integer i, integer j) where
    i is the pocket that the player on side 'color' should select
    j is the TOTAL NUMBER OF ALPHA BETA CUTS that were made during the course of the search
    INPUT: a game state, the player that is in control, the depth limit for the search, and a boolean that determines if state caching is on or not
    OUTPUT: a tuple (integer i, integer j) where i represents a move and j the number of AB cuts that took place while searching
    """
    raise RuntimeError("Method not implemented") #replace this line!

################### MCTS METHODS ####################
def ucb_select(board, mcts_tree):
    #IMPLEMENT! This is the only method that will be marked as a part of the assignment.  Feel free to implement the others, but only if you like.
    '''Select '''
    '''INPUT: a board state and an MCTS tree'''
    '''OUTPUT: the successive state of the input board that corresponds with the max UCB value in the tree.'''
    # You can encode this as follows:
    # 1. Cycle thru the successors of the given board.
    # 2. Calculate the UCB values for the successors, given the input tree
    # 3. Return the successor with the highest UCB value
    raise RuntimeError("Method not implemented") #replace this line!

################### ALL METHODS BELOW ARE OPTIONAL ####################
def choose_move(board, color, mcts_tree):
    #IMPLEMENT. Encoding this method is OPTIONAL.
    '''choose a move'''
    '''INPUT: a game state, the player that is in control and an MCTS tree'''
    '''OUTPUT: a number representing a move for the player tat is in control'''
    # Encoding this method is OPTIONAL.  You will want it to
    # 1. See if a given game state is in the MCTS tree.
    # 2. If yes, return the move that is associated with the highest average reward in the tree (from the perspective of the player 'color')
    # 3. If no, return a random move
    raise RuntimeError("Method not implemented") #replace this line!


def rollout(board, color, mcts_tree):
    #IMPLEMENT. Encoding this method is OPTIONAL.
    '''rollout the tree!'''
    '''INPUT: a game state that will be at the start of the path, the player that is in control and an MCTS tree (see class def in mancala_game)'''
    '''OUTPUT: nothing!  Just adjust the MCTS tree statistics as you roll out.'''
    # Encoding this method is OPTIONAL.  You will want it to
    # 1. Find a path from the root of the tree to a leaf based on ucs stats (use select_path(board, color, mctsree))
    # 2. Expand the last state in that path and add all the successors to the tree (use expand_leaf(board, color, mctsree))
    # 3. Simulate game play from the final state to a terminal and derive the reward
    # 4. Back-propagate the reward all the way from the terminal to the root of the MCTS tree
    raise RuntimeError("Method not implemented") #replace this line!


def select_path(board, color, mcts_tree):
    #IMPLEMENT. Encoding this method is OPTIONAL.
    '''Find a path from the root of the tree to a leaf based on ucs stats'''
    '''INPUT: a game state that will be at the start of the path, the player that is in control and an MCTS tree (see class def in mancala_game)'''
    '''OUTPUT: A list of states that leads from the root of the MCTS tree to a leaf.'''
    # Encoding this method is OPTIONAL.  You will want it to return a path from the board provided to a
    # leaf of the MCTS tree based on ucs stats (select_path(board, mctsree)).  You can encode this as follows:
    # Repeat:
    # 1. Add the state to the path
    # 2. Check to see if the state is a terminal.  If yes, return the path.
    # 3. If no, check to see if any successor of the state is a terminal.  If yes, add any unexplored terminal to the path and return.
    # 5. If no, descend the MCTS tree a level to select a new state based on the UCT criteria.
    raise RuntimeError("Method not implemented") #replace this line!

def expand_leaf(board, color, mcts_tree):
    '''Expand a leaf in the mcts tree'''
    '''INPUT: a game state that will be at the start of the path, the player that is in control and an MCTS tree (see class def in mancala_game)'''
    '''OUTPUT: nothing!  Just adjust the MCTS tree statistics as you roll out.'''
    # If the given state already exists in the tree, do nothing
    # Else, add the successors of the state to the tree.
    raise RuntimeError("Method not implemented") #replace this line!


def simulate(board, color):
    #IMPLEMENT. Encoding this method is OPTIONAL.
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
    raise RuntimeError("Method not implemented") #replace this line!

def backprop(path, reward, mcts_tree):
    #IMPLEMENT. Encoding this method is OPTIONAL.
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
    raise RuntimeError("Method not implemented") #replace this line!

def select_move_mcts(board, color, weight=1, numsamples = 50):
    mcts_tree = MCTS(weight) #initialize your MCTS tree
    for _ in range(numsamples): #sample the tree numsamples times
        #in here you'll want to encode a 'rollout' for each iteration
        #store the results of each rollout in the MCTS tree (mcts_tree)
        pass #change this!

    #Then, at the end of your iterations, choose the best move, according to your tree (ie choose_move(board, color, mcts_tree))
    raise RuntimeError("Method not implemented") #replace this line!

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
    algorithm = int(arguments[2])  # Minimax, alpha beta, or MCTS

    if (algorithm == 2): #implement this only if you really want to!!
        eprint("Running MCTS")
        limit = -1  # limit is irrelevant to MCTS!!
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
