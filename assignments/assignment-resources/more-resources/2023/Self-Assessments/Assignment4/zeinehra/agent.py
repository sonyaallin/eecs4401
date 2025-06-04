"""
An AI player for Othello. 

My heuristic function, compute_heuristic, firstly ensures that there is at least one possible move left
as it would be a terminal state otherwise. If it is a terminal state, inf or -inf is returned
to represent that this is 100% a win/loss. Otherwise, it looks for strong pieces on board. Corner pieces
are searched and adjacent pieces as they are "stable" meaning they cannot be converted.
These pieces are given a higher weighting as they are strong pieces. The same but negative value
is given if the opponent has such pieces. To increase ai mobility and reduce
opponent mobility, the number of opponent moves is represented negatively and the number of
ai movements is represented positively. To add on that, the frontier of each piece is calculated
for the ai and the opponent. This means the number of adjacent empty tiles to ai pieces decreases
score and the number of adjacent tiles to opponent pieces increases score.
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    score = get_score(board)

    if color == 1:
        return score[0] - score[1]
    else:
        return score[1] - score[0]


# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    score = 0
    # If this is a terminal state, return a very large/small number to represent a very high heuristic for the winning player
    opposite_color = 1 if color == 2 else 2
    if len(get_possible_moves(board, color)) == 0 and len(get_possible_moves(board, opposite_color)) == 0:
        score = compute_utility(board, color)
        if score > 0:
            return float("inf")
        elif score < 0:
            return float("-inf")
        else:
            return 0
    
    # Check corners and adjacent "stable" pieces and give them higher value (2)
    score += check_stable_heuristic(board, color)
    score -= check_stable_heuristic(board, opposite_color)

    # Checks frontier of every piece
    score += frontier_heuristic(board, color, opposite_color)

    score += len(get_possible_moves(board, color)) - len(get_possible_moves(board, opposite_color))
    
    return score

# Returns heuristic value of corners and stable pieces (double counts corners as they are high value)
def check_stable_heuristic(board, color):
    score = 0
    i, j = 0, 0
    # top left - top right
    while i < len(board) and board[i][j] == color:
        score += 2
        i += 1
    # top right - top left
    if i != len(board):
        i = len(board) - 1
        while i >= 0 and board[i][j] == color:
            score += 2
            i -= 1
    i = 0
    # top left - bot left
    while j < len(board) and board[i][j] == color:
        score += 2
        j += 1
    # bot left - top left
    if j != len(board):
        # print("j and board length are:", j, len(board))
        j = len(board) - 1
        while j >= 0 and board[i][j] == color:
            score += 2
            j -= 1
    
    i, j = 0, len(board) - 1
    # bot left - bot right
    while i < len(board) and board[i][j] == color:
        score += 2
        i += 1
    # bot right - bot left
    if i != len(board):
        i = len(board) - 1
        while i >= 0 and board[i][j] == color:
            score += 2
            i -= 1
    i, j = len(board) - 1, 0
    # top right - bot right
    while j < len(board) and board[i][j] == color:
        score += 2
        j += 1
    # bot right - top right
    if j != len(board):
        j = len(board) - 1
        while j >= 0 and board[i][j] == color:
            score += 2
            j -= 1

    return score

# Calculates frontier of all non-edge pieces
def frontier_heuristic(board, color, opposite_color):
    score = 0
    length = len(board)
    for i in range(1, length-1):
        for j in range(1, length-1):
            if board[i][j] == color:
                score -= (board[i-1][j] == 0) + (board[i][j-1] == 0) +\
                         (board[i+1][j] == 0) + (board[i][j+1] == 0)
            elif board[i][j] == opposite_color:
                score += (board[i-1][j] == 0) + (board[i][j-1] == 0) +\
                         (board[i+1][j] == 0) + (board[i][j+1] == 0)

    return score


############ MINIMAX ###############################
# Caching state dictionary
s_to_val = {}

def minimax_min_node(board, color, limit, caching = 0):
    moves = []
    opposite_color = 1 if color == 2 else 2

    # Calculate utility of every move
    for move in get_possible_moves(board, opposite_color):
        new_board = play_move(board, opposite_color, move[0], move[1])

        if caching and new_board in s_to_val:
            moves.append((move, s_to_val[new_board]))
            continue

        if len(get_possible_moves(new_board, color)) == 0:
            val = compute_utility(new_board, color)
            moves.append((move, val))
            if caching:
                s_to_val[new_board] = val
        elif limit == 1:
            val = compute_utility(new_board, color)
            # val = compute_heuristic(new_board, color)
            moves.append((move, val))
            if caching:
                s_to_val[new_board] = val
        else:
            val = minimax_max_node(new_board, color, limit-1, caching)[1]
            moves.append((move, val))
            if caching:
                s_to_val[new_board] = val

    # Find minimizing move for opposite player
    min_move = moves[0]
    for move in moves:
        if move[1] < min_move[1]:
            min_move = move

    return min_move

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    moves = []

    # Calculate utility of every move
    for move in get_possible_moves(board, color):
        new_board = play_move(board, color, move[0], move[1])
        opposite_color = 1 if color == 2 else 2

        if caching and new_board in s_to_val:
            moves.append((move, s_to_val[new_board]))
        elif len(get_possible_moves(new_board, opposite_color)) == 0:
            val = compute_utility(new_board, color)
            moves.append((move, val))
            if caching:
                s_to_val[new_board] = val
        elif limit == 1:
            val = compute_utility(new_board, color)
            # val = compute_heuristic(new_board, color)
            moves.append((move, val))
            if caching:
                s_to_val[new_board] = val
        else:
            val = minimax_min_node(new_board, color, limit-1, caching)[1]
            moves.append((move, val))
            if caching:
                s_to_val[new_board] = val

    # Find maximizing move and return that
    max_move = moves[0]
    for move in moves:
        if move[1] > max_move[1]:
            max_move = move

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
    if limit > 0:
        return minimax_max_node(board, color, limit, caching)[0]
    else:
        return minimax_max_node(board, color, float("inf"), caching)[0] 


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    moves = []
    opposite_color = 1 if color == 2 else 2
    temp_beta = float("inf")

    # Calculate utility of every move
    all_moves = get_possible_moves(board, opposite_color)

    # Order search from WORST heuristic to BEST heuristic
    if ordering:
        val_move = []
        for move in all_moves:
            new_board = play_move(board, opposite_color, move[0], move[1])
            val = compute_utility(new_board, color)
            val_move.append((val, move))

        val_move = sorted(val_move)
        # val_move.reverse()
        all_moves = []

        for val, move in val_move:
            all_moves.append(move)

    for move in all_moves:
        new_board = play_move(board, opposite_color, move[0], move[1])

        if caching and new_board in s_to_val:
            moves.append((move, s_to_val[new_board]))
        elif len(get_possible_moves(new_board, color)) == 0:
            val = compute_utility(new_board, color)
            moves.append((move, val))
            if caching:
                s_to_val[new_board] = val
        elif limit == 1:
            val = compute_utility(new_board, color)
            # val = compute_heuristic(new_board, color)
            moves.append((move, val))
            if caching:
                s_to_val[new_board] = val
        else:
            val = alphabeta_max_node(new_board, color, alpha, beta, limit-1, caching, ordering)[1]
            moves.append((move, val))
            if caching:
                s_to_val[new_board] = val

        # Update beta and check if more children need to be searched
        temp_beta = min(temp_beta, moves[-1][1])
        if beta > temp_beta:
            beta = temp_beta
            if beta <= alpha:
                break

    # Find minimizing move for opposite player
    min_move = moves[0]
    for move in moves:
        if move[1] < min_move[1]:
            min_move = move

    return min_move

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    moves = []
    temp_alpha = float("-inf")

    # Calculate utility of every move
    all_moves = get_possible_moves(board, color)

    # Order search from BEST heuristic to WORST heuristic
    if ordering:
        val_move = []
        for move in all_moves:
            new_board = play_move(board, color, move[0], move[1])
            val = compute_utility(new_board, color)
            val_move.append((val, move))

        val_move = sorted(val_move)
        val_move.reverse()
        all_moves = []

        for val, move in val_move:
            all_moves.append(move)


    for move in all_moves:
        new_board = play_move(board, color, move[0], move[1])
        opposite_color = 1 if color == 2 else 2

        if caching and new_board in s_to_val:
            moves.append((move, s_to_val[new_board]))
        elif len(get_possible_moves(new_board, opposite_color)) == 0:
            val = compute_utility(new_board, color)
            moves.append((move, val))
            if caching:
                s_to_val[new_board] = val
        elif limit == 1:
            val = compute_utility(new_board, color)
            # val = compute_heuristic(new_board, color)
            moves.append((move, val))
            if caching:
                s_to_val[new_board] = val
        else:
            val = alphabeta_min_node(new_board, color, alpha, beta, limit-1, caching, ordering)[1]
            moves.append((move, val))
            if caching:
                s_to_val[new_board] = val
        
        # Update alpha and check if more children need to be searched
        temp_alpha = max(temp_alpha, moves[-1][1])
        if alpha < temp_alpha:
            alpha = temp_alpha
            if beta <= alpha:
                break

    # Find maximizing move and return that
    max_move = moves[0]
    for move in moves:
        if move[1] > max_move[1]:
            max_move = move

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
    if limit > 0:
        return alphabeta_max_node(board, color, float("-inf"), float("inf"), limit, caching, ordering)[0]
    else:
        return alphabeta_max_node(board, color, float("-inf"), float("inf"), float("inf"), caching, ordering)[0]

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
