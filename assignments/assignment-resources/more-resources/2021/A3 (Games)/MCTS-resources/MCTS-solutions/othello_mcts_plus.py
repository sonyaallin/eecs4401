"""
MCTS-alphabeta hybrid.
MCTS earlygame, depth-limited alphabeta midgame, unlimited alphabeta engame.

Monte Carlo Tree Search uses caching, hueristic simulation,
and move selection during simulation at 10x speed.

Alphabeta uses node ordering and a filthy heuristic.
"""


from collections import Counter
from itertools import chain
from math import sqrt, log
import random
from statistics import mean
import sys
from time import time

from othello_shared import find_lines, get_possible_moves, get_score, play_move


# Globals & utilities
node_lookup = {}
dirs = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
corners = [[],[],[],[]]
size = [0, 0]

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


##
## Alphabeta endgame algorithm
##
def compute_utility(board, color):
    score = get_score(board)
    return score[1] - score[0] if color == 2 else score[0] - score[1]

def corner_occupancy_score(board, color):
    end = len(board) - 1
    score = 0
    for i in (0, end):
        for j in (0, end):
            if board[i][j] != 0:
                if board[i][j] == color:
                    score += 1
                else:
                    score -= 1
    return score

def mobility_score(board, color):
    return len(get_possible_moves(board, color)) - len(get_possible_moves(board, flip(color)))

def tile_difference_and_moves_remaining(board, color):
    counts = Counter(chain(*board))
    tile_difference = counts[color] - counts[flip(color)]
    moves_remaining = counts[0]

    return tile_difference, moves_remaining

def compute_heuristic(board, color):
    corners = corner_occupancy_score(board, color)
    mobility = mobility_score(board, color)
    tiles, moves = tile_difference_and_moves_remaining(board, color)

    score = (corners * 10) + (mobility * 2) + ((tiles) * ((moves + 1)**(-0.5))) 

    return score

def alphabeta_min_node(board, color, alpha, beta, limit, ordering):
    moves = get_possible_moves(board, flip(color))

    if len(moves) == 0:
        return compute_utility(board, color) * 10E4
    if limit == 0:
        return compute_heuristic(board, color)

    # Iterate over possible next boards, optionally sorted by utility (most negative first)
    next_boards = list(map(lambda move: play_move(board, flip(color), *move), moves))
    if ordering:
        next_boards.sort(key=lambda board: compute_utility(board, color))

    best_value = 10E6
    for next_board in next_boards:
        value = alphabeta_max_node(
            next_board, color, alpha, beta, limit-1, ordering
        )
        if value < beta:
            beta = value
            if beta <= alpha:
                return value
        if value < best_value:
            best_value = value

    return best_value

def alphabeta_max_node(board, color, alpha, beta, limit, ordering):
    moves = get_possible_moves(board, color)

    if len(moves) == 0:
        return compute_utility(board, color) * 10E4
    if limit == 0:
        return compute_heuristic(board, color)

    # Iterate over possible next boards, optionally sorted by utility
    next_boards = list(map(lambda move: play_move(board, color, *move), moves))
    if ordering:
        next_boards.sort(key=lambda board: compute_utility(board, color), reverse=True)

    best_value = -10E6
    for next_board in next_boards:
        value = alphabeta_min_node(
            next_board, color, alpha, beta, limit-1, ordering
        )
        if value > alpha:
            alpha = value
            if alpha >= beta:
                return value
        if value > best_value:
            best_value = value

    return best_value

def select_move_alphabeta(board, color, limit, ordering):
    moves = get_possible_moves(board, color)
    bestmove = ((-1,-1), -10E6)
    alpha = -10E6
    beta = 10E6
    for move in moves:
        value = alphabeta_min_node(
            play_move(board, color, *move),
            color, alpha, beta, limit-1, ordering
        )
        if value >= alpha:
            alpha = value
        if value > bestmove[1]:
            bestmove = (move, value)

    return bestmove[0]


##
## Monte Carlo Tree Search with caching and heuristic simulation
##

class Node():
    def __init__(self, parents, children, wins, total, board, turn):
        self.parents = parents
        self.children = children
        self.wins = wins
        self.total = total
        self.board = board
        self.expanded = False
        self.turn = turn
        node_lookup[board] = self
    
def flip(player):
    return 2 if player == 1 else 1

def detect_corner(move, end):
    i, j = move[0], move[1]
    return (
        i == 0 and j == 0
        or i == end and j == 0
        or i == 0 and j == end
        or i == end and j == end
    )

def compute_outcome(board):
    score = get_score(board)
    
    outcome = {
        1: score[0] > score[1],
        2: score[1] > score[0]
    }

    if score[0] == score[1]:
        outcome.update({1: 0.5, 2: 0.5})

    return outcome

def upper_confidence_bound(node):
    if node.total == 0:
        return float('Inf')

    avg_parent_total = mean(parent.total for parent in node.parents)
    ucb = (node.wins / node.total) + sqrt(2*log(avg_parent_total) / node.total)

    return ucb

def select(node):
    if not node.expanded or not node.children:
        return node

    selected_subnode = max(node.children, key=upper_confidence_bound)

    return select(selected_subnode)

