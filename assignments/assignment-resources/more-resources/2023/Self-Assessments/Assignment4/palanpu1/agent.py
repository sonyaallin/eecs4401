"""
An AI player for Othello. 
"""

import random
import sys
import time

cache = {}

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    darkDisks, lightDisks = get_score(board)
    if color == 1:
        return darkDisks - lightDisks
    return lightDisks - darkDisks


# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    return 0 #change this!


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)

    if caching:
        if (board, color, limit) in cache:
            return cache[(board, color, limit)]

    if color == 1:
        otherColor = 2
    elif color == 2:
        otherColor = 1

    b = float("inf")

    best = None
    possMoves = get_possible_moves(board, otherColor)
    if len(possMoves) == 0:
        b = compute_utility(board, color)
    if limit == 0:
        b = compute_utility(board, color)
        bestpair = (best, b)
        return bestpair

    for i in range(len(possMoves)):
        curMove = possMoves[i]
        movedBoard = play_move(board, otherColor, curMove[0], curMove[1])
        moveData = minimax_max_node(movedBoard, color, limit-1)

        stateUtil = moveData[1]

        if stateUtil < b:
            best = curMove
            b = stateUtil

    bestpair = (best, b)
    if caching:
        cache[(board, color, limit)] = bestpair
    return bestpair


def minimax_max_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below

    #Almost same as minimax min node
    if caching:
        if (board, color) in cache:
            return cache[(board, color, limit)]

    if color == 1:
        otherColor = 2
    elif color == 2:
        otherColor = 1


    b = -float("inf")

    best = None
    possMoves = get_possible_moves(board, color)
    if len(possMoves) == 0:
        b = compute_utility(board, color)
    if limit == 0:
        b = compute_utility(board, color)
        bestpair = (best, b)
        return bestpair

    for i in range(len(possMoves)):
        curMove = possMoves[i]
        movedBoard = play_move(board, color, curMove[0], curMove[1])
        moveData = minimax_min_node(movedBoard, color, limit - 1)
        stateUtil = moveData[1]

        if stateUtil > b:
            best = curMove
            b = stateUtil

    bestpair = (best, b)
    if caching:
        cache[(board, color, limit)] = bestpair
    return bestpair


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

    possMoves = get_possible_moves(board, color)
    noNext = compute_utility(board, color)
    if len(possMoves) == 0:
        return noNext
    if limit == 0:
        return noNext
    bestpair = minimax_max_node(board, color, limit, caching)
    chosen = bestpair[0]
    return chosen


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)

    if caching:
        if (board, color, alpha, beta, limit) in cache:
            return cache[(board, color, alpha, beta, limit)]

    if color == 1:
        otherColor = 2
    elif color == 2:
        otherColor = 1

    abParam = float("inf")

    best = None
    possMoves = get_possible_moves(board, otherColor)
    if len(possMoves) == 0:
        abParam = compute_utility(board, color)
        bestpair = (best, abParam)
        return bestpair
    if limit == 0:
        abParam = compute_utility(board, color)
        bestpair = (best, abParam)
        return bestpair

    possMovesWithUtils = []
    for move in possMoves:
        resultingBoard = play_move(board, otherColor, move[0], move[1])
        resultingUtil = compute_utility(resultingBoard, color)
        possMovesWithUtils.append((resultingUtil, move, resultingBoard))
    if ordering:
        # make tuples with (utility value, state) and then we can order
        possMovesWithUtils.sort()

    for i in range(len(possMovesWithUtils)):

        if beta <= alpha:
            break

        if abParam <= alpha:
            pair = (best, abParam)
            return pair

        checkMove = possMovesWithUtils[i][1]
        checkBoard = possMovesWithUtils[i][2]

        moveData = alphabeta_max_node(checkBoard, color, alpha, beta, limit-1)
        resultMove = moveData[0]
        resultUtil = moveData[1]

        if resultUtil < abParam:
            abParam = resultUtil
            best = checkMove

        if abParam < beta:
            beta = abParam


    bestpair = (best, abParam)
    if caching:
        cache[(board, color, alpha, beta, limit)] = bestpair
    return bestpair



def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):


    #IMPLEMENT (and replace the line below)

    if caching:
        if (board, color, alpha, beta, limit) in cache:
            return cache[(board, color, alpha, beta, limit)]

    if color == 1:
        otherColor = 2
    elif color == 2:
        otherColor = 1

    abParam = -float("inf")

    best = None

    possMoves = get_possible_moves(board, color)

    if len(possMoves) == 0:
        abParam = compute_utility(board, color)
        bestpair = (best, abParam)
        return bestpair
    if limit == 0:
        abParam = compute_utility(board, color)
        bestpair = (best, abParam)
        return bestpair

    possMovesWithUtils = []
    for move in possMoves:
        resultingBoard = play_move(board, color, move[0], move[1])
        resultingUtil = compute_utility(resultingBoard, color)
        possMovesWithUtils.append((resultingUtil, move, resultingBoard))
    if ordering:
        # make tuples with (utility value, state) and then we can order
        possMovesWithUtils.sort(reverse=True)

    for i in range(len(possMovesWithUtils)):

        if beta <= alpha:
            break

        if abParam >= beta:
            pair = (best, abParam)
            return pair

        checkMove = possMovesWithUtils[i][1]
        checkBoard = possMovesWithUtils[i][2]

        moveData = alphabeta_min_node(checkBoard, color, alpha, beta, limit - 1)
        resultMove = moveData[0]
        resultUtil = moveData[1]

        if resultUtil > abParam:
            abParam = resultUtil
            best = checkMove

        if abParam > alpha:
            alpha = abParam

    bestpair = (best, abParam)
    if caching:
        cache[(board, color, alpha, beta, limit)] = bestpair
    return bestpair


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

    possMoves = get_possible_moves(board, color)
    noNext = compute_utility(board, color)

    best = None

    if len(possMoves) == 0:
        best = noNext
    if limit == 0:
        best = noNext
        return best

    aParam = -float("inf")
    bParam = float("inf")

    for curMove in possMoves:
        moveRes = play_move(board, color, curMove[0], curMove[1])
        moveData = alphabeta_min_node(moveRes, color, aParam, bParam, limit - 1, caching, ordering)
        resMove = moveData[0]
        resultingUtil = moveData[1]
        if aParam < resultingUtil:
            aParam = resultingUtil
            best = curMove


    return best


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
