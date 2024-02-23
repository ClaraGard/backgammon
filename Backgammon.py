#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# https://github.com/weekend37/Backgammon/blob/master/Backgammon.py
"""
Backgammon interface
Run this program to play a game of Backgammon
"""
import numpy as np
import matplotlib.pyplot as plt
import time
import random

def init_board():
    # initializes the game board
    board = np.zeros(29)
    board[1] = -2
    board[12] = -5
    board[17] = -3
    board[19] = -5
    board[6] = 5
    board[8] = 3
    board[13] = 5
    board[24] = 2
    return board

def roll_dice():
    # rolls the dice
    dice = np.random.randint(1, 7, 2)
    
    return dice

def game_over(board):
    # returns True if the game is over    
    return board[27] == 15 or board[28] == -15
    
def pretty_print(board):
    string = str(np.array2string(board[1:13]) + '\n' +
                 np.array2string(board[24:12:-1]) + '\n' +
                 np.array2string(board[25:29]))
    print("board: \n", string)
      
def legal_move(board, die, player):
    # finds legal moves for a board and one dice
    # inputs are some BG-board, the number on the die and which player is up
    # outputs all the moves (just for the one die)
    possible_moves = []

    if player == 1:
        
        # dead piece, needs to be brought back to life
        if board[25] > 0: 
            start_pip = 25 - die
            if board[start_pip] > -2:
                possible_moves.append(np.array([25, start_pip]))
                
        # no dead pieces        
        else:
            # adding options if player is bearing off
            if sum(board[7:25] > 0) == 0: 
                if (board[die] > 0):
                    possible_moves.append(np.array([die, 27]))
                    
                elif not game_over(board): # smá fix
                    # everybody's past the dice throw?
                    s = np.max(np.where(board[1:7] > 0)[0] + 1)
                    if s < die:
                        possible_moves.append(np.array([s, 27]))
                    
            possible_start_pips = np.where(board[0:25] > 0)[0]

            # finding all other legal options
            for s in possible_start_pips:
                end_pip = s-die
                if end_pip > 0:
                    if board[end_pip] > -2:
                        possible_moves.append(np.array([s, end_pip]))
                        
    elif player == -1:
        # dead piece, needs to be brought back to life
        if board[26] < 0: 
            start_pip = die
            if board[start_pip] < 2:
                possible_moves.append(np.array([26, start_pip]))
                
        # no dead pieces       
        else:
            # adding options if player is bearing off
            if sum(board[1:19] < 0) == 0: 
                if (board[25 - die] < 0):
                    possible_moves.append(np.array([25 - die, 28]))
                elif not game_over(board): # smá fix
                    # everybody's past the dice throw?
                    s = np.min(np.where(board[19:25] < 0)[0])
                    if (6 - s) < die:
                        possible_moves.append(np.array([19 + s, 28]))

            # finding all other legal options
            possible_start_pips = np.where(board[0:25] < 0)[0]
            for s in possible_start_pips:
                end_pip = s + die
                if end_pip < 25:
                    if board[end_pip] < 2:
                        possible_moves.append(np.array([s, end_pip]))
        
    return possible_moves

def legal_moves(board, dice, player):
    # finds all possible moves and the possible board after-states
    # inputs are the BG-board, the dices rolled and which player is up
    # outputs the possible pair of moves (if they exists) and their after-states

    moves = []
    boards = []

    # try using the first dice, then the second dice
    possible_first_moves = legal_move(board, dice[0], player)
    for m1 in possible_first_moves:
        temp_board = update_board(board,m1,player)
        possible_second_moves = legal_move(temp_board, dice[1], player)
        for m2 in possible_second_moves:
            moves.append(np.array([m1,m2]))
            boards.append(update_board(temp_board, m2, player))
        
    if dice[0] != dice[1]:
        # try using the second dice, then the first one
        possible_first_moves = legal_move(board, dice[1], player)
        for m1 in possible_first_moves:
            temp_board = update_board(board,m1,player)
            possible_second_moves = legal_move(temp_board, dice[0], player)
            for m2 in possible_second_moves:
                moves.append(np.array([m1,m2]))
                boards.append(update_board(temp_board, m2, player))
            
    # if there's no pair of moves available, allow one move:
    if len(moves)==0: 
        # first dice:
        possible_first_moves = legal_move(board, dice[0], player)
        for m in possible_first_moves:
            moves.append(np.array([m]))
            boards.append(update_board(temp_board, m, player))
            
        # second dice:
        if dice[0] != dice[1]:
            possible_first_moves = legal_move(board, dice[1], player)
            for m in possible_first_moves:
                moves.append(np.array([m]))
                boards.append(update_board(temp_board, m, player))
            
    return moves, boards 

