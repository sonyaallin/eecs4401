#!/usr/bin/env python
import os  # for time functions
import subprocess

# import student's functions
from agent_TA import *

smallboards = [((0, 0, 0, 0), (0, 2, 1, 0), (0, 1, 1, 1), (0, 0, 0, 0)),
((0, 1, 0, 0), (0, 1, 1, 0), (0, 1, 2, 1), (0, 0, 0, 2)),
((0, 0, 0, 0), (0, 2, 1, 0), (0, 1, 1, 1), (0, 1, 1, 0)),
((0, 1, 0, 0), (0, 2, 2, 0), (0, 1, 2, 1), (0, 0, 2, 2)),
((1, 0, 0, 2), (1, 1, 2, 0), (1, 1, 1, 1), (1, 2, 2, 2)),
((0, 1, 0, 0), (0, 1, 1, 0), (2, 2, 2, 1), (0, 0, 0, 2))]

bigboards = [((0, 0, 0, 0, 0, 0), (0, 0, 2, 2, 0, 0), (0, 1, 1, 2, 2, 0), (2, 2, 1, 2, 0, 0), (0, 1, 0, 1, 2, 0), (0, 0, 0, 0, 0, 0)),
((0, 0, 0, 0, 0, 0), (0, 0, 1, 2, 0, 0), (0, 1, 1, 1, 1, 0), (2, 2, 1, 2, 0, 0), (0, 1, 0, 1, 2, 0), (0, 0, 0, 0, 0, 0)),
((0, 0, 0, 0, 1, 0), (0, 0, 1, 1, 0, 0), (0, 1, 1, 1, 1, 0), (2, 2, 1, 2, 0, 0), (0, 2, 0, 1, 2, 0), (0, 0, 2, 2, 1, 0)),
((0, 0, 0, 0, 0, 0), (0, 0, 0, 2, 0, 0), (0, 1, 2, 2, 2, 0), (0, 2, 2, 2, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0)),
((0, 0, 0, 0, 0, 0), (0, 0, 0, 2, 0, 0), (0, 1, 2, 1, 1, 0), (0, 2, 2, 2, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0))]

#Select what to test
test_heuristic = True

if test_heuristic:
    print('Testing Heuristic')  
    p1 = []
    p2 = []
    draw = 0;
    p1win = 0;
    p2win = 0;

    for i in range(0,5):
      for j in range(0,2):
        if (j%2 == 1):
          command = 'python3 othello_gui.py -d 6 -a agent_TA.py -b agent_TA2.py -l ' + str(i+2) + ' -c -o > result.txt'
        else:
          command = 'python3 othello_gui.py -d 6 -a agent_TA2.py -b agent_TA.py -l ' + str(i+2) + ' -c -o > result.txt'
        os.system(command)
        line = subprocess.check_output(['tail', '-1', 'result.txt'])
        values = [int(s) for s in line.split() if s.isdigit()]
        
        if (j%2 == 1):
          p1.append(values[0])
          p2.append(values[1])
          if values[0] > values[1]:
            p1win = p1win+1;
          elif values[0] == values[1]:
            draw = draw+1;
          elif values[0] < values[1]:
            p2win = p2win+1;
        else:   
          p1.append(values[1])
          p2.append(values[0])          
          if values[0] > values[1]:
            p2win = p2win+1;
          elif values[0] == values[1]:
            draw = draw+1;
          elif values[0] < values[1]:
            p1win = p1win+1;
                    
    winner = ""
    if (p1win > p2win):
      winner = "Player 1"
    elif (p1win > p2win):
      winner = "Player 2"     
    elif (p1win == p2win):
      winner = "None (tie)"  

    print("Player 1 wins {} of {} boards".format(p1win, len(p1)))
    print("Player 2 wins {} of {} boards".format(p2win, len(p2)))      
    print("Tie on {} of {} boards".format(draw, len(p2)))
    print("Overall winner: {}".format(winner)) 

    dir_path = os.path.dirname(os.path.realpath(__file__))

    f=open("A3games.txt", "a+")
    f.write(dir_path)
    f.write("\nPlayer 1 wins {} of {} boards\n".format(p1win, len(p1)))
    f.write("Player 2 wins {} of {} boards\n".format(p2win, len(p2)))      
    f.write("Tie on {} of {} boards\n".format(draw, len(p2)))
    f.write("Overall winner: {}\n\n".format(winner))  
    f.close()  





