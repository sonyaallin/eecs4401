"""
An AI player for Othello.

For this porject the heursitic I designed took the normal utlity score of the board and added 1 per corner
piece the player had and subtracted 1 per corner piece the enemy had. Also the more moves the board gave the
player the higher value it got the more moves the board gave the opponent the lower value the board got
"""

import random
import sys
import time
import math

printing = False
counter = 0
state_dict = {}

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)

def reverse_color(color):
    if color == 1:
        return 2
    else:
        return 1
# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    utility = 0
    p1Score, p2Score = get_score(board)
    if color == 1:
        utility = p1Score - p2Score
    else:
        utility = p2Score - p1Score
    return utility #change this!

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    utility = 0
    p1Score, p2Score = get_score(board)
    if color == 1:
        utility = p1Score - p2Score
    else:
        utility = p2Score - p1Score
    if board[0][0] == color:
        utility += 1
    else:
        utility -= 1
    if board[0][-1] == color:
        utility += 1
    else:
        utility -= 1
    if board[-1][0] == color:
        utility += 1
    else:
        utility -= 1
    if board[-1][-1] == color:
        utility += 1
    else:
        utility -= 1
    utility += get_possible_moves(board, color)
    utility -= get_possible_moves(board, reverse_color(color))
    return utility

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0, level = 1):
    global printing
    global state_dict
    #IMPLEMENT (and replace the line below)
    possible_moves = get_possible_moves(board, reverse_color(color))
    if len(possible_moves) == 0:
        if board in state_dict and caching:
            if state_dict[board][0] != math.inf:
                return ((0,0), state_dict[board][0])
            else:
                util = compute_utility(board, color)
                state_dict[board][0] = util
        else:
            util = compute_utility(board, color)
            state_dict[board] = [util, math.inf]
        return((0, 0), util)
    elif limit == 0:
        if board in state_dict and caching:
            if state_dict[board][0] != math.inf:
                return ((0,0), state_dict[board][0])
            else:
                util = compute_utility(board, color)
                state_dict[board][0] = util
        else:
            util = compute_utility(board, color)
            state_dict[board] = [util, math.inf]
        return (None, util)
    else:
        min_node = math.inf
        for move in possible_moves:
            new_board = play_move(board,reverse_color(color),move[0], move[1])
            if new_board in state_dict and caching:
                if state_dict[new_board][0] != math.inf:
                    temp_node = state_dict[new_board][0]
                else:
                    temp_node = minimax_max_node(new_board, color, limit - 1, caching, level + 1)[1]
                    state_dict[new_board][0] = temp_node
            else:
                temp_node = minimax_max_node(new_board, color, limit - 1, caching, level + 1)[1]
                state_dict[new_board] = [temp_node, math.inf]
            if  temp_node < min_node:
                min_node = temp_node
                min_move = move
        return (min_move, min_node)

