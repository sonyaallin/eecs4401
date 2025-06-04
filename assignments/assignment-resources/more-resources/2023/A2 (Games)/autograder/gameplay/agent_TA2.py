"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move
from A3.agent import compute_heuristic

cache = {} #use this for state caching

def eprint(*args, **kwargs): #use this for debugging, to print to sterr
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of board
def compute_utility_TA(board, color): #this should end up being BETTER
    score = get_score(board)
    if color == 1: 
        return  score[0] - score[1]
    else:
        return  score[1] - score[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node_TA(board, color, alpha, beta, limit, caching = 0, ordering = 0, heur = 0):
    # Get the color of the next player
    opponent = 1
    if color == 1: opponent = 2
        
    # Get the allowed moves
    all_moves = get_possible_moves(board, opponent)

    # If there are no moves left, return the utility
    if len(all_moves) == 0 or limit == 0:
        if heur == 0:
            return None, compute_utility_TA(board, color)
        else:
            return None, compute_heuristic(board, color)

    # Else if there are moves, get their utility and return the min
    min_utility = float("Inf")
    min_move = None
    limit -= 1

    all_moves_sorted = []

    # Get the utility of all the moves
    for each in all_moves:

        # Get the next board from that move and add the moves to the list
        next_board = play_move(board, opponent, each[0], each[1])
        all_moves_sorted.append((each, next_board))

        # Sort the list by utility, but in reverse
    if ordering: 
        all_moves_sorted.sort(key = lambda util: compute_utility_TA(util[1], color), reverse=True)

    # For each possible move, get the max utiltiy
    for each in all_moves_sorted:

        next_board = each[1]
        if caching and (next_board,opponent,alpha,beta) in cache: move, new_utility = cache[(next_board,opponent,alpha,beta)]

        else:
            move, new_utility = alphabeta_max_node_TA(each[1], color, alpha, beta, limit, caching, ordering, heur)
            if caching: cache[(next_board,opponent,alpha,beta)] = (move, new_utility)

        if new_utility < min_utility:
            min_utility = new_utility
            min_move = each[0]

        if min_utility < beta: #update beta
            beta = min_utility
        
        if min_utility <= alpha: #cutoff
            return min_move, min_utility 


    # After checking every move, return the minimum utility
    return min_move, min_utility

def alphabeta_max_node_TA(board, color, alpha, beta, limit, caching = 0, ordering = 0, heur = 0):

    # Get the allowed moves
    all_moves = get_possible_moves(board, color)

    # If there are no moves left, return the utility
    if len(all_moves) == 0 or limit == 0:
        if heur == 0:
            return None, compute_utility_TA(board, color)
        else:
            return None, compute_heuristic(board, color)

    # Else if there are moves, get their utility and return the max 
    # Store the minimum utility possible to use as a starting point for min  
    max_utility = float("-Inf")
    max_move = None
    limit -= 1 

    all_moves_sorted = []

    # Get the utility of all the moves
    for each in all_moves:

        # Get the next board from that move
        next_board = play_move(board, color, each[0], each[1])
        # Add the moves to the list
        all_moves_sorted.append((each, next_board))

    # Sort the list by utility (reversed so when iterated, it starts at the greatest value)
    if ordering: all_moves_sorted.sort(key = lambda util: compute_utility_TA(util[1], color), reverse=True)

    # For each possible move, get the max utiltiy
    for each in all_moves_sorted:

        #Check the cache
        next_board = each[1]
        if caching and (next_board, color) in cache: move, new_utility = cache[(next_board,color)]        

        else:
            # If the new utility is greater than the current max, update max_utility
            move, new_utility = alphabeta_min_node_TA(each[1], color, alpha, beta, limit, caching, ordering, heur)
            if caching: cache[(next_board, color)] = (move, new_utility)

        if new_utility > max_utility:
            max_utility = new_utility
            max_move = each[0]

        if max_utility > alpha: #update alpha
            alpha = max_utility            

        if alpha >= beta: #cutoff            
            return max_move, max_utility

    # After checking every move, return the maximum utility
    return max_move, max_utility

def select_move_alphabeta_TA(board, color, limit = -1, caching = 0, ordering = 0, heur = 0):

    alpha = float("-Inf")
    beta = float("Inf")
    node_ordering = []

    # Get the best move according to the max utiltiy
    move, utility = alphabeta_max_node_TA(board, color, alpha, beta, limit, caching, ordering, heur)
    return move

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Othello AI") # First line is the name of this AI
    arguments = input().split(",")
    
    color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light. 
    limit = int(arguments[1]) #Depth limit
    minimax = int(arguments[2]) #Minimax or alpha beta
    caching = int(arguments[3]) #Caching 
    ordering = int(arguments[4]) #Node-ordering (for alpha-beta only)

    if (minimax == 1): eprint("Running MINIMAX")
    else: eprint("Running ALPHA-BETA")

    if (caching == 1): eprint("State Caching is ON")
    else: eprint("State Caching is OFF")

    if (ordering == 1): eprint("Node Ordering is ON")
    else: eprint("Node Ordering is OFF")

    if (limit == -1): eprint("Depth Limit is OFF")
    else: eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True: # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL": # Game is over.
            print
        else:
            board = eval(input()) # Read in the input and turn it into a Python
                                  # object. The format is a list of rows. The
                                  # squares in each row are represented by
                                  # 0 : empty square
                                  # 1 : dark disk (player 1)
                                  # 2 : light disk (player 2)

            # Select the move and send it to the manager
            heur = 0           
            if (minimax != 1):
                movei, movej = select_move_alphabeta_TA(board, color, limit, caching, ordering, heur)
            
            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_ai()
