"""
An AI player for Othello. 

My heuristic makes use of get_score, which counts the number of tiles per opponent and player, as well as the number of possible moves for the opponent and player as well.
I also included the number of continuous pieces which are adjacent and inside a corner, this resulted in equal scores for the most part.
"""

from hashlib import new
from logging.config import valid_ident
import random
import sys
import time

state_dict = {}
min_dict = {}
max_dict = {}

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    d_score, l_score = get_score(board)    
    if color == 1:
        return d_score - l_score
    else:
        return l_score - d_score

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    d_score, l_score = get_score(board)    
    
    if color == 1:
        pieces =  d_score - l_score
        d_moves = get_possible_moves(board, 1)
        l_moves = get_possible_moves(board, 2)

        pieces = pieces - len(l_moves) + len(d_moves)
        
        length = len(board)-1

        adjacent = True
        counter = 0
        for i in range(length):
            for j in range(length):
                if board[i][j] == 1 and adjacent:
                    pieces += 1
                else:
                    break
                    # adjacent = False
                    # if board[i][j] == 0:
                    #     counter += 1
                    # elif board[i][j] == 1:
                    #     if counter % 2 == 1:
                    #         pieces -= counter
                    # else:
                    #     counter = 0
        adjacent = True
        counter = 0
        for i in range(length, 0, -1):
            for j in range(length):
                if board[i][j] == 1 and adjacent:
                    pieces += 1
                else:
                    break
                    # adjacent = False
                    # if board[i][j] == 0:
                    #     counter += 1
                    # elif board[i][j] == 1:
                    #     if counter % 2 == 1:
                    #         pieces -= counter
                    # else:
                    #     counter = 0
        adjacent = True
        for i in range(length):
            for j in range(length, 0, -1):
                if board[i][j] == 1 and adjacent:
                    pieces += 1
                else:
                    break
                    # adjacent = False
                    # if board[i][j] == 0:
                    #     counter += 1
                    # elif board[i][j] == 1:
                    #     if counter % 2 == 1:
                    #         pieces -= counter
                    # else:
                    #     counter = 0
        adjacent = True
        counter = 0
        for i in range(length, 0, -1):
            for j in range(length, 0, -1):
                if board[i][j] == 1 and adjacent:
                    pieces += 1
                else:
                    break
                    # adjacent = False
                    # if board[i][j] == 0:
                    #     counter += 1
                    # elif board[i][j] == 1:
                    #     if counter % 2 == 1:
                    #         pieces -= counter
                    # else:
                    #     counter = 0
        return pieces
    else:
        pieces =  l_score - d_score

        d_moves = get_possible_moves(board, 1)
        l_moves = get_possible_moves(board, 2)

        pieces = pieces - len(d_moves) + len(l_moves)

        length = len(board)-1
        
        adjacent = True
        counter = 0
        for i in range(length):
            for j in range(length):
                if board[i][j] == 2 and adjacent:
                    pieces += 1
                else:
                    break
                    # adjacent = False
                    # if board[i][j] == 0:
                    #     counter += 1
                    # elif board[i][j] == 2:
                    #     if counter % 2 == 1:
                    #         pieces -= counter
                    # else:
                    #     counter = 0
        adjacent = True
        counter = 0
        for i in range(length, 0, -1):
            for j in range(length):
                if board[i][j] == 2 and adjacent:
                    pieces += 1
                else:
                    break
                    # adjacent = False
                    # if board[i][j] == 0:
                    #     counter += 1
                    # elif board[i][j] == 2:
                    #     if counter % 2 == 1:
                    #         pieces -= counter
                    # else:
                    #     counter = 0
        counter = 0
        adjacent = True
        for i in range(length):
            for j in range(length, 0, -1):
                if board[i][j] == 2 and adjacent:
                    pieces += 1
                else:
                    break
                    # adjacent = False
                    # if board[i][j] == 0:
                    #     counter += 1
                    # elif board[i][j] == 2:
                    #     if counter % 2 == 1:
                    #         pieces -= counter
                    # else:
                    #     counter = 0
        counter = 0
        adjacent = True
        for i in range(length, 0, -1):
            for j in range(length, 0, -1):
                if board[i][j] == 2 and adjacent:
                    pieces += 1
                else:
                    break
                    # adjacent = False
                    # if board[i][j] == 0:
                    #     counter += 1
                    # elif board[i][j] == 2:
                    #     if counter % 2 == 1:
                    #         pieces -= counter
                    # else:
                    #     counter = 0

        return pieces

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    if color == 1:
        curr_color = 2
    else:
        curr_color = 1
    
    # Get possible moves for light
    moves = get_possible_moves(board, curr_color)
    # Terminal State
    if not moves or limit == 0:
        return (), compute_utility(board, color)

    curr_min = float("inf")
    curr_move = moves[0]
    
    for move in moves:
        # Move as light player
        new_board = play_move(board, curr_color, move[0], move[1])
        # Retrieve darks's best subsequent move from light's move
        if caching:
            if new_board in state_dict:
                value = state_dict[new_board]
            # if new_board in min_dict:
            #     value = min_dict[new_board]
            else:
                value = minimax_max_node(new_board, color, limit-1)[1]
                state_dict[new_board] = value
                # min_dict[new_board] = value
        else:
            value = minimax_max_node(new_board, color, limit-1)[1]
            
        if value < curr_min:
            curr_min = value
            curr_move = move
    
    return curr_move, curr_min