def minimax_max_node(board, color, limit, caching = 0, level = 1): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    global printing
    global state_dict
    possible_moves = get_possible_moves(board, color)
    if len(possible_moves) == 0:
        if board in state_dict and caching:
            if state_dict[board][1] != math.inf:
                return ((0,0), state_dict[board][1])
            else:
                util = compute_utility(board, color)
                state_dict[board][1] = util
        else:
            util = compute_utility(board, color)
            state_dict[board] = [math.inf, util]
        return((0, 0), util)
    elif limit == 0:
        if board in state_dict and caching:
            if state_dict[board][1] != math.inf:
                return ((0,0), state_dict[board][1])
            else:
                util = compute_utility(board, color)
                state_dict[board][1] = util
        else:
            util = compute_utility(board, color)
            state_dict[board] = [math.inf, util]
        return (None, util)
    else:
        max_node = -math.inf
        for move in possible_moves:
            if move == (0,1) and level == 1:
                printing = True
            elif level == 1:
                printing = False
            new_board = play_move(board,color,move[0], move[1])
            if new_board in state_dict and caching:
                if state_dict[new_board][1] != math.inf:
                    temp_node = state_dict[new_board][1]
                else:
                    temp_node = minimax_min_node(new_board, color, limit - 1, caching, level + 1)[1]
                    state_dict[new_board][1] = temp_node
            else:
                temp_node = minimax_min_node(new_board, color, limit - 1, caching, level + 1)[1]
                state_dict[new_board] = [math.inf, temp_node]
            if temp_node > max_node:
                max_node = temp_node
                max_move = move
        return (max_move, max_node)
            

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
    global state_dict
    state_dict = {}
    return minimax_max_node(board, color, limit, caching, 1)[0]
        
    

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    global printing
    global state_dict
    #IMPLEMENT (and replace the line below)
    possible_moves = get_possible_moves(board, reverse_color(color))
    if len(possible_moves) == 0:
        if board in state_dict and caching:
            if state_dict[board][0] != math.inf:
                return ((0,0), state_dict[board][0])
            else:
                util = compute_utility(board, color)
                state_dict[board][0] = util
        else:
            util = compute_utility(board, color)
            state_dict[board] = [util, math.inf]

        return((0, 0), util)
    elif limit == 0:
        if board in state_dict and caching:
            if state_dict[board][0] != math.inf:
                return ((0,0), state_dict[board][0])
            else:
                util = compute_utility(board, color)
                state_dict[board][0] = util
        else:
            util = compute_utility(board, color)
            state_dict[board] = [util, math.inf]
        return (None, util)
    else:
        min_node = math.inf
        if ordering:
            order_node = []
            for move in possible_moves:
                new_board = play_move(board,reverse_color(color),move[0], move[1])
                util = compute_utility(new_board, color)
                order_node.append((move, util))
            order_node = sorted(order_node, key= lambda a : a[1], reverse= False)
            for node in order_node:
                move = node[0]
                new_board = play_move(board,reverse_color(color),move[0], move[1])
                if new_board in state_dict and caching:
                    if state_dict[new_board][0] != math.inf:
                        temp_node = state_dict[new_board][0]
                    else:
                        temp_node = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
                        state_dict[new_board][0] = temp_node
                else:
                    temp_node = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
                    state_dict[new_board] = [temp_node, math.inf]
                if  temp_node < min_node:
                    min_node = temp_node
                    min_move = move
                if beta > min_node:
                    beta = min_node
                    if beta <= alpha:
                        break
            return (min_move, min_node)
        else:
            for move in possible_moves:
                new_board = play_move(board,reverse_color(color),move[0], move[1])
                if new_board in state_dict and caching:
                    if state_dict[new_board][0] != math.inf:
                        temp_node = state_dict[new_board][0]
                    else:
                        temp_node = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
                        state_dict[new_board][0] = temp_node
                else:
                    temp_node = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
                    state_dict[new_board] = [temp_node, math.inf]
                if  temp_node < min_node:
                    min_node = temp_node
                    min_move = move
                if beta > min_node:
                    beta = min_node
                    if beta <= alpha:
                        break
            return (min_move, min_node)            

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    global printing
    possible_moves = get_possible_moves(board, color)
    if len(possible_moves) == 0:
        if board in state_dict and caching:
            if state_dict[board][1] != math.inf:
                return ((0,0), state_dict[board][1])
            else:
                util = compute_utility(board, color)
                state_dict[board][1] = util
        else:
            util = compute_utility(board, color)
            state_dict[board] = [math.inf, util]
        return((0, 0), util)
    elif limit == 0:
        if board in state_dict and caching:
            if state_dict[board][1] != math.inf:
                return ((0,0), state_dict[board][1])
            else:
                util = compute_utility(board, color)
                state_dict[board][1] = util
        else:
            util = compute_utility(board, color)
            state_dict[board] = [math.inf, util]
        return (None, util)
    else:
        max_node = -math.inf
        if ordering:
            order_node = []
            for move in possible_moves:
                new_board = play_move(board,color,move[0], move[1])
                util = compute_utility(new_board, color)
                order_node.append((move, util))
            order_node = sorted(order_node, key= lambda a : a[1], reverse= True)
            for node in order_node:
                move = node[0]
                new_board = play_move(board,color,move[0], move[1])
                if new_board in state_dict and caching:
                    if state_dict[new_board][1] != math.inf:
                        temp_node = state_dict[new_board][1]
                    else:
                        temp_node = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
                        state_dict[new_board][1] = temp_node
                else:
                    temp_node = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
                    state_dict[new_board] = [math.inf, temp_node]
                if temp_node > max_node:
                    max_node = temp_node
                    max_move = move
                if alpha < max_node:
                    alpha = max_node
                    if beta <= alpha:
                        break
            return (max_move, max_node)
        else:
            for move in possible_moves:
                new_board = play_move(board,color,move[0], move[1])
                if new_board in state_dict and caching:
                    if state_dict[new_board][1] != math.inf:
                        temp_node = state_dict[new_board][1]
                    else:
                        temp_node = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
                        state_dict[new_board][1] = temp_node
                else:
                    temp_node = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
                    state_dict[new_board] = [math.inf, temp_node]
                if temp_node > max_node:
                    max_node = temp_node
                    max_move = move
                if alpha < max_node:
                    alpha = max_node
                    if beta <= alpha:
                        break
            return (max_move, max_node)            


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
    global state_dict
    state_dict = {}
    return alphabeta_max_node(board, color, -math.inf, math.inf, limit,caching, ordering)[0]

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


