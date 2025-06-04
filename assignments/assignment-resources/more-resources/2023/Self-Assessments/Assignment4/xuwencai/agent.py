
# For my heuristic, I implement the board locations where pieces are stable, i.e. where they cannot be flipped anymore.
# In the board, discs in the corner can not be flipped any more. So if a corner contains a disc, then it means the player
# has some advantage, we need to add some heuristic score. Also, I consider  number of moves you and your opponent 
# can make given the current board configuration. If number of moves is greater than your opponent, then it means you have
# more choices, which should add some scores


"""
An AI player for Othello. 
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
    result = get_score(board)
    if color == 1:
        return result[0] - result[1]
    return result[1] - result[0]


# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #  board locations where pieces are stable, i.e. where they cannot be flipped anymore.
    Score = 0
    row = len(board) - 1
    column = len(board)[0] - 1
    if board[0][0] == color:
        Score += 100
    if board[0][column] == color:
        Score += 100
    if board[row][0] == color:
        Score += 100
    if board[row][column] == color:
        Score += 100
    
    # Consider the number of moves you and your opponent can make given the current board configuration.
    moves = get_possible_moves(board, color)
    moves2 = get_possible_moves(board, getOpponent(color))

    Score += (len(moves) - len(moves2)) * 10

    Score += compute_utility(board, color)

    return Score



def getOpponent(color):
    if color == 1:
        return 2
    return 1

caches = {}

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    if caching == 1:
        if board in caches:
            return caches[board]
    moves = get_possible_moves(board, getOpponent(color))
   
    if limit == 0 or len(moves) == 0:
        return None, compute_utility(board, color)
    
    Min, worst_move = float('inf'), moves[0]
    for move in moves:
        new_board = play_move(board, getOpponent(color), move[0], move[1])
        score = minimax_max_node(new_board, color, limit - 1, caching)[1]
        if score < Min:
            Min, worst_move = score, move
        if caching == 1:
            caches[new_board] = (move, score)

    return worst_move, Min 


def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    if caching == 1:
        if board in caches:
            return caches[board]
    moves = get_possible_moves(board, color)

    if limit == 0 or len(moves) == 0:
        return None, compute_utility(board, color)
    
    Max, best_move = float('-inf'), moves[0]
    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        score = minimax_min_node(new_board, color, limit - 1, caching)[1]
        if score > Max:
            Max, best_move = score, move
        if caching == 1:
            caches[new_board] = (move, score)

    return best_move, Max


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
    caches.clear()
    return minimax_max_node(board, color, limit, caching)[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):

    if caching == 1:
        if board in caches:
            return caches[board]
    moves = get_possible_moves(board, getOpponent(color)) 

    if limit == 0 or len(moves) == 0:
        return None, compute_utility(board, color)
    
    Min, worst_move = float('inf'), moves[0]
    for move in moves:
        new_board = play_move(board, getOpponent(color), move[0], move[1])
        score =alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
        if score < Min:
            Min, worst_move = score, move
        if caching == 1:
            caches[new_board] = (move, score)
        beta = min(beta, score)
        if alpha >= beta:
            break
    return worst_move, Min 


def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching == 1:
        if board in caches:
            return caches[board]
    moves = get_possible_moves(board, color)

    if limit == 0 or len(moves) == 0:
        return None, compute_utility(board, color)

    if ordering == 1:
        sorted_moves = []
        d = {}
        for move in moves:
            temp_board = play_move(board, color, move[0], move[1])
            score = compute_utility(temp_board, color)
            if not d.get(score):
                d[score] = set()
                d[score].add(move)
            else:
                d[score].add(move)
        sort_score = sorted(list(d.keys()), reverse=True)
        for score in sort_score:
            sorted_moves.extend(d[score])
        
        moves[:] = sorted_moves
 
        
        

            
 

    Max, best_move = float('-inf'), moves[0]
    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        score = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
        if score > Max:
            Max, best_move = score, move
        if caching == 1:
            caches[new_board] = (move, score)
        alpha = max(alpha, score)
        if alpha >= beta:
            break

    return best_move, Max


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
    caches.clear()
    return alphabeta_max_node(board, color, float("-inf"), float("inf"), limit, caching, ordering)[0]


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
