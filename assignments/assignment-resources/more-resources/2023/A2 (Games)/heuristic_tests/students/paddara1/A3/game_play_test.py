#!/usr/bin/env python
import sys
from othello_game import OthelloGameManager, AiPlayerInterface, play_game
from agent import compute_heuristic
import signal


smallboards = [((0, 0, 0, 0), (0, 2, 1, 0), (0, 1, 1, 1), (0, 0, 0, 0)),
((0, 1, 0, 0), (0, 1, 1, 0), (0, 1, 2, 1), (0, 0, 0, 2)),
((0, 0, 0, 0), (0, 2, 1, 0), (0, 1, 1, 1), (0, 1, 1, 0)),
((0, 1, 0, 0), (0, 2, 2, 0), (0, 1, 2, 1), (0, 0, 2, 2)),
((1, 0, 0, 2), (1, 1, 2, 0), (1, 1, 1, 1), (1, 2, 2, 2)),
((0, 1, 0, 0), (0, 1, 1, 0), (2, 2, 2, 1), (0, 0, 0, 2))]

def signal_handler(signum, frame):
    raise Exception("Timed out!")

def test_heuristic(efile, name):

    size = 6 #board size
    ordering = True
    caching = True
    minimax = False
    a1wins = 0
    a2wins = 0
    ties = 0
    agent1 = "agent_TA_default.py"
    agent2 = "agent_TA_student.py"
    n = 6 #num games = n * 2

    okflag = False
    timeset = 10 #if it takes more than ths to calculate the heuristic on a single board we have a problem
    signal.signal(signal.SIGALRM, signal_handler)
    for i in range(len(smallboards)):
        board = smallboards[i]

        signal.alarm(timeset)  # Two minutes per game MAX
        try:
            val = compute_heuristic(board, 1)
        except Exception as e:
            output = str(e)
            output = output.replace(",", "-")
            efile.write("{}, Exception encountered -- {}\n".format(name, output))
            val = 0

        if val != 0: okflag = True

        signal.alarm(timeset)  # Two minutes per game MAX
        try:
            val = compute_heuristic(board, 2)
        except Exception as e:
            output = str(e)
            output = output.replace(",", "-")
            efile.write("{}, Exception encountered -- {}\n".format(name, output))
            val = 0

        if val != 0: okflag = True

    if not okflag: return 0, 10, -1, [] #no points for no heuristic!!
    timeset = 120 #two minutes per game is allowed MAX

    #5 different depths
    totals = []
    for i in range(1, n): #depths from 3 to 7

        p1 = AiPlayerInterface(agent1, 1, i+2, minimax, caching, ordering)
        p2 = AiPlayerInterface(agent2, 2, i+2, minimax, caching, ordering)
        game = OthelloGameManager(size)

        signal.alarm(timeset)  # Two minutes per game MAX
        try:
            (p1name, p1, p2, p2name) = play_game(game, p1, p2)
        except Exception as e:
            output = str(e)
            output = output.replace(",", "-")
            efile.write("{}, Exception encountered -- {}\n".format(name, output))
            (p1name, p1, p2, p2name) = (p2.name, -99, -99, -99) #error!!

        totals.append((p1name, p1, p2, p2name, i+2, 0))
        if p1 == -99 and p1name == p1.name: #TA timed out or erred
            a2wins += 1
        elif p1 == -99 and p1name == p2.name: #student erred or timed out
            a1wins += 1
        elif p1 > p2: #TA win
            a1wins += 1
        elif p1 == 0:
            ties += 1
        else: #student win
            a2wins += 1

    #rotate player order
    for i in range(1, n):
        p1 = AiPlayerInterface(agent2, 1, i + 2, minimax, caching, ordering)
        p2 = AiPlayerInterface(agent1, 2, i + 2, minimax, caching, ordering)
        game = OthelloGameManager(size)

        signal.alarm(timeset)  # Two minutes per game MAX
        try:
            (p1name, p1, p2, p2name) = play_game(game, p1, p2)
        except Exception as e:
            output = str(e)
            output = output.replace(",", "-")
            efile.write("{}, Exception encountered -- {}\n".format(name, output))
            (p1name, p1, p2, p2name) = (p1.name, -99, -99, -99) #error!

        totals.append((p1name, p1, p2, p2name, i+2, 1))
        if p1 == -99 and p1name == p1.name: #student times out
            a1wins += 1
        elif p1 == -99 and p1name == p2.name: #TA times out
            a2wins += 1
        elif p1 > p2: #student win
            a2wins += 1
        elif p1 == 0:
            ties += 1
        else: #TA win
            a1wins += 1

    return a2wins, a1wins, ties, totals

if __name__ == "__main__":
    name = sys.argv[1]
    fname = sys.argv[2]
    sname = sys.argv[3]
    ename = sys.argv[4]
    student = 0
    TA = 0
    ties = 0
    totals = []

    ffile = open(fname, "a")
    sfile = open(sname, "a")
    efile = open(ename, "a")
    try:
        (student, TA, ties, totals) = test_heuristic(efile, name)
    except Exception as ex:
        output = str(ex)
        output = output.replace(",", "-")
        efile.write("{}, Exception encountered -- {}\n".format(name, output))

    if sum([student, TA, ties]) == 0: #this means the student agent could not play
        student, TA, ties = 0, 10, 0

    for i in totals:
        sfile.write("{}, {}, {}, {}, {}\n".format(name, i[1], i[2], i[4], i[5]))
    ffile.write("{}, {}, {}, {}\n".format(name, student, TA, ties))
    ffile.close()
    sfile.close()
    efile.close()

    print("{}, {}, {}, {}".format(name, student, TA, ties))



