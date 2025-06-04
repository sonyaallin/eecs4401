"""
An AI player for Othello.
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

# TODO: Implement the depth limit for alphabeta once you know that it works for minimax

# TODO: should you end the game once there's no more moves?

state_to_minimax = {}

should_stop = True

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)

# Method to compute utility value of terminal state
def compute_utility(board, color):

    p1_count, p2_count = get_score(board)
    if color == 1:
        return p1_count - p2_count
    elif color == 2:
        return p2_count - p1_count
    else:
        eprint("CUSTOM ERROR: ummm compute_utility's color is actually: " + str(color))


# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    return 0 #change this!

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)
    #return ((0,0),0)

    # caching: return previously found minimax value
    if caching == 1 and board in state_to_minimax:
        # eprint(state_to_minimax[board])
        return state_to_minimax[board] # TODO: should probably return a tuple here lol

    '''
    if limit == 0:
        return (-1, -1), compute_utility(board, color) # TODO: should probably return a tuple here lol
    '''

    # if state is terminal, return it's utility
    if limit == 0 or get_possible_moves(board, color) == []:
        resulting_minimax = (-1, -1), compute_utility(board, color)
        if caching == 1:
            state_to_minimax[board] = resulting_minimax
        return resulting_minimax

    # get successor moves
    child_list = get_possible_moves(board, color)
    child_utilities = []
    # eprint("====================== MIN: child list: " + str(child_list))
    # eprint("======================      child_utilities: " + str(child_utilities))

    # get successor utilities
    for child in child_list:
        # eprint("====================== >   MIN: child: " + str(child))
        new_state = play_move(board, color, child[0], child[1])
        child_utility = minimax_max_node(new_state, other_color(color), limit - 1, caching)
        # eprint("====================== >   MIN: child utility (max): " + str(child_utility))
        child_utilities.append(child_utility[1])

    # get the move with the lowest utility
    min_child_utility = min(child_utilities)
    min_child = None
    for i in range(len(child_utilities)):
        if child_utilities[i] == min_child_utility:
            min_child = child_list[i]

    # note minimax value for caching
    if caching == 1:
        state_to_minimax[board] = min_child, min_child_utility

    return min_child, min_child_utility


def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    #return ((0,0),0)

    if caching == 1 and board in state_to_minimax:
        # eprint(state_to_minimax[board])
        return state_to_minimax[board] # TODO: should probably return a tuple here lol

    '''
    if limit == 0:
        return (-1, -1), compute_utility(board, color) # TODO: should probably return a tuple here
    '''

    # if state is terminal, return it's utility
    if limit == 0 or get_possible_moves(board, color) == []:
        resulting_minimax = (-1, -1), compute_utility(board, color)
        if caching == 1:
            state_to_minimax[board] = resulting_minimax
        return resulting_minimax

    # get successor moves
    child_list = get_possible_moves(board, color)
    child_utilities = []
    # eprint("====================== MAX: child list: " + str(child_list))
    # eprint("======================      child_utilities: " + str(child_utilities))

    # get successor utilities
    for child in child_list:
        # eprint("====================== >   MAX: child: " + str(child))
        new_state = play_move(board, color, child[0], child[1])
        child_utility = minimax_min_node(new_state, other_color(color), limit - 1, caching)
        # eprint("====================== >   MAX: child utility (min): " + str(child_utility))
        child_utilities.append(child_utility[1])

    # get the move with the highest utility
    max_child_utility = max(child_utilities)
    max_child = None
    for i in range(len(child_utilities)):
        if child_utilities[i] == max_child_utility:
            max_child = child_list[i]

    # note minimax value for caching
    if caching == 1:
        state_to_minimax[board] = max_child, max_child_utility

    return max_child, max_child_utility

def select_move_minimax(board, color, limit, caching = 0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    """
    #IMPLEMENT (and replace the line below)
    #return (0,0) #change this!

    max_child, max_child_utility = minimax_max_node(board, color, limit, caching)
    return max_child



############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    #return ((0,0),0) #change this!

    if limit == 0:
        return (-1, -1), compute_utility(board, color)

    # if state is terminal, return it's utility
    if get_possible_moves(board, color) == []:
        return (-1, -1), compute_utility(board, color)

    # get successor moves
    child_list = get_possible_moves(board, color)
    child_utilities = []
    # eprint("====================== MIN: child list: " + str(child_list))
    # eprint("======================      child_utilities: " + str(child_utilities))
    last_updating_child = None
    final_beta = None

    # find the right beta
    for child in child_list:
        # eprint("====================== >   MIN: child: " + str(child))
        new_state = play_move(board, color, child[0], child[1])

        child_utility = alphabeta_max_node(new_state, other_color(color), alpha, beta, limit - 1, caching, ordering)[1]
        beta = min(beta, child_utility)

        # eprint("====================== >   MIN: child utility (min): " + str(alphabeta_max_node(new_state, other_color(color), alpha, beta, limit, caching, ordering)[1]))
        child_utilities.append(beta)

        if beta == child_utility:
            last_updating_child = child

        if beta <= alpha:
            # beta_child = child
            break
    final_beta = beta

    '''
    for i in range(len(child_utilities)):
        if child_utilities[i] == beta:
            beta_child = child_list[i]
    '''

    return last_updating_child, beta


def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    #return ((0,0),0) #change this!

    if limit == 0:
        return (-1, -1), compute_utility(board, color)

    # if state is terminal, return it's utility
    if get_possible_moves(board, color) == []:
        return (-1, -1), compute_utility(board, color)

    # get successor moves
    child_list = get_possible_moves(board, color)
    child_utilities = []
    # eprint("====================== MAX: child list: " + str(child_list))
    # eprint("======================      child_utilities: " + str(child_utilities))
    last_updating_child = None
    final_alpha = None

    # find the right beta
    for child in child_list:
        # eprint("====================== >   MAX: child: " + str(child))
        new_state = play_move(board, color, child[0], child[1])


        child_utility = alphabeta_min_node(new_state, other_color(color), alpha, beta, limit - 1, caching, ordering)[1]
        alpha = max(alpha, child_utility)
        if alpha == child_utility:
            last_updating_child = child


        # eprint("====================== >   MAX: child utility (min): " + str(alphabeta_max_node(new_state, other_color(color), alpha, beta, limit, caching, ordering)[1]))
        child_utilities.append(alpha)

        if beta <= alpha:
            # alpha_child = child
            break
    final_alpha = alpha

    '''
    for i in range(len(child_utilities)):
        if child_utilities[i] == alpha:
            alpha_child = child_list[i]
    '''

    return last_updating_child, final_alpha


def select_move_alphabeta(board, color, limit, caching = 0, ordering = 0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations.
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations.
    """
    #IMPLEMENT (and replace the line below)

    max_child, max_child_utility = alphabeta_max_node(board, color, float("-inf"), float("inf"), limit, caching)
    return max_child

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
            if (minimax == 1): #run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else: #else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)

            print("{} {}".format(movei, movej))


# Custom helpers

def other_color(color):
    if color == 1:
        return 2
    elif color == 2:
        return 1
    else:
        print("CUSTOM ERROR: IN other_color: " + str(color) + " is not a valid color")

if __name__ == "__main__":
    run_ai()