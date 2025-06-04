"""
An AI player for Othello. 
"""

# The heuristic uses the idea of compute utility as well as the number of moves
# me and my opponent can make given the current board state

from cmath import inf
from operator import ne
import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move


state_mappings = {}
def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    #c= compute_heuristic(board, color)
    player1_score, player2_score = get_score(board)
    if (color == 1):
        return player1_score - player2_score 
    elif (color == 2):
        return player2_score - player1_score 
    #return 0 #change this!

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    player1_score, player2_score = get_score(board)
    moves_for_p1 = len(get_possible_moves(board, 1))
    moves_for_p2 = len(get_possible_moves(board, 2))
    if (color == 1):
        return player1_score - player2_score + moves_for_p1 - moves_for_p2
    elif (color == 2):
        return player2_score - player1_score + moves_for_p2 - moves_for_p1
    #return 0 #change this!

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)
    min_utility = float("inf")
    #min_utility = len(board) * len(board)
    min_move = None
    if color == 1:
        player = 2
    else:
        player = 1
    possible_moves = get_possible_moves(board, player)

    if caching and board in state_mappings:
        return state_mappings[board]

    if len(possible_moves) == 0 or limit == 0:
        #eprint("here")
        return (None, compute_utility(board, color))
    for move in possible_moves:
        next_board = play_move(board, player, move[0], move[1])
        #eprint(next_board)
        if caching and next_board in state_mappings:
            move_utility = state_mappings[next_board]
        else:
            move_utility = minimax_max_node(next_board, color, limit - 1, caching)
            if caching and limit != 0:
                state_mappings[next_board] = move_utility
        
        #eprint(str(move_utility))
        #min_utility = min(min_utility, utility)
        if (move_utility[1] < min_utility):   
            #eprint("xd")                                                                                                                                                                                                                                                                                                                                                       
            min_utility = move_utility[1]
            min_move = move

    #return ((0,0),0) 
    if caching:
        state_mappings[board] = (min_move, min_utility)                                                                                                                                                                                                                                                                                                
    return (min_move, min_utility)

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    max_utility = float("-inf")
   
    max_move = None
    if caching and board in state_mappings:
        return state_mappings[board]
    possible_moves = get_possible_moves(board, color)
    #eprint(str(possible_moves))
    if len(possible_moves) == 0 or limit == 0:
        return (None, compute_utility(board, color))
    for move in possible_moves:
        next_board = play_move(board, color, move[0], move[1])
        if caching and next_board in state_mappings:
            move_utility = state_mappings[next_board]
        else:
            move_utility = minimax_min_node(next_board, color, limit - 1, caching)
            if caching and limit != 0:
                state_mappings[next_board] = move_utility
        #eprint(str(move_utility))
        #min_utility = min(min_utility, utility)
        if (move_utility[1] > max_utility):
            max_utility = move_utility[1]
            max_move = move
            #eprint("22222222222222222222222222")

    #return ((0,0),0)
    #state_value_mappings[board] = (max_move, max_utility)  
    if caching:
        state_mappings[board] =  (max_move, max_utility)                                                                                                                                                  
    return (max_move, max_utility)
    #return ((0,0),0)

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
    best = minimax_max_node(tuple(map(tuple, board)), color, limit, caching)
    return best[0]
    #return (0,0) #change this!

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    min_utility = float("inf")
    #min_utility = len(board) * len(board)
    min_move = None
    if color == 1:
        player = 2
    else:
        player = 1

    next_boards = []
    sorted_next_boards = []
    if limit == 0:
        return (None, compute_utility(board, color))

    if caching and board in state_mappings:
        return state_mappings[board]
    possible_moves = get_possible_moves(board, player)

    if len(possible_moves) == 0 :
        return (None, compute_utility(board, color))
    for move in possible_moves:
        next_board = play_move(board, player, move[0], move[1])
        utility = compute_utility(next_board, player)
        next_boards.append((next_board, utility, move))
    if ordering:   
        next_boards.sort(key=lambda x:x[1])
    for next_board, utility, move in next_boards:
        if caching and next_board in state_mappings:
            move_utility = state_mappings[next_board]
        else:
            move_utility = alphabeta_max_node(next_board, color, alpha, beta, limit - 1, caching, ordering)
            if caching and limit != 0:
                state_mappings[next_board] = move_utility
        #eprint(str(move_utility))
        #min_utility = min(min_utility, utility)
        if (move_utility[1] < min_utility):   
            #eprint("xd")                                                                                                                                                                                                                                                                                                                                                       
            min_utility = move_utility[1]
            min_move = move
        if beta > min_utility:
            beta = min_utility
            if beta <= alpha:
                break

    #return ((0,0),0)  
    #state_value_mappings[board] = (min_move, min_utility) 
    if caching:
        state_mappings[board] = (min_move, min_utility)                                                                                                                                                    
    return (min_move, min_utility)
    #return ((0,0),0) #change this!

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    max_utility = float("-inf")
   
    max_move = None
    next_boards = []
    sorted_next_boards = []
    if limit == 0:
        return (None, compute_utility(board, color))

    if caching and board in state_mappings:
        return state_mappings[board]
    possible_moves = get_possible_moves(board, color)

    #eprint(str(possible_moves))
    if len(possible_moves) == 0:
        return (None, compute_utility(board, color))
    for move in possible_moves:
        next_board = play_move(board, color, move[0], move[1])
        utility = compute_utility(next_board, color)
        next_boards.append((next_board, utility, move))
        #eprint(next_board)
    if ordering:    
        next_boards.sort(key=lambda x : x[1], reverse=True)

    for next_board, utility, move in next_boards:
        if caching and next_board in state_mappings:
            move_utility = state_mappings[next_board]
        else:
            move_utility = alphabeta_min_node(next_board, color, alpha, beta, limit - 1, caching, ordering)

            if caching and limit != 0:
                state_mappings[next_board] = move_utility
        #eprint(str(move_utility))
        #min_utility = min(min_utility, utility)
        if (move_utility[1] > max_utility):
            max_utility = move_utility[1]
            max_move = move
            #eprint("22222222222222222222222222")
        if alpha < max_utility:
            alpha = max_utility
            if beta <= alpha:
                break

    #return ((0,0),0)
    
    #state_value_mappings[board] = (max_move, max_utility) 
    if caching:
        state_mappings[board] = (max_move, max_utility)                                                                                                                                                    
    return (max_move, max_utility)
    #return ((0,0),0) #change this!

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
    best = alphabeta_max_node(tuple(map(tuple, board)), color, float("-inf"), float("inf"), limit, caching, ordering)
    return best[0]
    #return (0,0) #change this!

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
