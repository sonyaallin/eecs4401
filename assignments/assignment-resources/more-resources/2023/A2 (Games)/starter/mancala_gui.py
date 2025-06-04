#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module contains a simple graphical user interface for Mancala. 

Thanks to Daniel Bauer, Columbia University, for a version of Othello that this was based on
"""
import getopt, sys
import random
from datetime import datetime

from tkinter import *
from tkinter import scrolledtext

from mancala_game import MancalaGameManager, AiPlayerInterface, Player, InvalidMoveError, AiTimeoutError, end_game, get_possible_moves

class MancalaGui(object):

    def __init__(self, game_manager, player1, player2):

        self.game = game_manager
        self.players = [player1, player2]
        self.height = 2  #2 sides to the board
        self.width = self.game.dimension #pit count
        
        self.offset = 3
        self.cell_size = 100
        self.stone_size = 10

        root = Tk()
        root.wm_title("Mancala")
        root.lift()
        root.attributes("-topmost", True)
        self.root = root
        self.canvas = Canvas(root,height = self.cell_size * (self.height+1) + self.offset,width = self.cell_size * (self.width+2) + self.offset)
        self.move_label = Label(root)
        self.score_label = Label(root)
        self.text = scrolledtext.ScrolledText(root, width=70, height=10)
        self.move_label.pack(side="top")
        self.score_label.pack(side="top")
        self.canvas.pack()
        self.text.pack()
        self.draw_board()

    def get_position(self,x,y):
        i = (x -self.offset) // self.cell_size
        j = (y -self.offset) // self.cell_size
        return i,j

    def mouse_pressed(self,event):
        # get the human move
        i,j = self.get_position(event.x, event.y)
        try:
            player = "Player A" if self.game.current_player == 1 else "Player B"
            self.log("{}: {},{}".format(player, i-1, j))
            self.game.play(i-1, j)
            self.draw_board()
            a = get_possible_moves(self.game.board, self.game.current_player)
            if not get_possible_moves(self.game.board, self.game.current_player):
                other_player = abs(self.game.current_player-1)
                self.game.board.pockets, value = end_game(self.game.board, other_player)
                self.game.board.mancalas[other_player] += value                
                self.draw_board()
                winner = "Player B" if (self.game.board.mancalas[0] > self.game.board.mancalas[1]) else "Player A" 
                self.log("GAME OVER: winner is {}".format(winner))
                self.shutdown("Game Over")
            elif isinstance(self.players[self.game.current_player], AiPlayerInterface):
                self.root.unbind("<Button-1>")
                self.root.after(100,lambda: self.ai_move())
        except InvalidMoveError:
            self.log("Invalid move. {},{}".format(i,j))

    def shutdown(self, text):
        self.move_label["text"] = text 
        self.root.unbind("<Button-1>")
        if isinstance(self.players[0], AiPlayerInterface): 
            self.players[0].kill(self.game)
        if isinstance(self.players[1], AiPlayerInterface): 
            self.players[1].kill(self.game)
 
    def ai_move(self):
        player_obj = self.players[self.game.current_player]
        try:
            #get the AI move
            flag = False
            move = player_obj.get_move(self.game)
            player = "Player A" if self.game.current_player == 1 else "Player B"
            player = "{} {}".format(player_obj.name, player)
            if move != "None\n": #
                flag = True
                self.log("{}: {}".format(player, move))
                self.game.play(move,self.game.current_player)
            self.draw_board()
            if not flag or not get_possible_moves(self.game.board, self.game.current_player):
                other_player = abs(self.game.current_player-1)
                self.game.board.pockets, value = end_game(self.game.board, other_player)
                self.game.board.mancalas[other_player] += value
                self.draw_board()
                winner = "Player B" if (self.game.board.mancalas[0] > self.game.board.mancalas[1]) else "Player A" 
                self.log("GAME OVER: winner is {}".format(winner))
                self.shutdown("Game Over")
            elif isinstance(self.players[self.game.current_player], AiPlayerInterface):
                self.root.after(1, lambda: self.ai_move())
            else: 
                self.root.bind("<Button-1>",lambda e: self.mouse_pressed(e))
        except AiTimeoutError:
            self.shutdown("Game Over, {} lost (timeout)".format(player_obj.name))

    def run(self):
        if isinstance(self.players[0], AiPlayerInterface):
            self.root.after(10, lambda: self.ai_move())
        else: 
            self.root.bind("<Button-1>",lambda e: self.mouse_pressed(e))        
        self.draw_board()
        self.canvas.mainloop()

    def draw_board(self):
        self.draw_pits()
        self.draw_stones()
        player = "Player A" if self.game.current_player == 1 else "Player B"
        self.move_label["text"]= player
        self.score_label["text"]= "Player B {} : {} Player A".format(*self.game.board.mancalas) 
   
    def log(self, msg, newline = True): 
        self.text.insert("end","{}{}".format(msg, "\n" if newline else ""))
        self.text.see("end")
 
    def draw_pits(self):
        colors = ("light green", "light blue") if self.game.current_player == 1 else ("light blue", "light green")
        for i in range(1,self.width+1):
            self.canvas.create_oval(i*self.cell_size + self.offset, self.offset, (i+1)*self.cell_size + self.offset, self.cell_size + self.offset, fill=colors[0])
            self.canvas.create_oval(i*self.cell_size + self.offset, self.cell_size + self.offset, (i+1)*self.cell_size + self.offset, 2*self.cell_size + self.offset, fill=colors[1])
        
        #pits for players
        self.canvas.create_oval(self.offset, self.offset, self.cell_size + self.offset, 2*self.cell_size + self.offset, fill="white")
        self.canvas.create_oval((self.width+1)*self.cell_size + self.offset, self.offset, (self.width+2)*self.cell_size + self.offset, 2*self.cell_size + self.offset, fill="white")


    def draw_stone(self, i, j):
        x = (i + 0.5) * self.cell_size - self.stone_size/2 + random.randint(0,20) - 10
        y = (j + 0.5) * self.cell_size - self.stone_size/2 + random.randint(0,20) - 10
        
        self.canvas.create_oval(x, y, x+self.stone_size, y+self.stone_size, fill="green")
        
    def draw_stones(self):       
        for i in range(2):
            for j in range(1,len(self.game.board.pockets[i])+1):
                x = (j + 0.5) * self.cell_size + self.offset
                y = (i+1)*self.cell_size - 2*self.offset
                for k in range(self.game.board.pockets[i][j-1]):
                    self.draw_stone(j, i)
                self.canvas.create_text(x, y,font="Arial", text=str(self.game.board.pockets[i][j-1]))

        #draw disks on the board
        for i in range(self.game.board.mancalas[0]):
            x = self.cell_size/2 + random.randint(0,20) - 10
            y = self.cell_size + random.randint(0,20) - 10
            self.canvas.create_oval(x, y, x + self.stone_size, y + self.stone_size, fill="blue")
        x = self.cell_size/2
        y = 2*self.cell_size - 2*self.offset
        self.canvas.create_text(x, y,font="Arial", text=str(self.game.board.mancalas[0]))

        #draw disks in the stone pits
        for i in range(self.game.board.mancalas[1]):
            x = (self.width+1.5)*self.cell_size + random.randint(0,20) - 10
            y = self.cell_size + random.randint(0,20) - 10 
            self.canvas.create_oval(x, y, x + self.stone_size, y + self.stone_size, fill="red")
        x = (self.width+1.5)*self.cell_size
        y = 2*self.cell_size - 2*self.offset
        self.canvas.create_text(x, y,font="Arial", text=str(self.game.board.mancalas[1]))


def main(argv):

    random.seed(datetime.now().timestamp())

    size = 0
    limit = -1       
    algorithm = 0
    agent1 = None
    agent2 = None
    caching = 0

    try:
        opts, args = getopt.getopt(argv,"hl:d:a:b:t:c",["limit=","dimension=","agent1=","agent2=","algorithm=","caching="])
    except getopt.GetoptError:
        print('mancala_gui.py -d <dimension> [-a <agentA> -b <agentB> -l <depth-limit> -t <algorithm-choice> -c]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('mancala_gui.py -d <dimension> -a <agentA> [-b <agentB> -l <depth-limit> -t <algorithm-choice> -c]')
            sys.exit()
        elif opt in ("-d", "--dimension"):
            size = int(arg)
        elif opt in ("-a", "--agentA"):
            agent1 = arg
        elif opt in ("-b", "--agentB"):
            agent2 = arg
        elif opt in ("-c", "--caching"):
            caching = 1
        elif opt in ("-t", "--type"):
            algorithm = int(arg)
        elif opt in ("-l", "--limit"):
            limit = int(arg)  

    if size <= 0: #if no dimension provided
        print('Please provide a board size.')
        print('mancala_gui.py -d <dimension> [-a <agentA> -b <agentB> -l <depth-limit> -t <algorithm-choice> -c]')
        sys.exit(2)  

    if agent1 != None and agent2 != None and size > 0:
        p1 = AiPlayerInterface(agent1, 0, limit, algorithm, caching)
        p2 = AiPlayerInterface(agent2, 1, limit, algorithm, caching)
    elif agent1 != None and size > 0:
        p1 = Player(0)
        p2 = AiPlayerInterface(agent1, 1, limit, algorithm, caching)
    else: 
        p1 = Player(0)
        p2 = Player(1)
        
    game = MancalaGameManager(size)
    gui = MancalaGui(game, p1, p2) 
    gui.run()

if __name__ == "__main__":
   main(sys.argv[1:])

