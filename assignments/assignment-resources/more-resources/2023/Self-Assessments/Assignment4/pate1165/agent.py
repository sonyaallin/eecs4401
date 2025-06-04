"""
An AI player for Othello. 

Description For Heuristic:
- we want to maximize our moves so i start with the number of moves we can make
- next corners are very good and stable places so i put weighted for that high
- the square that is one away from the outside is very bad and is the "danger zone" and i decrease the value of
it if it has chips on this zone
- I also check for peices around the corner as if the corner is not yours then it is very bad to take the squares 
around the corner as it dangourous as the opponent can easily take those chips as they already have the corner
- chips on the wall are very good as they are pretty stable so i check for this and increase the value to return

"""

import random
import sys
import time
import math # ADDED THIS IMPORT
# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move
cache_dict = {}
cache_dict_max = {}




def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    s = get_score(board)
    

    #Dark Color
    if color == 2:
        return s[1] - s[0]
    #Light Color 
    return s[0] - s[1] 

# Better heuristic value of board
#***Description: At the top of this file***
def compute_heuristic(board, color): #not implemented, optional

    x = len(board)
    y = len(board[0])

    #GET UR MOVES - want to maximize this
    val = len(get_possible_moves(board, color))
    

    #corner checks **very good**
    if board[0][0] == color:
        val = val*50
    if board[0][y-1] == color:
        val = val*50
    if board[x-1][0] == color:
        val = val*50
    if board[x-1][y-1] == color:
        val = val*50

    #Bad zones - lower val
    for i in range(1,x):
        if board[i][1] == color:
            val *= 0.8
        if board[i][x-1] == color:
            val *= 0.8
        if board[1][i]  == color:
            val *= 0.8
        if board[y-1][i]  == color:
            val *= 0.8

    #Walls
    for i in range(0,x):
        if board[0][i] == color:
            val = val*5000
        if board[x-1][i] == color:
            val = val*5000
        if board[i][0] == color:
            val = val*5000
        if board[i][x-1] == color:
            val = val*5000
        

    #right outside of the corner 
    if board[0][0] != color and color in [board[0][1],board[1][0],board[1][0]]:
        val = val*0.20
    if board[0][y-1] != color and color in [board[0][y-2],board[1][y-1],board[1][y-2]]:
        val = val*0.20
    if board[x-1][0] == color and color in [board[x-1][1],board[x-2][0],board[x-2][1]]:
        val = val*0.20
    if board[x-1][y-1] == color and color in [board[x-1][y-2],board[x-2][y-1],board[x-2][y-2]]:
        val = val*0.20
        
    return val 

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    if caching == 1 and (board,color) in cache_dict.keys():
        return cache_dict[(board,color)]
    if color == 1:
        new_color = 2
    else:
        new_color = 1
    pos_move = get_possible_moves(board, new_color)

    #Base Case                                     
    if pos_move == [] or limit == 0:
        return ((0,0),compute_utility(board,color))
    limit -= 1

    high = math.inf
    ret = ()

    for x in pos_move:
        m = minimax_max_node(play_move(board, new_color, x[0], x[1]), color, limit, caching)
        if m[1] < high:
            high = m[1]
            ret = x
    if caching == 1:
        cache_dict[((board,color))] = (ret,high)
    return (ret,high)


def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility

    #Base Case
    if caching == 1 and (board,color) in cache_dict_max.keys():
        return cache_dict_max[(board,color)]
    #IMPLEMENT (and replace the line below)
    pos_move = get_possible_moves(board, color)
    #Base Case
    

    if pos_move == [] or limit == 0:
        return ((0,0),compute_utility(board,color))
    limit -= 1
    low = -math.inf
    ret = ()



    for x in pos_move:
        m = minimax_min_node(play_move(board, color, x[0], x[1]), color, limit, caching)
        if m[1] > low:
            low = m[1]
            ret = x
    if caching == 1:
        cache_dict_max[(board,color)] = (ret,low)
    return (ret,low)

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
    return minimax_max_node(board, color, limit, caching)[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching == 1 and (board,color) in cache_dict.keys():
        return cache_dict[(board,color)]
    if color == 1:
        new_color = 2
    else:
        new_color = 1

    pos_move = get_possible_moves(board, new_color)
    #Base Case                                     
    if pos_move == [] or limit == 0:
        return ((0,0),compute_utility(board,color))
    limit -= 1

    high = math.inf
    ret = ()
    if ordering == 1:
        sorted_moves = [(compute_utility(play_move(board,new_color,p[0],p[1]),color),p) for p in pos_move]
        sorted_moves.sort()
        for x in sorted_moves:
            m = alphabeta_max_node(play_move(board, new_color, x[1][0], x[1][1]), color, alpha, beta, limit, caching, ordering)
            if m[1] < high:
                high = m[1]
                ret = x[1]

            if beta > high:
                beta = high
                if beta <= alpha:
                    break
    else:
    
        for x in pos_move:
            m = alphabeta_max_node(play_move(board, new_color, x[0], x[1]), color, alpha, beta, limit, caching, ordering)
            if m[1] < high:
                high = m[1]
                ret = x

            if beta > high:
                beta = high
                if beta <= alpha:
                    break

    if caching == 1:
        cache_dict[((board,color))] = (ret,high)
    return (ret,high)


def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching == 1 and ((board,color) in cache_dict_max.keys()):
        return cache_dict_max[(board,color)]
    #Base Case

    #IMPLEMENT (and replace the line below)
    pos_move = get_possible_moves(board, color)
    #Base Case
    

    if pos_move == [] or limit == 0:
        return ((0,0),compute_utility(board,color))
    limit -= 1
    low = -math.inf
    ret = ()
    if ordering == 1:
        sorted_moves = [(compute_utility(play_move(board,color,p[0],p[1]),color),p) for p in pos_move]
        sorted_moves.sort(reverse=True)
        for x in sorted_moves:
            m = alphabeta_min_node(play_move(board, color, x[1][0], x[1][1]), color,alpha,beta, limit, caching,ordering)
            if m[1] > low:
                low = m[1]
                ret = x[1]
            if alpha < low:
                alpha = low
            #If alpha < beta is true then continue else we need to break
                if beta <= alpha:
                    break
    else:
        for x in pos_move:
            m = alphabeta_min_node(play_move(board, color, x[0], x[1]), color,alpha,beta, limit, caching,ordering)
            if m[1] > low:
                low = m[1]
                ret = x
            if alpha < low:
                alpha = low
            #If alpha < beta is true then continue else we need to break
                if beta <= alpha:
                    break
    if caching == 1:
        cache_dict_max[(board,color)] = (ret,low)
    return (ret,low)

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
    return alphabeta_max_node(board,color,-math.inf,math.inf,limit,caching,ordering)[0]

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
