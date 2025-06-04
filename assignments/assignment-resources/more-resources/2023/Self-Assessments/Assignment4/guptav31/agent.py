"""
An AI player for Othello. 

 The heuristic assigns high values to the corner pieces if color can take them in the next move.
 This is balanced with the possibility of other_color taking the corner in the next move using a weight.
 Moreove, we assign high values to the three squares adjacent to each corner if other_color can take them,
 since those moves nearly guarantee that color can take the corner spots. This is from the strategy
 where taking a corner allows you to start building a bunch of unflippable pieces.
 The heuristic also favors color having more possible moves, or more freedom, than other_color, since limiting the other
 player's options is also a helpful strategy.
 Finally, the heuristic is only run for the first 2/3 of the game, by which time, color has usually already grabbed the corners.
 Since the number of possible moves starts to increase dramatically as the game goes on, we switch to just compute_utility to lower
 the cost of running the heuristic. Plus, if the game is already 2/3 done, we are much closer to terminal states, so the compute_utility
 function becomes quite useful. 

"""

from cmath import inf
import random
import sys
import time
from turtle import update

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    

state_cache = {}

def update_state_cache(board, utility):
    state_cache[board] = utility


# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    dark_discs, light_discs = get_score(board)
    if color == 1:
        return dark_discs - light_discs
    elif color == 2:
        return light_discs - dark_discs

    #return 0 #change this!

