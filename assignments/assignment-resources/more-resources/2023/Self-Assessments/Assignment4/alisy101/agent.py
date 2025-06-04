"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

dictmin = {}
dictmax = {}
dictabmin = {}
dictabmax = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    p1, p2 = get_score(board)
    if color == 1:
        return p1 - p2
    return  p2 - p1

# Better heuristic value of board
def adjacent_search(board, corner, color, c):
    #breadth first search of pieces near corners
    score = c
    visited = set()
    queue = []
    queue.append(corner)
    while queue:
        move = queue.pop(0)
        if move[0]+1 < len(board) and (move[0]+1, move[1]) not in visited and board[move[0]+1][move[1]] == color:
            score += 1
            queue.append((move[0]+1, move[1]))
            visited.add((move[0]+1, move[1]))
        if move[0]-1 > 0 and (move[0]-1, move[1]) not in visited and board[move[0]-1][move[1]] == color:
            score += 1
            queue.append((move[0]-1, move[1]))
            visited.add((move[0]-1, move[1]))
        if move[1]+1 < len(board) and (move[0], move[1] + 1) not in visited and board[move[0]][move[1]+1] == color:
            score += 1
            queue.append((move[0], move[1]+1))
            visited.add((move[0], move[1]+1))
        if move[1]-1 > 0 and (move[0], move[1] - 1) not in visited and board[move[0]][move[1]-1] == color:
            score += 1
            queue.append((move[0], move[1]-1))
            visited.add((move[0], move[1]-1))
    return score

def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT

    #You want to aim to place more pieces on walls and corners
    #thus we reward states with more pieces on walls and corners

    a=get_possible_moves(board, color)
    b=get_possible_moves(board, 3-color)
    remaining_moves = (len(board) ** 2) - (len(a) + len(b))  #remaining moves on board
    score = 0
    if remaining_moves/(len(board) ** 2) > 0.25:  #if the board is more than 1/4th empty
        #then if our limit is something small, our terminal states won't have pieces near
        #the corners. So we must use something else to compute_heuristic for this case.
        #we try to minimize opponent moves and maximize players moves
        score = compute_utility(board, color)  
        score += len(a) - len(b)

    if len(board) > 7: 
        c = 3  #just some values i got from trial and error.
    else:
        c = 5
         
    if board[0][-1] == color: #looks for clusters near the corner
        score += adjacent_search(board, (0,len(board)-1), color, c)
    if board[0][0] == color:
        score += adjacent_search(board, (0, 0), color, c)
    if board[-1][0] == color: 
        score += adjacent_search(board, (len(board)-1,0), color, c)
    if board[-1][-1] == color:
        score += adjacent_search(board, (len(board)-1,len(board)-1), color, c)

    if board[0][-1] == 3-color: #looks for clusters near the corner (for enemy)
        score -= adjacent_search(board, (0,len(board)-1), 3-color, c)
    if board[0][0] == 3-color:
        score -= adjacent_search(board, (0, 0), 3-color, c)
    if board[-1][0] == 3-color: 
        score -= adjacent_search(board, (len(board)-1,0), 3-color, c)
    if board[-1][-1] == 3-color:
        score -= adjacent_search(board, (len(board)-1,len(board)-1), 3-color, c)
    return score

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)
    hkey = (str(board), color)
    if caching:
        if hkey in dictmin:
            return dictmin[hkey]
    score = ((-1, -1), float('inf'))
    if color == 1:
        nextp = 2
    else:
        nextp = 1
    results = get_possible_moves(board, nextp)
    if not results or not limit:
        return (score[0], compute_utility(board, color))
    for move in results:
        nextboard = play_move(board, nextp, move[0], move[1])
        newscore = minimax_max_node(nextboard, color, limit-1, caching)
        if newscore[1] < score[1]:
            score = (move, newscore[1])
    dictmin[hkey] = score 
    return score

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    hkey = (str(board), color)
    if caching:
        if hkey in dictmax:
            return dictmax[hkey]
    results = get_possible_moves(board, color)
    score = ((-1, -1), float('-inf'))
    if not results or not limit:
        return (score[0], compute_utility(board, color))
    for move in results:
        nextboard = play_move(board, color, move[0], move[1])
        newscore = minimax_min_node(nextboard, color, limit-1, caching)
        if newscore[1] > score[1]:
            score = (move, newscore[1]) 
    dictmax[hkey] = score
    return score

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
    #IMPLEMENT (and replace the line below)
    hkey = (str(board), color)
    if caching:
        if hkey in dictabmin:
            return dictabmin[hkey]
    beta1 = ((-1, -1), beta)
    if color == 1:
        nextp = 2
    else:
        nextp = 1
    results = get_possible_moves(board, nextp)
    if not results or not limit:
        return (beta1[0], compute_utility(board, color))
    movedic = {}
    for move in results:
        movedic[move] = play_move(board, nextp, move[0], move[1])
    if ordering:
        
        results.sort(key=lambda x:compute_utility(movedic[x], color), reverse=False)
    for move in results:
        nextboard = movedic[move]
        newscore = alphabeta_max_node(nextboard, color, alpha, beta1[1], limit-1, caching, ordering)
        if newscore[1] < beta1[1]:
            beta1 = (move, newscore[1])

        if beta1[1] <= alpha:
            break
    dictabmin[hkey] = beta1
    return beta1

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    hkey = (str(board), color)
    if caching:
        if hkey in dictabmax:
            return dictabmax[hkey]
    results = get_possible_moves(board, color)
    alpha1 = ((-1, -1), alpha)
    
    if not results or not limit:
        return (alpha1[0], compute_utility(board, color))
    movedic = {}
    for move in results:
        movedic[move] = play_move(board, color, move[0], move[1])
    if ordering:
        results.sort(key=lambda x:compute_utility(movedic[x], color), reverse=True)

    for move in results:
        nextboard = movedic[move]
        newscore = alphabeta_min_node(nextboard, color, alpha1[1], beta, limit-1, caching, ordering)
        if newscore[1] > alpha1[1]:
            alpha1 = (move, newscore[1])

        if beta <= alpha1[1]:
            break
    dictabmax[hkey] = alpha1
    return alpha1

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
