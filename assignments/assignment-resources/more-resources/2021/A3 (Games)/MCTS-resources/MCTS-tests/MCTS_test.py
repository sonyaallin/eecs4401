'''
The processing time presented here gives you a rough idea about how long your MCTS should take to complete.
This is based on the simplest implementation without any optimization or high performance libraries.
As long as your algorithm can achieve similar time, you are fine.

part1: default board processing time
board size, limit <-> time(sec)
4, 1000                 0.3
6, 1000                 1.8
8, 1000                 5.9
10, 1000               13.6
12, 1000               28.1

part2: special board processing time
board_A = \
        ((0, 2, 1, 1, 0, 2, 0, 0),
         (0, 1, 1, 1, 2, 2, 2, 0),
         (0, 0, 1, 2, 1, 1, 2, 1),
         (0, 1, 1, 1, 1, 1, 1, 2),
         (1, 1, 1, 2, 1, 2, 2, 0),
         (0, 1, 1, 1, 2, 2, 2, 0),
         (0, 0, 1, 1, 1, 0, 1, 0),
         (0, 0, 0, 1, 2, 0, 0, 0))
limit <-> time(sec)
1000        1.2
2000        2.2
4000        4.6

board_B = \
        ((0, 0, 0, 0, 0, 0, 0, 0),
         (0, 2, 2, 2, 0, 0, 0, 0),
         (0, 1, 1, 1, 0, 0, 2, 0),
         (0, 0, 1, 2, 1, 2, 1, 0),
         (0, 0, 1, 2, 2, 0, 0, 0),
         (0, 1, 0, 2, 0, 0, 0, 0),
         (0, 0, 2, 0, 0, 0, 0, 0),
         (0, 0, 0, 0, 0, 0, 0, 0))
limit <-> time(sec)
1000        3.7
2000        7.4
4000        14.7

part3: special board next move score

board_A(after 2000 iterations):

CURRENT_ROOT's CHILDREN:
No. 0
-----MCTS node info------
reward: 12
total: 43
move: (0, 0)
-----------END-----------
No. 1
-----MCTS node info------
reward: 14
total: 46
move: (4, 0)
-----------END-----------
No. 2
-----MCTS node info------
reward: 59
total: 130
move: (5, 6)
-----------END-----------
No. 3
-----MCTS node info------
reward: 82
total: 172
move: (5, 7)
-----------END-----------
No. 4
-----MCTS node info------
reward: 157
total: 311
move: (6, 0)
-----------END-----------
No. 5
-----MCTS node info------
reward: 10
total: 39
move: (7, 0)
-----------END-----------
No. 6
-----MCTS node info------
reward: 502
total: 946
move: (7, 1)
-----------END-----------
No. 7
-----MCTS node info------
reward: 69
total: 148
move: (7, 4)
-----------END-----------
No. 8
-----MCTS node info------
reward: 26
total: 69
move: (7, 5)
-----------END-----------
No. 9
-----MCTS node info------
reward: 40
total: 95
move: (7, 6)
-----------END-----------


board_B(after 2000 iterations):
CURRENT_ROOT's CHILDREN:
No. 0
-----MCTS node info------
reward: 7
total: 29
move: (0, 0)
-----------END-----------
No. 1
-----MCTS node info------
reward: 418
total: 690
move: (1, 0)
-----------END-----------
No. 2
-----MCTS node info------
reward: 29
total: 64
move: (2, 0)
-----------END-----------
No. 3
-----MCTS node info------
reward: 56
total: 108
move: (2, 5)
-----------END-----------
No. 4
-----MCTS node info------
reward: 13
total: 39
move: (3, 0)
-----------END-----------
No. 5
-----MCTS node info------
reward: 129
total: 225
move: (3, 6)
-----------END-----------
No. 6
-----MCTS node info------
reward: 91
total: 164
move: (3, 7)
-----------END-----------
No. 7
-----MCTS node info------
reward: 27
total: 61
move: (4, 0)
-----------END-----------
No. 8
-----MCTS node info------
reward: 65
total: 122
move: (4, 2)
-----------END-----------
No. 9
-----MCTS node info------
reward: 24
total: 56
move: (4, 5)
-----------END-----------
No. 10
-----MCTS node info------
reward: 22
total: 53
move: (4, 6)
-----------END-----------
No. 11
-----MCTS node info------
reward: 97
total: 174
move: (5, 4)
-----------END-----------
No. 12
-----MCTS node info------
reward: 47
total: 93
move: (5, 5)
-----------END-----------
No. 13
-----MCTS node info------
reward: 65
total: 121
move: (6, 1)
-----------END-----------
'''