def expand(node):
    if node.expanded:
        return

    for move in get_possible_moves(node.board, node.turn):
        board = play_move(node.board, node.turn, *move)
        pre_existing_node = node_lookup.get(board)
        if pre_existing_node:
            pre_existing_node.parents.append(node)
        else:
            child = Node(
                parents=[node], 
                children=[],
                wins=0,
                total=0,
                board=board,
                turn=flip(node.turn)
            )
            node.children.append(child)

    node.expanded = True

def simulate_random(board, turn):

    xstart = random.randint(0, size[1])
    ystart = random.randint(0, size[1])
    
    def get_move():
        # corners first
        for x, y in corners:
            if board[y][x] == 0:
                for xdir, ydir in dirs:
                    u = x + xdir
                    v = y + ydir
                    found_other = False
                    while u >= 0 and u < size[0] and v >= 0 and v < size[0]:
                        if board[v][u] == 0:
                            break
                        elif board[v][u] == turn:
                            if not found_other:
                                break
                            else:
                                return (x,y)
                        u += xdir
                        v += ydir
                        found_other = True

        # if corners empty check the rest
        for i in range(size[0]):
            for j in range(size[0]):
                x = (xstart+i) % (size[1])
                y = (ystart+j) % (size[1])
                if board[y][x] == 0:

                    for xdir, ydir in dirs:
                        u = x + xdir
                        v = y + ydir
                        found_other = False
                        while u >= 0 and u < size[0] and v >= 0 and v < size[0]:
                            if board[v][u] == 0:
                                break
                            elif board[v][u] == turn:
                                if not found_other:
                                    break
                                else:
                                    return (x,y)
                            u += xdir
                            v += ydir
                            found_other = True
        return False

    move = get_move()

    if not move:
        return compute_outcome(board)

    next_board = play_move(board, turn, *move)

    return simulate_random(next_board, flip(turn))

def simulate(board, turn):
    moves = get_possible_moves(board, turn)

    if len(moves) == 0:
        return compute_outcome(board)

    next_move = next(
        (move for move in moves if detect_corner(move, len(board)-1)),
        random.choice(moves)
    )
    next_board = play_move(board, turn, *next_move)
    
    return simulate_random(next_board, flip(turn))

def backpropagate(node, outcome):
    node.total += 1
    # update outcome for who made this move / node
    node.wins += outcome[flip(node.turn)]

    for parent in node.parents:
        backpropagate(parent, outcome)

def select_move_MCTS(board, color, limit):
    """
    Uses MCTS for the early game, depth-limited alpha-beta
    for midgame, and unlimited alpha-beta for endgame.

    MCTS component includes caching and heuristic simulation, as well as a modified
    move-finding function that is 10x faster than get_possible_moves.
    """
    if limit < 1:
        if limit == 0:
            return select_move_alphabeta(board, color, 1, True)
        limit = 10E6
    board = tuple(tuple(row) for row in board)
    size[0] = len(board)
    size[1] = len(board) - 1
    corners[0] = (0, 0)
    corners[1] = (0, size[1])
    corners[2] = (size[1], 0)
    corners[3] = (size[1], size[1])

    counts = Counter(chain(*board))
    moves_remaining = counts[0]

    # Endgame: unlimited alpha-beta
    if moves_remaining < 12:
        return select_move_alphabeta(board, color, 100, True)
    # Midgame: 4-deep alpha-beta
    if moves_remaining < 50:
        return select_move_alphabeta(board, color, 4, True)

    # Earlygame: MCTS w/ heuristic simulation & caching
    root = node_lookup.get(board) or Node([], [], 0, 0, board, color)
    start_time = time()
    time_limit = 10

    counter = 0
    while time() - start_time < time_limit - 0.1 and counter < limit:
        node = select(root)
        expand(node)
        outcome = simulate(node.board, node.turn)
        backpropagate(node, outcome)
        counter += 1
    eprint('[Custom] passes: ', counter)
    
    best_node = max(root.children, default=None, key=lambda node: node.wins / node.total if node.total else 0)
    if not best_node:
        eprint('no move found')
        return ()

    best_move = next(
        move
        for move in get_possible_moves(root.board, root.turn)
        if play_move(root.board, root.turn, *move) == best_node.board
    )

    return best_move

def run_mcts():
    """
        Please do not modify this part.
        """
    print("Hybrid-Stairs")  # First line is the name of this AI
    arguments = input().split(",")

    color = int(arguments[0])  # Player color: 1 for dark (goes first), 2 for light.
    limit = int(arguments[1])  # Iteration limit
    minimax = int(arguments[2])  # not used here
    caching = int(arguments[3])  # not used here
    ordering = int(arguments[4])  # not used here


    if (limit == -1):
        eprint("Iteration Limit is OFF")
    else:
        eprint("Iteration Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True:  # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL":  # Game is over.
            print
        else:
            board = eval(input())  # Read in the input and turn it into a Python
            # object. The format is a list of rows. The
            # squares in each row are represented by
            # 0 : empty square
            # 1 : dark disk (player 1)
            # 2 : light disk (player 2)

            # Select the move and send it to the manager
            movei, movej = select_move_MCTS(board, color, limit)

            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_mcts()
