"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move
"""
My heurstic take the same thing as compute utility and then also accounts for the moves available. And it also
takes into account how useful the corners are and how you shouldn't give up the corners.
"""
BOARDS={}
def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)

# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    p1,p2= get_score(board)
    if color==1:
        return p1-p2
    return p2-p1
    return 0 #change this!

# Better heuristic value of board
def test_square(board, color, x,y):
    if x >=len(board) or y >= len(board):
        return 0
    if board[x][y]==0:
        return 0
    if board[x][y]==color:
        return 1
    return -1
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    other_player= 1
    if color==1:
        other_player=2
    t= compute_utility(board, color)+ get_possible_moves(board, color)- get_possible_moves(board, other_player)
    t+= test_square(board,color, 0,0)
    t+= test_square(board, color, 0, len(board)-1)
    t+= test_square(board, color,len(board)-1,0)
    t+= test_square(board, color, len(board)-1, len(board)-1)
    t-= 3*test_square(board,color, 1,1)
    t-= 3*test_square(board,color, 1,len(board)-2)
    t-= 3*test_square(board,color, len(board)-2,1)
    t-= 3*test_square(board,color, len(board)-2,len(board)-2)
    t-=1.5*test_square(board, color, 0,1)
    t-=1.5*test_square(board, color, 1,0)
    t-=1.5*test_square(board, color, 1, len(board)-1)
    t-=1.5*test_square(board, color, 0, len(board)-2)
    t-=1.5*test_square(board, color,len(board)-1,1)
    t-=1.5*test_square(board, color, len(board)-2,0)
    t-=1.5*test_square(board, color, len(board)-2, len(board)-1)
    t-=1.5*test_square(board, color, len(board)-1, len(board)-2)
    return t #change this!

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)
    if caching and (board,color,0) in BOARDS:
        return BOARDS[(board, color,0)]
    other_player= 2
    if color==2:
        other_player=1
    moves = get_possible_moves(board, other_player)
    # print("min", board, moves, limit)
    if moves==[]:
        return (0,0), compute_utility(board, color)
    worst = ((0,0),999999999)
    l=[]
    for move in moves:
        board_after_move= play_move(board, other_player, move[0], move[1])
        if limit-1<=0 or (get_possible_moves(board_after_move, color)==[] and get_possible_moves(board_after_move, other_player)==[]):
            # print(move,board_after_move,  compute_utility(board_after_move, color))
            tmp = (move, compute_utility(board_after_move, color))
        else:
            tmp = minimax_max_node(board_after_move, color,limit-1, caching)
        if tmp[1]<worst[1]:
            worst= move, tmp[1]
        # if tmp[1] not in l:
        l.append(tmp[1])
    # print("min", l, worst, limit)
    if caching:
        BOARDS[(board, color,0)]= worst
    return worst

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    if caching and (board,color,1) in BOARDS:
        print(1)
        return BOARDS[(board, color,1)]
    other_player= 2
    if color==2:
        other_player=1
    moves = get_possible_moves(board, color)
    # print("max", board, moves, limit)
    if moves==[]:
        # print("yp")
        return (0,0), compute_utility(board, color)
    best = ((0,0),-999999999)
    l = []
    for move in moves:
        # print(move, limit)
        board_after_move= play_move(board, color, move[0], move[1])
        if limit-1 <=0  or (get_possible_moves(board_after_move, color)==[] and get_possible_moves(board_after_move, other_player)==[]):
            # print(move, board_after_move,  compute_utility(board_after_move, color))
            tmp = (move, compute_utility(board_after_move, color))
        else:
            tmp = minimax_min_node(board_after_move, color,limit-1, caching)
        if tmp[1]>best[1]:
            best= move, tmp[1]
        # if tmp[1] not in l:
        l.append(tmp[1])
    # print("max",l, best, limit)
    # print(best, board)
    if caching:
        BOARDS[(board, color,1)]= best
    return best

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
    # if color==1:
    return minimax_max_node(board, color, limit, caching)[0]
    # return minimax_min_node(board, 2, limit, caching)[0]
    #IMPLEMENT (and replace the line below)
    return (0,0) #change this!

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    if caching and (board,color,0) in BOARDS:
        return BOARDS[(board, color, 0)]
    other_player= 2
    if color==2:
        other_player=1
    moves = get_possible_moves(board, other_player)
    # print("max", board, moves, limit)
    if moves==[]:
        # print("yp",  compute_utility(board, color))
        return (0,0), compute_utility(board, color)
    worst = ((0,0),999999999)
    l= []
    if ordering:
        t = moves[:]
        moves.sort(key= lambda move: compute_utility(play_move(board, other_player, move[0], move[1]), color))
        if moves==t:
            print(1)
    for move in moves:
        if beta <= alpha:
            return worst
        board_after_move= play_move(board, other_player, move[0], move[1])
        if limit-1 <=0 or (get_possible_moves(board_after_move, color)==[] and get_possible_moves(board_after_move, other_player)==[]):
            tmp = (move, compute_utility(board_after_move, color))
        else:
            tmp = alphabeta_max_node(board_after_move, color,alpha, beta,limit-1, caching)
        if worst[1] is None or tmp[1]<worst[1]:
            worst= move, tmp[1]
        beta = min(beta, tmp[1])
        l.append((move, tmp[1]))
    if caching:
        BOARDS[(board, color,0)]= worst
    # if limit==1:
    #     print(l)
    return worst 
    return ((0,0),0) #change this!

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    if caching and (board,color,1) in BOARDS:
        return BOARDS[(board, color,1)]
    other_player= 2
    if color==2:
        other_player=1
    moves = get_possible_moves(board, color)
    # print("max", board, moves, limit)
    if moves==[]:
        # print("yp")
        return (0,0), compute_utility(board, color)
    best = ((0,0),-999999999)
    if ordering:
        moves.sort(key= lambda move: -compute_utility(play_move(board, color, move[0], move[1]), color))
    l= []
    for move in moves:
        if beta <= alpha:
            return best
        board_after_move= play_move(board, color, move[0], move[1])
        if limit-1 <=0 or (get_possible_moves(board_after_move, color)==[] and get_possible_moves(board_after_move, other_player)==[]):
            tmp = (move, compute_utility(board_after_move, color))
        else:
            tmp = alphabeta_min_node(board_after_move, color,alpha, beta,limit-1, caching)
        if best[1] is None or tmp[1]>best[1]:
            best= move, tmp[1]
        alpha = max(alpha, tmp[1])
        l.append((move, tmp[1]))
    if caching:
        BOARDS[(board, color,1)]= best
    # print(l)
    return best
    return ((0,0),0) #change this!

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
    # if color==1:
    return alphabeta_max_node(board, color, -999999999, 999999999,limit, caching, ordering)[0]
    # return alphabeta_min_node(board, 1, float('inf'), -float('inf'),limit, caching, ordering)[0]
    return (0,0) #change this!

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