def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    # Get possible moves for dark
    moves = get_possible_moves(board, color)
    
    # Terminal State
    if not moves or limit == 0:
        return (), compute_utility(board, color)

    curr_max = float("-inf")
    curr_move = moves[0]
    
    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        if caching:
            if new_board in state_dict:
                value = state_dict[new_board]
            # if new_board in max_dict:
            #     value = max_dict[new_board]
            else:
                value = minimax_min_node(new_board, color, limit-1)[1]
                state_dict[new_board] = value   
                # max_dict[new_board] = value
        else:
            value = minimax_min_node(new_board, color, limit-1)[1]
            
        if value > curr_max:
            curr_max = value
            curr_move = move
    
    return curr_move, curr_max

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
    move = minimax_max_node(board, color, limit, caching)
    return move[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if color == 1:
        curr_color = 2
    else:
        curr_color = 1

    moves = get_possible_moves(board, curr_color)
    
    # Terminal State
    if not moves or limit == 0:
        return (), compute_utility(board, color)

    ut_val = float("inf")
    curr_move = moves[0]

    moves_values = []

    if ordering:
        for move in moves:
            new_board = play_move(board, curr_color, move[0], move[1])
            moves_values.append((move, compute_utility(new_board, curr_color)))

        moves_values.sort(key=lambda y: y[1], reverse=True)
        moves = (x[0] for x in moves_values)

    for move in moves:
        new_board = play_move(board, curr_color, move[0], move[1])

        if caching:
            if new_board in state_dict:
                value = state_dict[new_board]
            # if new_board in min_dict:
            #     value = min_dict[new_board]
            else:
                value = alphabeta_max_node(new_board, color, alpha, beta, limit-1, caching, ordering)[1]
                state_dict[new_board] = value
                # min_dict[new_board] = value
        else:
            value = alphabeta_max_node(new_board, color, alpha, beta, limit-1, caching, ordering)[1]

        ut_val = min(ut_val, value)

        if beta > ut_val:
            beta = ut_val
            curr_move = move
            if beta <= alpha:
                break
                
    return curr_move, beta

    
def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # Get possible moves for dark
    moves = get_possible_moves(board, color)
    
    # Terminal State
    if not moves or limit == 0:
        return (), compute_utility(board, color)
    
    ut_val = float("-inf")
    curr_move = moves[0]

    moves_values = []

    if ordering:
        for move in moves:
            new_board = play_move(board, color, move[0], move[1])
            moves_values.append((move, compute_utility(new_board, color)))

        moves_values.sort(key=lambda y: y[1], reverse=True)
        moves = [x[0] for x in moves_values]

    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        
        if caching:
            if new_board in state_dict:
                value = state_dict[new_board]
            # if new_board in max_dict:
            #     value = max_dict[new_board]
            else:
                value = alphabeta_min_node(new_board, color, alpha, beta, limit-1, caching, ordering)[1]
                state_dict[new_board] = value
                # max_dict[new_board] = value
        else:
            value = alphabeta_min_node(new_board, color, alpha, beta, limit-1, caching, ordering)[1]

        ut_val = max(ut_val, value)

        if alpha < ut_val:
            alpha = ut_val
            curr_move = move
            if beta <= alpha:
                break
                
    return curr_move, alpha



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
    move = alphabeta_max_node(board, color, float("-inf"), float("inf"), limit, caching, ordering)
    return move[0]

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Wolfgang AI") # First line is the name of this AI
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
