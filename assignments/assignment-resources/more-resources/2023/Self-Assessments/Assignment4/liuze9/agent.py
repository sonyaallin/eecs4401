"""
An AI player for Othello. 
"""
'''
My custom heuristic considers 3 factors, the difference between the amount of the players pieces (h1), number of corners captured(h2), 
and the difference between the amount of move the two players can do(h3). 
h1 and h2 are divided by the total amount of (pieces/moves) since as the board grows wider the difference will be greater 
(eg. in  10x10 board having an extra 5 pieces can be gained esily while in a 5x5 board having 5 extra pieces is much more singifactn)
while the amount of corners is always the same.

'''

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

states = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    s = get_score(board)
    if color == 1:
        return s[0] - s[1]
    return s[1] - s[0]

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    '''
    My custom heuristic considers 3 factors, the difference between the amount of the players pieces (h1), number of corners captured(h2), 
    and the difference between the amount of move the two players can do(h3). 
    h1 and h2 are divided by the total amount of (pieces/moves) since as the board grows wider the difference will be greater 
    (eg. in  10x10 board having an extra 5 pieces can be gained esily while in a 5x5 board having 5 extra pieces is much more singifactn)
    while the amount of corners is always the same.

    '''
    u = compute_utility(board, color)
    s = get_score(board)
    h1 = 0
    if s[0]+s[1] !=0:
        h1 = (u/(s[0]+s[1]))
    corners = [board[-1][-1],board[-1][0],board[0][0],board[0][-1]]
    c1=0
    c2=0
    for c in corners:
        if c==color:
            c1+=1
        elif c!=0:
            c2+=1
    h2 = 0
    if c1+c1!=0:
        h2 = 10*(c1-c2)
    am1 = len(get_possible_moves(board,color))
    am2 = len(get_possible_moves(board,1+(color==1)))
    h3 = 0
    if am1+am2!=0:
        h3 = (am1-am2)/(am1+am2)
    return h1+h2+h3
    

    
    


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    if caching==1 and board in states:
        return states[board]
    m = (None, float('inf'))
    moves = get_possible_moves(board,1+(color==1))
    if moves == [] or limit == 0:
        m = (None, compute_utility(board, color))
        states[board] = m
        return m
    limit -= 1
    for move in moves:
        new_board = play_move(board, 1+(color==1), move[0], move[1])
        score = minimax_max_node(new_board, color, limit, caching)[1]
        if score < m[1]:
            m=(move,score)
    states[board] = m
    return m

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    if caching==1 and board in states:
        return states[board]
    m = (None, float('-inf'))
    moves = get_possible_moves(board,color)
    if moves == [] or limit == 0:
        m = (None, compute_utility(board, color))
        states[board] = m
        return m
    limit -= 1
    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        score = minimax_min_node(new_board, color, limit, caching)[1]
        if score > m[1]:
            m=(move,score)
    states[board] = m
    return m

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
    
    return minimax_max_node(board, color, limit, caching)[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching==1 and board in states:
        return states[board]
    m = (None, float('inf'))
    moves = get_possible_moves(board,1+(color==1))
    new_boards = []
    for move in moves:
        b = play_move(board, 1+(color==1), move[0], move[1])
        u = compute_utility(b, color)
        i = 0
        if ordering == 1:
            while i<len(new_boards):
                if u > new_boards[i][1]:
                    new_boards.insert(i, (b,u,move))
                    i = len(new_boards)
                i+=1
        else:
            new_boards.append((b,u,move))

    if moves == [] or limit==0:
        m = (None, compute_utility(board, color))
        states[board] = m
        return m
    limit -= 1
    for b in new_boards:
        score = alphabeta_max_node(b[0],color, alpha, beta, limit, caching, ordering)[1]
        if score < beta:
            beta = score
        if alpha >= beta:
            return (None, float('-inf'))
        if score < m[1]:
            m=(b[2],score)
    states[board] = m
    return m

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching ==1 and board in states:
        return states[board]
    m = (None, float('-inf'))
    moves = get_possible_moves(board,color)
    new_boards = []
    for move in moves:
        b = play_move(board, color, move[0], move[1])
        u = compute_utility(b, color)
        i = 0
        if ordering ==1:
            while i<len(new_boards):
                if u > new_boards[i][1]:
                    new_boards.insert(i, (b,u,move))
                    i = len(new_boards)
                i+=1
        else:
            new_boards.append((b,u,move))
    if moves == [] or limit==0:
        m = (None, compute_utility(board, color))
        states[board] = m
        return m
    limit -= 1
    for b in new_boards:
        score = alphabeta_min_node(b[0], color, alpha, beta, limit, caching, ordering)[1]
        if score > alpha:
            alpha = score
        if alpha >= beta:
            return (None, float('inf'))
        if score > m[1]:
            m = (b[2],score)
    states[board] = m
    return m

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
