"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move
caching_dict = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    # call get score to get number of discs of each color
    disk = get_score(board)
    # get difference between number of discs for color and for the opponent
    if color == 1:
        return disk[0] - disk[1]
    else:
        return disk[1] - disk[0]

# Better heuristic value of board
def compute_heuristic(board, color):
    # Explanation of heuristic:
    # This heuristic calls the compute_utility function to get the utility of the final game board, then it performs
    # several checks involving the mobility of the player and the position of the pieces in order to build upon the
    # utility value to get a value for the current (board, color) pair. We consider the mobility(current number of
    # moves that the current color and the opponent can make). As having a larger selection of moves is more important
    # in Othello than having a greater number of current discs(as this increases chances of winning). We compute mobility 
    # by taking the number of moves that the current player(color) can make, minus the number of moves the opponent(opp_color) 
    # can make. Next we check the corner pieces. These pieces are very important as they will always remain stable once
    # obtained and typically increases chances of winning as it becomes far easier to obtain other stable pieces(such as 
    # edge pieces). We put a weight of 10000 on the corner pieces as they are extremely valuable. Next we check the C and X 
    # squares, which are the squares directly surrounding the corner pieces. These pieces are very important as we do not 
    # want to occupy these pieces without having its corresponding corner piece, as this can lead to giving up the corner 
    # square to the opponent. Thus we apply a penalty for occupying this square when we do not occupy its corner. And we 
    # apply a reward for occupying these pieces when we are occupying the corresponding corner. This is given a weight of 
    # 150 as it is not nearly as important as the corner piece(may want to occupy these squares without the corner is certain
    # cases). Finally we check the edge squares. The edge squares can also be highly valuable as they can be used to get 
    # several inner squares. We similarily check these squares and apply a reward for every edge square being occupied. 
    # This is given a weight of 50(not as valuable as corners, C squares or X squares). By taking the sum of all these 
    # rewards and deductions, we get the final value of the (board, color) pair.
    n = len(board)
    opp_color = 2 if color == 1 else 1
    # get previous utility
    utility_val = compute_utility(board, color)

    # check mobility 
    utility_val += (len(get_possible_moves(board, color)) - len(get_possible_moves(board, opp_color)))

    # check corners
    top_left = board[0][0] == color
    top_right = board[0][-1] == color
    bottom_left = board[-1][0] == color
    bottom_right = board[-1][-1] == color
    # given weight of 10000 due to high value
    utility_val += 10000*(top_left + top_right + bottom_left + bottom_right)

    # check for c squares and x squares(weight of 150)
    adjacent_top_left = 150*((board[0][1] == color) + (board[2][0] == color) + (board[2][1] == color))
    adjacent_top_right = 150*((board[0][-2] == color) + (board[2][-1] == color) + (board[2][-2] == color))
    adjacent_bottom_left = 150*((board[-1][1] == color) + (board[-2][0] == color) + (board[-2][1] == color))
    adjacent_bottom_right = 150*((board[-1][-2] == color) + (board[-2][-1] == color) + (board[-2][-2] == color))
    
    # add or deduct value for C and X squares depending on whether corner is occupied or not
    utility_val = utility_val - adjacent_top_left if not top_left else utility_val + adjacent_top_left
    utility_val = utility_val - adjacent_top_right if not top_right else utility_val + adjacent_top_right
    utility_val = utility_val - adjacent_bottom_left if not bottom_left else utility_val + adjacent_bottom_left
    utility_val = utility_val - adjacent_bottom_right if not bottom_right else utility_val + adjacent_bottom_right

    # check edges(by loop through all edges and summing values with weight of 50)
    for index in range(2, n-2):
        utility_val += 50*(board[0][index] == color)
        utility_val += 50*(board[index][0] == color)
        utility_val += 50*(board[index][-1] == color)
        utility_val += 50*(board[-1][index] == color)

    return utility_val


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    opp_color = 2 if color == 1 else 1

    # if we have seen this board and we are caching, return the stored value
    if caching and (board, color) in caching_dict:
        return caching_dict[(board, color)]

    # get possible moves, if there are none or we have reached depth limit, call 
    # and return the heuristic
    moves = get_possible_moves(board, opp_color)
    if moves == [] or limit == 0:
        final_result = (None,compute_utility(board, color))
        return final_result

    # loop through all moves and recurse to find path that leads to the minimum heuristic
    # value, choose the move that leads to that path
    final_result = ((0,0),float('inf'))
    for move in moves:
        # get board after making this move
        new_board = play_move(board, opp_color, move[0], move[1])
        # recurse upon the new board and get the result
        branch_result = minimax_max_node(new_board, color, limit-1, caching)
        # check to get minimum value
        if branch_result[1] < final_result[1]:
            final_result = (move, branch_result[1])

    # if we are caching, store the final value
    if caching:
        caching_dict[(board, color)] = final_result
    return final_result

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    # if we have seen this board and we are caching, return the stored value
    if caching and (board, color) in caching_dict:
        return caching_dict[(board, color)]

    # get possible moves, if there are none or we have reached depth limit, call 
    # and return the heuristic
    moves = get_possible_moves(board, color)
    if moves == [] or limit == 0:
        final_result = (None,compute_utility(board, color))
        return final_result

    # loop through all moves and recurse to find path that leads to the maximum heuristic
    # value, choose the move that leads to that path
    final_result = ((0,0),float('-inf'))
    for move in moves:
        # get board after making this move
        new_board = play_move(board, color, move[0], move[1])
        # recurse upon the new board and get the result
        branch_result = minimax_min_node(new_board, color, limit-1, caching)
        # check to get maximum value
        if branch_result[1] > final_result[1]:
            final_result = (move, branch_result[1])
    
    # if we are caching, store the final value
    if caching:
        caching_dict[(board, color)] = final_result
    return final_result

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
    # call the max node function as we want the best move(highest heuristic value)
    return minimax_max_node(board, color, limit, caching)[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    opp_color = 2 if color == 1 else 1

    # if we have seen this board and we are caching, return the stored value
    if caching and (board, color) in caching_dict:
        return caching_dict[(board, color)]

    # get possible moves, if there are none or we have reached depth limit, call 
    # and return the heuristic
    moves = get_possible_moves(board, opp_color)
    if moves == [] or limit == 0:
        final_result = ((0,0),compute_utility(board, color))
        return final_result
    
    final_result = ((0,0),float('inf'))

    # loop through all moves and call the play_move function to get all (move, board) tuples
    boards = []
    for move in moves:
        boards.append((move, play_move(board, opp_color, move[0], move[1])))

    # if we are node ordering, sort the (move, board) tuples by the (board,color) heuristic value 
    if ordering:
        boards.sort(key= lambda x: compute_utility(x[1], color))

    # loop through all (move, board) tuples and recurse to find path that leads 
    # to the minimum heuristic value, choose the move that leads to that path
    for new_board in boards:
        # recurse upon the current board
        branch_result = alphabeta_max_node(new_board[1], color, alpha, beta, limit-1, caching, ordering)
        # check to get minimum value
        if branch_result[1] < final_result[1]:
            final_result = (new_board[0], branch_result[1])
        # break if beta is less than or equal to alpha
        if branch_result[1] < beta:
            beta = branch_result[1]
            if beta <= alpha:
                break

    # if we are caching, store the final value
    if caching:
        caching_dict[(board, color)] = final_result
    return final_result

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # if we have seen this board and we are caching, return the stored value
    if caching and (board, color) in caching_dict:
        return caching_dict[(board, color)]

    # get possible moves, if there are none or we have reached depth limit, call 
    # and return the heuristic
    moves = get_possible_moves(board, color)
    if moves == [] or limit == 0:
        final_result = ((0,0),compute_utility(board, color))
        return final_result
    
    final_result = ((0,0),float('-inf'))
    
    # loop through all moves and call the play_move function to get all (move, board) tuples
    boards = []
    for move in moves:
        boards.append((move, play_move(board, color, move[0], move[1])))
    
    # if we are node ordering, sort the (move, board) tuples by the (board,color) heuristic value 
    if ordering:
        boards.sort(reverse=True, key = lambda x: compute_utility(x[1], color))

    # loop through all (move, board) tuples and recurse to find path that leads 
    # to the minimum heuristic value, choose the move that leads to that path
    for new_board in boards:
        # recurse upon the current board
        branch_result = alphabeta_min_node(new_board[1], color, alpha, beta, limit-1, caching, ordering)
        # check to get maximum value
        if branch_result[1] > final_result[1]:
            final_result = (new_board[0], branch_result[1])
        # break if beta is less than or equal to alpha
        if branch_result[1] > alpha:
            alpha = branch_result[1]
            if beta <= alpha:
                break

    # if we are caching, store the final value     
    if caching:
        caching_dict[(board, color)] = final_result
    return final_result

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
     # call the max node function as we want the best move(highest heuristic value)
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
