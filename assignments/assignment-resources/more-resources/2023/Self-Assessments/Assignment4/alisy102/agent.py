"""
An AI player for Othello.
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

MIN_DP = {}
MAX_DP = {}
BETA_DP = {}
ALPHA_DP = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)

# Method to compute utility value of terminal state
def compute_utility(board, color):
    p1, p2 = get_score(board)
    if color == 1:
        return p1 - p2 #change this!
    return p2 - p1

# Better heuristic value of board
def compute_heuristic(board, color):
    good = [(0,0), (0,len(board)-1), (len(board)-1, 0), (len(board)-1, len(board)-1)] # corner pieces
    player = get_possible_moves(board, color)
    opp = get_possible_moves(board, 3-color)
    p1, p2 = get_score(board)
    rem = ((p1 + p2) / (len(board)**2)) # percentage of board occupied (helps to identify start / end phase)

    visited = set()
    def dfs(i, j, color): #look for cluster of fixed pieces
        if (i, j) in visited:
            return 0
        visited.add((i, j))
        nxt = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        score = 1
        for u, v in nxt:
            if 0 <= i+u < len(board) and 0 <= j+v < len(board):
                if board[i+u][j+v] == color and check_ifcorner(i+u, j+v, color):
                    score += dfs(i+u, j+v, color)
        
        return score
    
    def check_ifcorner(i, j, color): #checks if i, j is a fixed piece
        corners = [[(1, 0), (1, -1), (0, -1)], [(0, -1), (-1, -1), (-1, 0)],  
                [(-1, 0), (-1, 1), (0, 1)], [(0, 1), (1, 1), (1, 0)]]

        for c in corners:
            isC = True
            for u, v in c:
                if len(board) > (i+u) >= 0 and len(board) > (j+v) >= 0:
                    if (board[i+u][j+v] != color):
                        isC = False
            if isC:
                return True
        return False

    s = 0
    for i, j in good:
        if board[i][j] == color:
            s += (len(board)-3)*dfs(i, j, color)*rem #fixed pieces for player (more weight for end game)
    
    for i, j in good:
        if board[i][j] == 3-color:
            s -= (len(board)-3)*dfs(i, j, 3-color) #fixed pieces for opponent

    # in the previous few lines, starting at the corner pieces, we found all fixed
    # pieces that were clustered around the corners for player and opponent


    danger = set()
    for i in range(1,len(board)-1):  # inner ring is a danger zone
        danger.add(((1,i), (0, i)))
        danger.add(((i,1), (i, 0)))
        danger.add(((len(board)-2,i), (len(board)-1, i)))
        danger.add(((i,len(board)-2), (i,len(board)-1)))

    for c, d in danger: # more points if opposition is in danger zone 
        if board[c[0]][c[1]] == 3-color and board[d[1]][d[0]] != 3-color:
            s += (1/(rem*100)) # try to guide opponent in to danger zone during early phase

    if color == 1:
        s += p1 - p2
    else:
        s += p2 - p1

    for i, j in player:
        lines = find_lines(board, i, j, color)
        for line in lines:
            s += len(lines)   # disks player can flip
    for i, j in opp:
        lines = find_lines(board, i, j, 3-color)
        for line in lines:
            s -= len(lines) # disks opposition can flip
    return s

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)
    if caching and (color, str(board)) in MIN_DP:
        return MIN_DP[(color, str(board))]
    opp = 1
    if color == 1: opp = 2
    moves = get_possible_moves(board, opp)
    if not moves or not limit:
        return (-1, -1), compute_utility(board, color)

    m = (-1, -1), float('inf')
    for c in moves:
        next_board = play_move(board, opp, c[0], c[1])
        n = c, minimax_max_node(next_board, color, limit-1, caching)[1]
        m = min(m, n, key=lambda x: x[1])
    MIN_DP[(color, str(board))] = m
    return m

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    if caching and (color, str(board)) in MAX_DP:
        return MAX_DP[(color, str(board))]
    moves = get_possible_moves(board, color)
    if not moves or not limit:
        return (-1, -1), compute_utility(board, color)

    m = (-1, -1), float('-inf')
    for c in moves:
        next_board = play_move(board, color, c[0], c[1])
        n = c, minimax_min_node(next_board, color, limit-1, caching)[1]
        m = max(m, n, key=lambda x: x[1])
    MAX_DP[(color, str(board))] = m
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
    #IMPLEMENT (and replace the line below)
    return minimax_max_node(board, color, limit, caching)[0] #change this!

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    if caching and (color, str(board)) in BETA_DP:
        return BETA_DP[(color, str(board))]
    opp = 1
    if color == 1: opp = 2
    moves = get_possible_moves(board, opp)
    if not moves or not limit:
        return (-1, -1), compute_utility(board, color)

    m = (-1, -1), beta
    moves = [(c, play_move(board, opp, c[0], c[1])) for c in moves]
    if ordering:
        moves.sort(key=lambda x: compute_utility(x[1], color))
    for c in moves:
        #next_board = play_move(board, opp, c[0], c[1])
        n = c[0], alphabeta_max_node(c[1], color, alpha, beta, limit-1, caching, ordering)[1]
        m = min(m, n, key=lambda x: x[1])
        beta = m[1]
        if beta <= alpha:
            break
    BETA_DP[(color, str(board))] = m
    return m

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    if caching and (color, str(board)) in ALPHA_DP:
        return ALPHA_DP[(color, str(board))]
    moves = get_possible_moves(board, color)
    if not moves or not limit:
        return (-1, -1), compute_utility(board, color)

    m = (-1, -1), alpha
    moves = [(c, play_move(board, color, c[0], c[1])) for c in moves]
    if ordering:
        moves.sort(key=lambda x: compute_utility(x[1], color), reverse=True)
    for c in moves:
        # next_board = play_move(board, color, c[0], c[1])
        n = c[0], alphabeta_min_node(c[1], color, alpha, beta, limit-1, caching, ordering)[1]
        m = max(m, n, key=lambda x: x[1])
        alpha = m[1]
        if beta <= alpha:
            break
    ALPHA_DP[(color, str(board))] = m
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
    #IMPLEMENT (and replace the line below)
    return alphabeta_max_node(board, color, float('-inf'), float('inf'), limit, caching, ordering)[0] #change this!

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