# Better heuristic value of board
# The heuristic assigns high values to the corner pieces if color can take them in the next move.
# This is balanced with the possibility of other_color taking the corner in the next move using a weight.
# Moreove, we assign high values to the three squares adjacent to each corner if other_color can take them,
# since those moves nearly guarantee that color can take the corner spots. This is from the strategy
# where taking a corner allows you to start building a bunch of unflippable pieces.
# The heuristic also favors color having more possible moves, or more freedom, than other_color, since limiting the other
# player's options is also a helpful strategy.
# Finally, the heuristic is only run for the first 2/3 of the game, by which time, color has usually already grabbed the corners.
# Since the number of possible moves starts to increase dramatically as the game goes on, we switch to just compute_utility to lower
# the cost of running the heuristic. Plus, if the game is already 2/3 done, we are much closer to terminal states, so the compute_utility
# function becomes quite useful. 
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT

    if color == 1:
        other_color = 2
    else:
        other_color = 1

    max_heuristic = 0
    min_heuristic = 0
    dimension = len(board)
    area = dimension*dimension
    corners = [(0, 0), (0, dimension - 1), (dimension - 1, 0), (dimension - 1, dimension - 1)]
    dangers = [(0,1), (1,0), (0, dimension-2), (1, dimension -1), (dimension-2, 0), (dimension -1, 1), (dimension - 1, dimension - 2), (dimension - 2, dimension - 1)]
    mega_dangers = [(1,1), (dimension - 2, 1),(1, dimension-2), (dimension - 2, dimension-2)]
    
    poss_moves_max = get_possible_moves(board, color)
    num_max_moves = len(poss_moves_max)
    poss_moves_min = get_possible_moves(board, other_color)
    num_min_moves = len(poss_moves_min)
    max_corners = 0
    min_corners = 0

    light, dark = get_score(board)
    if num_max_moves+num_min_moves == 0 or (light + dark > (2*area)//3):
        return compute_utility(board, color)
    else:
        freedom = (num_max_moves - num_min_moves) / (num_max_moves + num_min_moves)
        for corner in corners:
            if corner in poss_moves_max:
                max_corners += 1
            elif corner in poss_moves_min:
                min_corners += 1
        corner_weight = (max_corners - min_corners) / (4)
        for danger in dangers:
            if danger in poss_moves_min:
                min_heuristic += 3
        for mega_danger in mega_dangers:
            if mega_danger in poss_moves_min:
                min_heuristic += 5
        
        if freedom != 0 and corner_weight != 0:
            if (freedom < 0 and corner_weight > 0) or (corner_weight < 0 and freedom > 0):
                return (area+min_heuristic)*freedom*corner_weight
            else:
                return (area+min_heuristic)*freedom*corner_weight*-1

        

        #OTHER HEURISTICS I TRIED, BUT WERE TOO COSTLY
        #for move in poss_moves_max:
        #    if move in corners:
        #        max_heuristic += 5
        #    elif move in dangers:
        #        max_heuristic += -3
        #    elif move in mega_dangers:
        #        max_heuristic += -10
        #    max_heuristic += len(find_lines(board, move[0], move[1], color))

        #if freedom != 0:
        #    max_heuristic = freedom * max_heuristic
        #for move in poss_moves_min:
        #    if move in corners:
        #        min_heuristic += 5
        #    elif move in dangers:
        #        min_heuristic += -3
        #    elif move in mega_dangers:
        #        min_heuristic += -10
        #    min_heuristic += len(find_lines(board, move[0], move[1], color))

    return compute_utility(board, color)#change this!

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)
    
    if color == 1:
        other_color = 2
    else:
        other_color = 1

    min_utility = inf
    worst_move = None
    poss_moves = get_possible_moves(board, other_color)
    
    #print("poss_moves min node: ", poss_moves)
    if len(poss_moves) == 0 or limit == 0: #No moves are possible, the game is over
        return (None, compute_utility(board, color))
    else:
        for move in poss_moves:
            
            curr_board = play_move(board, other_color, move[0], move[1])
            if caching == 1 and curr_board not in state_cache.keys():
                opp_move, curr_utility = minimax_max_node(curr_board, color, limit-1, caching)
                update_state_cache(curr_board, curr_utility)
            elif caching == 1:
                curr_utility = state_cache[curr_board]   
            else:
                opp_move, curr_utility = minimax_max_node(curr_board, color, limit-1, caching)
            
            if curr_utility < min_utility:
                min_utility = curr_utility
                worst_move = move
            
        return(worst_move, min_utility)

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    max_utility = -inf
    best_move = None
    poss_moves = get_possible_moves(board, color)
    #if limit == 5:
    #    print("poss moves: ", poss_moves)

    if color == 1:
        other_color = 2
    else:
        other_color = 1
    
    #print("poss_moves max node: ", poss_moves)
    if len(poss_moves) == 0 or limit == 0: #No moves are possible, the game is over
        return (None, compute_utility(board, color))
    else:
        for move in poss_moves:
            
            curr_board = play_move(board, color, move[0], move[1])
            if caching == 1 and curr_board not in state_cache.keys():
                opp_move, curr_utility = minimax_min_node(curr_board, color, limit-1, caching)
                update_state_cache(curr_board, curr_utility) 
            elif caching == 1:
                curr_utility = state_cache[curr_board]
            else:
                opp_move, curr_utility = minimax_min_node(curr_board, color, limit-1, caching)
            #if limit == 1:
            #    print("move: ", move, " curr_utility: ", curr_utility)
            if curr_utility > max_utility:
                max_utility = curr_utility
                best_move = move
        
        return(best_move, max_utility)
    

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
    move, utility = minimax_max_node(board, color, limit-1, caching)
   
    #print("move: ", move)
    return move #change this!

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    if color == 1:
        other_color = 2
    else:
        other_color = 1

    min_utility = inf
    worst_move = None
    poss_moves = get_possible_moves(board, other_color)
    child_boards = []
    
    #print("poss_moves min node: ", poss_moves)
    if len(poss_moves) == 0 or limit == 0: #No moves are possible, the game is over
        return (None, compute_utility(board, color))
    else:
        if ordering == 0:
            for move in poss_moves:
                
                curr_board = play_move(board, other_color, move[0], move[1])
                if caching == 1 and curr_board not in state_cache.keys():
                    opp_move, curr_utility = alphabeta_max_node(curr_board, color, alpha, beta, limit-1, caching, ordering)
                    update_state_cache(curr_board, curr_utility)
                elif caching == 1:
                    curr_utility = state_cache[curr_board]
                else:
                    opp_move, curr_utility = alphabeta_max_node(curr_board, color, alpha, beta, limit-1, caching, ordering)
                if curr_utility < min_utility:
                    min_utility = curr_utility
                    worst_move = move
                    beta = min(beta, min_utility)
                    if beta <= alpha:
                        break
        else:
            best_utility = -inf
            for move in poss_moves:
                child = play_move(board, other_color, move[0], move[1])
                child_boards.append((move, child))
            sorted_child_boards = sort_board(child_boards, color)
            for pair in sorted_child_boards:
                if caching == 1 and pair[1] not in state_cache.keys():
                    opp_move, curr_utility = alphabeta_max_node(pair[1], color, alpha, beta, limit-1, caching, ordering)
                    update_state_cache(pair[1], curr_utility)
                elif caching == 1:
                    curr_utility = state_cache[pair[1]]
                else:
                    opp_move, curr_utility = alphabeta_max_node(pair[1], color, alpha, beta, limit-1, caching, ordering)
                
                if curr_utility < min_utility:
                    min_utility = curr_utility
                    worst_move = pair[0]
                    beta = min(beta, min_utility)
                    if beta <= alpha:
                        break

        return(worst_move, min_utility)


