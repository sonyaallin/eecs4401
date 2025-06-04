"""
An AI player for Othello. 
"""

import random
import sys
import time
import heapq

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move
minimax_cache = {}
alphabeta_cache = {}


def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    (x,y) = get_score(board)
    if (color == 1):
        return x-y
    else:
        return y-x


# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    # return 0 #change this!
    # TODO
    return compute_utility(board, color)

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT
    global minimax_cache

    if color == 1:
        opp_color = 2
    elif color == 2:
        opp_color = 1

    possible_moves = get_possible_moves(board, opp_color)

    # to return earlyyy
    if not limit:
        compyeet = compute_utility(board, color)
        return (-1, -1), compyeet
    if not possible_moves:
        compyeet = compute_utility(board, color)
        return (-1, -1), compyeet

    min_move = ((-1, -1), float('inf'))

    
    if len(minimax_cache) == 0: # aka if its empty
        minimax_cache = {}

    for i, j in possible_moves:

        current_score = float('inf')
        played_board = play_move(board, opp_color, i, j)
        cache = (opp_color, played_board)
        
        if (not caching) or (not cache) in minimax_cache:
            calc = minimax_max_node(played_board, color, limit - 1, caching)[1]
            current_score = calc
            if caching:
                minimax_cache[cache] = current_score
        else:
            current_score = minimax_cache[cache]

        if min_move[1] > current_score:
            min_move = ((i, j), current_score)

    return min_move

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT
    global minimax_cache
    max_move = ((-1, -1), float('-inf'))

    possible_moves = get_possible_moves(board, color)

    # to return earlyyy
    if not limit:
        compyeet = compute_utility(board, color)
        return (-1, -1), compyeet
    if not possible_moves:
        compyeet = compute_utility(board, color)
        return (-1, -1), compyeet

    for i, j in possible_moves:
        current_score = float('-inf')
        played_board = play_move(board, color, i, j)
        cache = (color, played_board)

        # some how this is faster than the original way i did it hmmm
        if caching and cache in minimax_cache:
            minicache = minimax_cache[cache]
            current_score = minicache
        else:
            current_score = minimax_min_node(played_board, color, limit - 1, caching)[1]
            if caching:
                minimax_cache[cache] = current_score
        
        # this way didnt improve it ... guess im leaving it as aboveeee
        # if (not caching) or (not cache) in minimax_cache:
        #     current_score = minimax_min_node(played_board, color, limit - 1, caching)[1]
        #     if caching:
        #         minimax_cache[cache] = current_score
        # else:
        #     current_score = minimax_cache[cache]

        if max_move[1] < current_score:
            max_move = ((i, j), current_score)

    return max_move

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
    #IMPLEMENT
    # i take care of caching in hte actual function so i guess i dont have to worry here
    # i hope LMAO
    minimax_cache.clear()
    return minimax_max_node(board, color, limit, caching)[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT
    global alphabeta_cache
    min_heap = []
    board_states = []

    if color == 1:
        opp_color = 2
    elif color == 2:
        opp_color = 1

    possible_moves = get_possible_moves(board, opp_color)
    min_move = ((-1, -1), float('inf'))

    # to return earlyyy
    if not limit:
        compyeet = compute_utility(board, color)
        return (-1, -1), compyeet
    if not possible_moves:
        compyeet = compute_utility(board, color)
        return (-1, -1), compyeet

    for (i, j) in possible_moves:
        played_board = play_move(board, opp_color, i, j)
        if not ordering:
            board_states.append((played_board, i, j))
        else:
            compyeet = compute_utility(played_board, color)
            playeet = (played_board, i, j)
            heapq.heappush(min_heap, (compyeet, playeet))

    # need to append !!!!! this is where you went wrong smhhh
    while ordering and min_heap:
        board_states.append(heapq.heappop(min_heap)[1])

    #this was the wrong way to do itttt
    #while (not ordering) or (not min_heap):
    #    board_states.append(heapq.heappop(min_heap)[1])

    for (played_board, i, j) in board_states:
        current_score = float('inf')
        cache = (opp_color, played_board)

        if caching and cache in alphabeta_cache:
            current_score = alphabeta_cache[cache]
        else:
            new_lim = limit -1
            current_score = alphabeta_max_node(played_board, color, alpha, beta, limit - 1, caching, ordering)[1]
            if caching:
                alphabeta_cache[cache] = current_score

        if min_move[1] > current_score:
            min_move = ((i, j), current_score)

        beta = min(beta, current_score)

        if alpha >= beta:
            break

    return min_move

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT
    global alphabeta_cache
    max_move = ((-1, -1), float('-inf'))
    max_heap = []
    board_states = []

    possible_moves = get_possible_moves(board, color)

    # to return earlyyy
    if not limit:
        compyeet = compute_utility(board, color)
        return (-1, -1), compyeet
    if not possible_moves:
        compyeet = compute_utility(board, color)
        return (-1, -1), compyeet

    for i, j in possible_moves:
        played_board = play_move(board, color, i, j)
        if ordering:
            negcompyeet = -1*compute_utility(played_board, color)
            inverse = (negcompyeet, (played_board, i, j))
            #push to the heap
            heapq.heappush(max_heap, inverse)
        else:
            board_states.append((played_board, i, j))

    while ordering and max_heap:
        board_states.append(heapq.heappop(max_heap)[1])

    for played_board, i, j in board_states:
        current_score = float('-inf')
        cache = (color, played_board)

        if caching and cache in alphabeta_cache:
            current_score = alphabeta_cache[cache]
        else:
            current_score = alphabeta_min_node(played_board, color, alpha, beta, limit - 1, caching, ordering)[1]
            if caching:
                alphabeta_cache[cache] = current_score

        # compute the utility given the min node was played
        if max_move[1] < current_score:
            max_move = ((i, j), current_score)
        alpha = max(alpha, current_score)
        if beta <= alpha:
            break

    return max_move

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
    #IMPLEMENT
    # i take care of caching in hte actual function so i guess i dont have to worry here
    # i hope LMAO
    alphabeta_cache.clear()
    return alphabeta_max_node(board, color, float('-inf'), float('inf'), limit, caching, ordering)[0]

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

if __name__ == "__main__":
    run_ai()