# You will need to modify these tests for your program
# You can just put these codes in your othello_mcts file
# An updated version of MCTS_state, you are not required to follow this way but
# it may help you understand the above outputs
class MCTS_state(object):
    """
            This sample code gives you a idea of how to store records for each node
            in the tree. However, you are welcome to modify this part or define your own
            class.
    """

    def __init__(self, step, parent, children, reward, total, move, board, visited=0):
        self.step = step
        self.parent = parent  # a list of states
        self.children = children  # a list of states
        self.reward = reward  # number of win
        self.total = total  # number of simulation for self and (grand*)children
        self.move = move
        self.board = board
        self.visited = visited  # 0 -> not visited yet, 1 -> already visited

    def add_child(self, new_child):
        self.children.append(new_child)

    def display(self):
        print("-----MCTS node info------")
        print("reward:", self.reward)
        print("total:", self.total)
        print("move:", self.move)
        print("-----------END-----------")

def create_initial_board(dimension):
    board = []
    for i in range(dimension):
        row = []
        for j in range(dimension):
            row.append(0)
        board.append(row)

    i = dimension // 2 - 1
    j = dimension // 2 - 1
    board[i][j] = 2
    board[i + 1][j + 1] = 2
    board[i + 1][j] = 1
    board[i][j + 1] = 1
    final = []
    for row in board:
        final.append(tuple(row))
    return tuple(final)

def test_for_MCTS_iteration():
    test_board = create_initial_board(12)
    
    global current_root
    time_list = []
    for i in range(10):
        current_root = MCTS_state(0, [], [], 0, 0, None, None)
        start_time = time.time()
        # MCTS_iteration(board, player, limit, initial=True)
        MCTS_iteration(test_board, 1, 1000, True)
        total_time = (time.time() - start_time)
        print("--- %.4f seconds ---" % total_time)
        time_list.append(total_time)
    print("average: %.4f seconds" % (sum(time_list)/len(time_list)))


def test_for_MCTS_iteration_v2():
    board_A = \
        ((0, 2, 1, 1, 0, 2, 0, 0),
         (0, 1, 1, 1, 2, 2, 2, 0),
         (0, 0, 1, 2, 1, 1, 2, 1),
         (0, 1, 1, 1, 1, 1, 1, 2),
         (1, 1, 1, 2, 1, 2, 2, 0),
         (0, 1, 1, 1, 2, 2, 2, 0),
         (0, 0, 1, 1, 1, 0, 1, 0),
         (0, 0, 0, 1, 2, 0, 0, 0))

    board_B = \
        ((0, 0, 0, 0, 0, 0, 0, 0),
         (0, 2, 2, 2, 0, 0, 0, 0),
         (0, 1, 1, 1, 0, 0, 2, 0),
         (0, 0, 1, 2, 1, 2, 1, 0),
         (0, 0, 1, 2, 2, 0, 0, 0),
         (0, 1, 0, 2, 0, 0, 0, 0),
         (0, 0, 2, 0, 0, 0, 0, 0),
         (0, 0, 0, 0, 0, 0, 0, 0))


    global current_root
    time_list = []
    for i in range(10):
        current_root = MCTS_state(0, [], [], 0, 0, None, None)
        start_time = time.time()
        MCTS_iteration(board_B, 1, 2000, True)
        total_time = (time.time() - start_time)
        print("--- %.4f seconds ---" % total_time)
        time_list.append(total_time)
    print("average: %.4f seconds" % (sum(time_list)/len(time_list)))