def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    max_utility = -inf
    best_move = None
    poss_moves = get_possible_moves(board, color)
    child_boards = []


    #print("poss_moves max node: ", poss_moves)
    if len(poss_moves) == 0 or limit == 0: #No moves are possible, the game is over
        return (None, compute_utility(board, color))
    
    else:
        
        if ordering == 0:
            for move in poss_moves:
                
                curr_board = play_move(board, color, move[0], move[1])
                if caching == 1 and curr_board not in state_cache.keys():
                    opp_move, curr_utility = alphabeta_min_node(curr_board, color, alpha, beta, limit-1, caching, ordering)
                    update_state_cache(curr_board, curr_utility)
                elif caching == 1:
                    curr_utility = state_cache[curr_board]
                else:
                    opp_move, curr_utility = alphabeta_min_node(curr_board, color, alpha, beta, limit-1, caching, ordering)
                if curr_utility > max_utility:
                    max_utility = curr_utility
                    best_move = move
                    alpha = max(alpha, max_utility)
                    if beta <= alpha:
                        break
        else:
            best_utility = -inf
            for move in poss_moves:
                child = play_move(board, color, move[0], move[1])
                child_boards.append((move, child))
            sorted_child_boards = sort_board(child_boards, color)
            for pair in sorted_child_boards:
                if caching == 1 and pair[1] not in state_cache.keys():
                    opp_move, curr_utility = alphabeta_min_node(pair[1], color, alpha, beta, limit-1, caching, ordering)
                    update_state_cache(pair[1], curr_utility)
                elif caching == 1:
                    curr_utility = state_cache[pair[1]]
                else:
                    opp_move, curr_utility = alphabeta_min_node(pair[1], color, alpha, beta, limit-1, caching, ordering)
                
                if curr_utility > max_utility:
                    max_utility = curr_utility
                    best_move = pair[0]
                    alpha = max(alpha, max_utility)
                    if beta <= alpha:
                        break

        return(best_move, max_utility)


#Quicksort algorithm for making a sorted list of boards
def sort_board(child_boards, color):
    
    
    if len(child_boards) <= 1:
        return child_boards
    else:
        pivot = len(child_boards)//2
        pivot_utility = compute_utility(child_boards[pivot][1], color)
        right_array = []
        left_array = []
        for pair in child_boards:
            if pair != child_boards[pivot]:
                utility = compute_utility(pair[1], color)
                if utility > pivot_utility:
                    left_array.append(pair)
                else:
                    right_array.append(pair)
    return sort_board(left_array, color) + [child_boards[pivot]] + sort_board(right_array, color)


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
    alpha = -inf
    beta = inf

    
    move, utility = alphabeta_max_node(board, color, alpha, beta, limit-1, caching, ordering)
    

    return move

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
