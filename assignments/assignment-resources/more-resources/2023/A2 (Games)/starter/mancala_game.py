#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module contains the main Mancala game which maintains the board, score, and 
players.  

Thanks to Daniel Bauer, Columbia University, for a version of Othello that this was based on
"""
import sys
import subprocess
from threading import Timer
from collections import defaultdict

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class MCTS: # Use this to represent an MCTS tree
    def __init__(self, weight=1):
        self.rewards = defaultdict(int)  # This will map states (e.g. boards) onto total rewards
        self.counts = defaultdict(int)  #  This will map states (e.g. boards) onto total visits
        self.successors = dict()    # This will store successors of state and it can be used to represent states that have been expaned in the tree.
                                    # States (or boards) that are keys of the dict will be those that have been explored.
                                    # Boards that exist in values but NOT in keys represent leaves (or unexplored states)
        self.weight = weight  # This can be used to dial the "exploration" weight up or down.

    def __str__(self):
        string = ""
        for state in self.successors:
            string += "{}, ".format(state)

        return "rewards: {}, counts: {}, states visited {}".format(sum(self.rewards.values()), sum(self.counts.values()), string)

class InvalidMoveError(RuntimeError):
    pass

class AiTimeoutError(RuntimeError):
    pass

class Board(object):
    def __init__(self, pockets, mancalas):
        self.pockets = pockets
        self.mancalas = mancalas

    def __eq__(self, other):
        if self.pockets == other.pockets and self.mancalas == other.mancalas:
            return True
        else:
            return False

    def __hash__(self):
        return hash((tuple(self.pockets), tuple(self.mancalas)))

class Player(object):
    def __init__(self, color, name="Human"):
        self.name = name
        self.color = color

    def get_move(self, manager):
        pass  

class AiPlayerInterface(Player):

    TIMEOUT = 30

    def __init__(self, filename, color, limit, algorithm = 2, caching = False):

        self.color = color
        self.process = subprocess.Popen(['python3',filename], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        name = self.process.stdout.readline().decode("ASCII").strip()
        print("AI introduced itself as: {}".format(name))
        self.name = name
        self.process.stdin.write((str(color) + "," + str(limit) + "," + str(caching) + "," + str(algorithm) + "\n").encode("ASCII"))
        self.process.stdin.flush()

    def timeout(self): 
        sys.stderr.write("{} timed out.".format(self.name))
        self.process.kill() 
        self.timed_out = True

    def get_move(self, manager):
        white_score, dark_score = manager.board.mancalas[0], manager.board.mancalas[1]
        print((white_score, dark_score))
        self.process.stdin.write("SCORE {} {}\n".format(white_score, dark_score).encode("ASCII"))
        self.process.stdin.flush()
        self.process.stdin.write("{}\n".format(str(manager.board.pockets)).encode("ASCII"))
        self.process.stdin.flush()
        self.process.stdin.write("{}\n".format(str(manager.board.mancalas)).encode("ASCII"))
        self.process.stdin.flush()

        timer = Timer(AiPlayerInterface.TIMEOUT, lambda: self.timeout())
        self.timed_out = False
        timer.start()

        # Wait for the AI call
        move_s = self.process.stdout.readline().decode("ASCII")
        if self.timed_out:  
            raise AiTimeoutError
        timer.cancel()

        return move_s
    
    def kill(self,manager):
        white_score, dark_score = get_score(manager.board)
        self.process.stdin.write("FINAL {} {}\n".format(white_score, dark_score).encode("ASCII"))
        self.process.kill() 

class MancalaGameManager(object):

    def __init__(self, dimension = 6):
        self.dimension = dimension
        self.board = Board(self.create_initial_pockets(), [0, 0]);
        self.current_player = 0
            
    def create_initial_pockets(self):
        pockets = []
        for i in range(2): 
            row = []
            for j in range(self.dimension):
                row.append(4) # 4 stones in each pocket to begin
            pockets.append(row) 

        final = [] # deep copy
        for row in pockets: 
            final.append(tuple(row))
        return tuple(final)

    def print_board(self):
        for row in self.board.pockets: 
            print(" ".join([str(x) for x in row]))
                   
    def play(self, i, j):
        i = int(i)
        j = int(j)
        #eprint("{} {}".format(i, j))
        if self.board.pockets[j][i] == 0 or j != self.current_player:
           raise InvalidMoveError("That is not a valid move for this player.")
     
        self.board = play_move(self.board, self.current_player, i) 
        self.current_player = abs(self.current_player - 1) #can be 0 or 1

    def get_possible_moves(self):
        return get_possible_moves(self.board, self.current_player)


def get_possible_moves(board, player):
    """
    Return a list of all possible (column,row) tuples that player can play on
    the current board. 
    """
    # Board is printed upside down!
    # p = abs(player - 1)
    result = []
    for j in range(len(board.pockets[player])):
        if board.pockets[player][j] > 0: # If there are pieces to move
            result.append(j)
    return result

def end_game(board, player):
    value = 0
    new_board = []
    for row in board.pockets: 
        new_board.append(list(row[:]))

    for j in range(len(new_board[player])):
        value +=  new_board[player][j]
        new_board[player][j] = 0

    final = []
    for row in new_board: 
        final.append(tuple(row))
    return tuple(final), value 

def play_move(board, player, j):
    """
    Play a move on the current board. 
    """  
    side = player
    new_board = []
    new_mancalas = [board.mancalas[0], board.mancalas[1]]
    for row in board.pockets: 
        new_board.append(list(row[:]))

    #eprint(board.pockets)
    stone_count = board.pockets[side][j] # Find the number of stones in the pocket
    new_board[side][j] = 0 # Set to 0

    if (player == 1):
        direction = True
        ind = j + 1
    else:
        direction = False
        ind = j - 1

    while (stone_count > 0): # Deposit stones around the board

        # Are we at the end of the board?
        if (ind > (len(board.pockets[side])-1) or ind < 0):

            side = 0 if side == 1 else 1 # Swap the side of the board
            direction = not direction # Swap the direction of the deposite

            if (ind > (len(board.pockets[side])-1)): # If we are at the end of the board, deposit stone in a mancala before we continue
                if (player == 1):
                    stone_count -= 1
                    new_mancalas[player] += 1
                ind = len(board.pockets[side])-1
            else:
                if (player == 0):
                    stone_count -= 1
                    new_mancalas[player] += 1
                ind = 0

        if stone_count == 0: # Is it possible we bottomed out at this point?
            break

        # But if not, put a stone in a pocket and decrement stone count
        new_board[side][ind] = new_board[side][ind] + 1
        stone_count -= 1

        if (stone_count == 0 and new_board[side][ind] == 1 and side == player): # Do we have a capture?
            captures = new_board[abs(side-1)][ind] # If yes, capture stones in the opposite pit
            new_board[abs(side-1)][ind] = 0
            new_mancalas[player] += captures

        if (direction): ind += 1
        else: ind -= 1

    # Return a copy of the board details
    final = []
    for row in new_board: 
        final.append(tuple(row))

    #eprint(final)

    return Board(final, new_mancalas)


def get_score(game):
    return game.mancalas[0], game.mancalas[1]
