"""
An AI player for Othello. 
"""

import random
import sys
import time
cache = {}
"""
Advanced heuristic function contains three parts:
1. parity
parity_value is calculated based on the number of current pieces of both players.
We just subtract two values and divide by sum of two values and multiply by 100 to get the parity_value.
2. mobility
mobility_value is calculated based on the current number of choice of next step for both players.
We just subtract two values and divide by sum of two values and multiply by 100 to get the mobility_value.
3. corners captured and stability
If a piece is placed on the corner, then it will never be flanked. Thus, we can calculate corners_value based on the 
number of corners already taken by both players. 
We just subtract two values and divide by sum of two values and multiply by 100 to get the corners_value.

Furthermore, we can also assume the pieces that connected with own corner piece is stable. If a piece is connected with corner
and formed an island, then it will also never be flanked. Thus, we calculate the stability_value based on the current number of pieces that 
connected with own corner piece. 
We just subtract two values and divide by sum of two values and multiply by 100 to get the stability_value.
Finally, we can sum up these values together to get our final utility.
"""
# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    scores = get_score(board=board)
    return scores[0] - scores[1] if color == 1 else scores[1] - scores[0]#change this!

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    # parity
    m, n = len(board), len(board[0])
    scores = get_score(board)
    curr_score = scores[0] if color == 1 else scores[1]
    oppo_score = scores[1] if color == 1 else scores[0]
    parity_value = 100 * ((curr_score - oppo_score) / (curr_score + oppo_score))
    # mobility
    curr_moves, oppo_moves = len(get_possible_moves(board, color)), len(get_possible_moves(board, 3-color))
    if curr_score > oppo_score and curr_moves == 0:
        return float("inf")
    mobility_value = 100 * (curr_moves - oppo_moves) / (curr_moves + oppo_moves) if (curr_moves + oppo_moves) != 0 else 0
    # corners captured and stability
    corners = [(0, 0), (-1, 0), (0, -1), (-1, -1)]
    curr_corners, oppo_corners, curr_stability, oppo_stability = 0, 0, 0, 0
    board_copy = copy_board(board)
    for i, j in corners:
        if board[i][j] == color:
            curr_corners += 1
            curr_stability += find_stable_disc(board_copy, color, i, j, m, n)
        elif board[i][j] == 0:
            continue
        else:
            oppo_corners += 1
            oppo_stability += find_stable_disc(board_copy, 3-color, i, j, m, n)

    corners_value = 100 * (curr_corners - oppo_corners) / (curr_corners + oppo_corners) if (curr_corners + oppo_corners) != 0 else 0
    stability_value = 100 * (curr_stability - oppo_stability) / (curr_stability + oppo_stability) if (curr_stability + oppo_stability) != 0 else 0
    return parity_value + mobility_value + corners_value + stability_value

def find_stable_disc(board, color, i, j, m, n):
    total = 0
    dirctions = [[0, 1], [1, 0], [0, -1], [-1, 0]]
    lst = [[_[0] + i, _[1] + j] for _ in dirctions]
    while lst:
        cell = lst.pop()
        i, j = cell[0], cell[1]
        if 0 <= i < n and 0 <= j < m:
            if board[i][j] == color:
                total += 1
                lst.extend([[_[0] + i, _[1] + j] for _ in dirctions])
                board[i][j] = 0
    return total




def copy_board(board):
    board_copy = [[0] * len(board[0]) for _ in range(len(board))]
    for i in range(len(board)):
        for j in range(len(board[0])):
            board_copy[i][j] = board[i][j]
    return board_copy
############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)
    if caching != 0 and board in cache:
        return cache[board]
    opponent = 2 if color == 1 else 1
    possible_moves = get_possible_moves(board, opponent)
    if possible_moves == [] or limit == 0:
        return None, compute_utility(board, color)
    best_move = None
    min_utility = float("inf")
    for move in possible_moves:
        new_state = play_move(board, opponent, move[0], move[1])
        _, utility = minimax_max_node(new_state, color, limit-1, caching)
        if utility < min_utility:
            min_utility = utility
            best_move = move
        if caching != 0:
            cache[new_state] = (move, utility)
    return best_move, min_utility


def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    if caching != 0 and board in cache:
        return cache[board]
    possible_moves = get_possible_moves(board, color)
    if possible_moves == [] or limit == 0:
        return None, compute_utility(board, color)
    best_move = None
    max_utility = -float("inf")
    for move in possible_moves:
        new_state = play_move(board, color, move[0], move[1])
        _, utility = minimax_min_node(new_state, color, limit - 1, caching)
        if utility > max_utility:
            max_utility = utility
            best_move = move
        if caching != 0:
            cache[new_state] = (move, utility)
    return best_move, max_utility


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
    cache.clear()
    return minimax_max_node(board, color, limit, caching)[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    if caching != 0 and board in cache:
        return cache[board]
    opponent = 2 if color == 1 else 1
    possible_moves = get_possible_moves(board, opponent)

    if possible_moves == [] or limit == 0:
        return None, compute_utility(board, color)
    best_move = None
    min_utility = float("inf")
    new_states = []
    for move in possible_moves:
        new_states.append((play_move(board, opponent, move[0], move[1]), move))
    """
    if ordering != 0:
        new_states.sort(key=lambda x: compute_utility(x[0], color), reverse=True)
    """
    for new_state in new_states:
    #    new_state = play_move(board, color, move[0], move[1])
        _, utility = alphabeta_max_node(new_state[0], color, alpha, beta, limit - 1, caching, ordering)
        if utility < min_utility:
            min_utility = utility
            best_move = new_state[1]
        if caching:
            cache[new_state[0]] = (new_state[1], utility)
        if beta > utility:
            beta = utility
        if beta <= alpha:
            break
    '''
    if caching != 0:
        cache[board] = (best_move, min_utility)
    '''
    return best_move, min_utility

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    if caching != 0 and board in cache:
        return cache[board]
    possible_moves = get_possible_moves(board, color)
    if possible_moves == [] or limit == 0:
        return None, compute_utility(board, color)
    best_move = None
    max_utility = -float("inf")
    new_states = []
    for move in possible_moves:
        new_states.append((play_move(board, color, move[0], move[1]), move))
    if ordering != 0:
        new_states.sort(key=lambda x: compute_utility(x[0], color), reverse=True)
    for new_state in new_states:
     #   new_state = play_move(board, color, move[0], move[1])
        _, utility = alphabeta_min_node(new_state[0], color, alpha, beta, limit - 1, caching, ordering)
        if utility > max_utility:
            max_utility = utility
            best_move = new_state[1]
        if caching:
            cache[new_state[0]] = (new_state[1], utility)
        if alpha < utility:
            alpha = utility
        if beta <= alpha:
            break
    '''
    if caching != 0:
        cache[board] = (best_move, max_utility)
    '''
    return best_move, max_utility

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
    return alphabeta_max_node(board, color, -float("inf"), float("inf"), limit, caching, ordering)[0]

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
