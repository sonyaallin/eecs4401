"""
An AI player for Othello.
"""
"""
DESCRIPTION OF HEURISTIC:
I know from a previous assignment (from 209 I think?) that the optimal locations to be are in the
corners in Othello so I added extra weight to those squares. It was also such that taking the option that gives you
the most moves is also good to take, so I added weight to the amount of moves a move leaves you with (didn't consider
the opponents move but I'm tired so I'm done.
"""


import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

STATE_DICTIONARY = {}

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
    score = get_score(board)
    if color == 1:
        heur = score[0] - score[1]
    else:
        heur =  score[1] - score[0]
    if color == 1:
        moves = get_possible_moves(board, 2)
    else:
        moves = get_possible_moves(board, 1)
    heur -= len(moves)
    if board[0][0] == color:
        heur += 10
    if board[0][len(board)-1] == color:
        heur += 10
    if board[len(board)-1][0] == color:
        heur += 10
    if board[len(board)-1][len(board)-1] == color:
        heur += 10
    return heur

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    if limit == 0:
        return "Leaf", compute_utility(board, color)
    if color == 1:
        opp_color = 2
    else:
        opp_color = 1
    moves = get_possible_moves(board, opp_color)
    if not moves:
        return "Leaf", compute_utility(board, color)
    min_val = float("inf")
    minmove = None
    for move in moves:
        new = play_move(board, opp_color, move[0], move[1])
        converted = tuple(map(tuple, new))
        if caching == 0 or converted not in STATE_DICTIONARY:
            util = minimax_max_node(new, color, limit - 1, caching)[1]
        else:
            util = STATE_DICTIONARY[converted]
        if caching == 0:
            STATE_DICTIONARY[converted] = util
        if util < min_val:
            min_val = util
            minmove = move
    return minmove, min_val

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    if limit == 0:
        return "Leaf", compute_utility(board, color)
    moves = get_possible_moves(board, color)
    if not moves:
        return "Leaf", compute_utility(board, color)
    max_val = float("-inf")
    maxmove = None
    for move in moves:
        new = play_move(board, color, move[0], move[1])
        converted = tuple(map(tuple, new))
        if caching == 0 or converted not in STATE_DICTIONARY:
            util = minimax_min_node(new, color, limit - 1, caching)[1]
        else:
            util = STATE_DICTIONARY[converted]
        if caching == 1:
            STATE_DICTIONARY[converted] = util
        if util > max_val:
            max_val = util
            maxmove = move
    return maxmove, max_val

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
    if color == 1:
        opp_color = 2
    else:
        opp_color = 1
    if limit == 0:
        return "Leaf", compute_utility(board, color)
    moves = get_possible_moves(board, opp_color)
    boards = list(map(lambda x: play_move(board, opp_color, x[0], x[1]), moves))
    if not moves:
        return "Leaf", compute_utility(board, color)
    if ordering == 1:
        order_moves(moves, boards, color, opp_color)
    min_val = float("inf")
    minmove = None
    for i in range(len(moves)):
        if caching == 0 or boards[i] not in STATE_DICTIONARY:
            util = alphabeta_max_node(boards[i], color, alpha, beta, limit - 1, caching, ordering)[1]
        else:
            util = STATE_DICTIONARY[boards[i]]
        if caching == 1:
            STATE_DICTIONARY[boards[i]] = util
        beta = min(beta, min_val)
        if alpha >= beta:
            break;
        if util < min_val:
            min_val = util
            minmove = moves[i]
    return minmove, min_val


def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if limit == 0:
        return "Leaf", compute_utility(board, color)
    moves = get_possible_moves(board, color)
    boards = list(map(lambda x: play_move(board, color, x[0], x[1]), moves))
    if not moves:
        return "Leaf", compute_utility(board, color)
    if ordering == 1:
        moves = order_moves(moves, boards, color, color)
    max_val = float("-inf")
    maxmove = None
    for i in range(len(moves)):
        #new = play_move(board, color, move[0], move[1])
        if caching == 0 or boards[i] not in STATE_DICTIONARY:
            util = alphabeta_min_node(boards[i], color, alpha, beta, limit - 1, caching, ordering)[1]
        else:
            util = STATE_DICTIONARY[boards[i]]
        if caching == 1:
            STATE_DICTIONARY[boards[i]] = util
        alpha = max(alpha, max_val)
        if beta <= alpha:
            break;
        if util > max_val:
            max_val = util
            maxmove = moves[i]
    return maxmove, max_val

def order_moves(moves, boards, aicolor, turncolor):
    #how does this not work i have no idea
    dic = {}
    for i in range(len(boards)):
        value = compute_utility(boards[i], aicolor)
        dic[moves[i]] = value
    if turncolor == aicolor:
        return list(dict(sorted(dic.items(), key=lambda item: item[1], reverse=True)).keys())
    else:
        return list(dict(sorted(dic.items(), key=lambda item: item[1])).keys())

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