def update_board(board, move, player):
    # updates the board
    # inputs are some board, one move and the player
    # outputs the updated board
    board_to_update = np.copy(board) 

    # if the move is there
    if len(move) > 0:
        startPip = move[0]
        endPip = move[1]
        
        # moving the dead piece if the move kills a piece
        kill = board_to_update[endPip] == (-1*player)
        
        if kill:
            board_to_update[endPip] = 0
            jail = 25 + (player == 1)
            board_to_update[jail] = board_to_update[jail] - player
        
        board_to_update[startPip] = board_to_update[startPip] - 1*player
        board_to_update[endPip] = board_to_update[endPip] + player

    return board_to_update

def winner_gains(winner, board):
    points = 1

    if winner == 1 and board[28] == 0:
        points = 2
        if sum(board[1:13]) < 0:
            points = 3
    elif winner == -1 and board[27] == 0:
        points = 2
        if sum(board[13:25]) > 0:
            points = 3
    
    return points
    
def play_a_game(winners, beginners):
    board = init_board() # initialize the board
    player = np.random.randint(2)*2 - 1 # which player begins?
    beginner = player
    
    # play on
    while not game_over(board):
        # roll dice
        dice = roll_dice()
            
        # make a move (2 moves if the same number appears on the dice)
        for _ in range(1+int(dice[0] == dice[1])):
            board_copy = np.copy(board) 

            possible_moves = legal_moves(board_copy, dice, player)
            
            move = []
            if len(possible_moves[0]) != 0:
                move = random.choice(possible_moves[0])
                
            # update the board
            if len(move) != 0:
                for m in move:
                    board = update_board(board, m, player)
                                
                
        # players take turns 
        player = -player

    # if game_over(board):
    #     print("final move, dice and board:")
    #     print(move)
    #     print(dice)
    #     pretty_print(board)
        
    # updates of statistics
    if beginner == 1:
        beginners["orange"][0] += 1
    else:
        beginners["blue"][0] += 1

    winner = -1*player
    points = winner_gains(winner, board) 
    if winner == 1:
        winners["orange"][0] += 1
        if beginner == 1:
            beginners["orange"][1] += 1
        if points == 1:
            winners["orange"][1] += 1
        elif points == 2:
            winners["orange"][2] += 1
        else:
            winners["orange"][3] += 1
    else:
        winners["blue"][0] += 1
        if beginner == -1:
            beginners["blue"][1] += 1
        if points == 1:
            winners["blue"][1] += 1
        elif points == 2:
            winners["blue"][2] += 1
        else:
            winners["blue"][3] += 1       
       
    # return the winner
    return winners, beginners
    
def main():
    startTime = time.time()

    nGames = 50
    winners = {"orange": [0, 0, 0, 0], "blue": [0, 0, 0, 0]} # Collecting stats of the games
    beginners = {"orange": [0, 0], "blue": [0,0]}
    for _ in range(nGames):
        winners, beginners= play_a_game(winners, beginners)

    print(f"Out of {nGames} games between blue and orange:\n")
    print(f"Player orange won {winners['orange'][0]} times and won " \
          f"{winners['orange'][1] + winners['orange'][2]*2 + winners['orange'][3]*3} points.")
    print(f"Player blue won {winners['blue'][0]} times and won " \
          f"{winners['blue'][1] + winners['blue'][2]*2 + winners['blue'][3]*3} points.\n")
    print(f"Player orange won {winners['orange'][1]} 1-point plays, {winners['orange'][2]} 2-point plays " \
          f"and {winners['orange'][3]} 3-point plays.")
    print(f"Player blue won {winners['blue'][1]} 1-point plays, {winners['blue'][2]} 2-point plays " \
          f"and {winners['blue'][3]} 3-point plays.\n")
    print(f"Player orange started {beginners['orange'][0]} times and won " \
          f"{100*beginners['orange'][1]/beginners['orange'][0]}% of started games.")
    print(f"Player blue started {beginners['blue'][0]} times and won " \
          f"{100*beginners['blue'][1]/beginners['blue'][0]}% of started games.\n")

    runTime = time.time()-startTime
    print("runTime:", runTime)
    print("average time:", runTime/nGames)
    
if __name__ == '__main__':
    main()