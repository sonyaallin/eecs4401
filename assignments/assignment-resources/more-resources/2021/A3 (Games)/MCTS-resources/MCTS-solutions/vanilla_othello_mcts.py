import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move
import math

def eprint(*args, **kwargs):  # you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)

ID = 0
class MCTS_state():
    """
            This sample code gives you a idea of how to store records for each node
            in the tree. However, you are welcome to modify this part or define your own
            class.
    """
    def __init__(self, ID, parent, child, reward, total, board,color,move,origin):
        self.ID = ID
        self.parent = parent    # a states
        self.child = child      # a list of states
        self.reward = reward    # number of win
        self.total = total      # number of simulation for self and (grand*)children
        self.board = board
        self.visited = 0        # 0 -> not visited yet, 1 -> already visited
        self.color = color
        self.move = move
        self.origin = origin
        
    def get_all_child(self):
        return self.child
    
    def get_next_color(self):
        return 1 if self.color == 2 else 2
    
    def get_ucb(self):
        bias = math.sqrt(2)
        if self.total == 0:
            return float("inf")
        parent_total = self.parent.total
        return self.reward/self.total + bias * math.sqrt(math.log(parent_total)/self.total)
    
    def is_visited(self):
        return self.visited
    
    def find_max_ucb_child(self):
        cur = None
        max_ucb = -float("inf")
        for  c in self.child:
            if not c.is_visited:
                return c
            cur_ucb = c.get_ucb()
            if( cur_ucb > max_ucb):
                cur = c
                max_ucb = cur_ucb
        return cur
    
    
    def get_move(self):
        return self.move
    
    def find_the_best_move(self):
        cur = None
        max_ucb = -float("inf")
        for  c in self.child:
            if not c.is_visited:
                continue
            cur_ucb = c.get_ucb()
            if( cur_ucb > max_ucb):
                cur = c
                max_ucb = cur_ucb
        return cur.get_move()
    

    def update(self, win):
        if(win):
            self.total += 1
            self.reward += 1
        else:
            self.total += 1
        p = self.parent
        if p:
            p.update(win)
            
            
    def generate_sample(self):
        cur_color = self.color
        cur_board = self.board
        all_move = get_possible_moves(cur_board, cur_color)
        while(len(all_move) != 0):
            i,j = random.choice(all_move)
            cur_board = play_move(cur_board,cur_color,i,j)
            cur_color = 1 if cur_color  == 2 else 2
            all_move = get_possible_moves(cur_board, cur_color)
        score = get_score(cur_board)
        self_score = score[self.origin - 1]
        other_score = score[0 if self.origin  == 2 else 1]
        self.update(self_score > other_score)
        
        
            
        
    def find_the_expand_child(self):
        if(self.visited == 0 ):
            all_moves = get_possible_moves(self.board, self.color)
            next_color = self.get_next_color()
            for move in all_moves:
                global ID
                next_board = play_move(self.board,self.color,move[0],move[1])
                mcts = MCTS_state(ID, self, [], 0, 0, next_board,next_color,move, self.origin)
                ID += 1
                self.child.append(mcts)
            self.visited = 1
            if(len(self.child) == 0):
                return self
            else:
                return self.child[0]
        cur = self.find_max_ucb_child()
        if(cur.is_visited()):
            return cur.find_the_expand_child()
        return cur
        ##first expand
            
            
    def mcts_step(self):
        cur = self.find_the_expand_child()
        cur.generate_sample()
        
        
    
def select_move_MCTS(board, color, limit):
    """
               You can add additional help functions as long as this function will return a position tuple
    """
    global ID
    ID = 0
    initial_state = MCTS_state(ID, None, [], 0, 0, board,color,None,color)
    for itr in range(limit):
        initial_state.mcts_step()
    eprint([c.get_ucb() for c in initial_state.get_all_child()])
    return initial_state.find_the_best_move()
     # this is just an example. delete it when you start to code.

def run_mcts():
    """
        Please do not modify this part.
        """
    print("Othello AI")  # First line is the name of this AI
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