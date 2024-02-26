#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# https://github.com/weekend37/Backgammon/blob/master/Backgammon.py
"""
Backgammon interface
Run this program to play a game of Backgammon
"""
import numpy as np
import time
import random
import copy

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
    
    return np.random.randint(1, 7, 2)

def game_over(board):
    # returns True if the game is over   
     
    return board[27] == 15 or board[28] == -15
    
def pretty_print(board):
    string = str(np.array2string(board[1:13]) + '\n' +
                 np.array2string(board[24:12:-1]) + '\n' +
                 np.array2string(board[25:29]))
    print("board: \n", string)
      
def legal_move(board, dice, player):
    # finds legal moves (from, to) for a board and one dice, returns empty list if none

    possible_moves = []

    if player == 1:
        # dead piece, needs to be brought back to life
        if board[25] > 0: 
            start_pip = 25 - dice
            if board[start_pip] > -2:
                possible_moves.append(np.array([25, start_pip]))
                
        # no dead pieces        
        else:
            # adding options if player is bearing off
            if sum(board[7:25] > 0) == 0: 
                if (board[dice] > 0):
                    possible_moves.append(np.array([dice, 27]))
                    
                elif not game_over(board): # smá fix
                    # everybody's past the dice throw?
                    s = np.max(np.where(board[1:7] > 0)[0] + 1)
                    if s < dice:
                        possible_moves.append(np.array([s, 27]))
                    
            possible_start_pips = np.where(board[0:25] > 0)[0]

            # finding all other legal options
            for s in possible_start_pips:
                end_pip = s-dice
                if end_pip > 0:
                    if board[end_pip] > -2:
                        possible_moves.append(np.array([s, end_pip]))
                        
    elif player == -1:
        # dead piece, needs to be brought back to life
        if board[26] < 0: 
            start_pip = dice
            if board[start_pip] < 2:
                possible_moves.append(np.array([26, start_pip]))
                
        # no dead pieces       
        else:
            # adding options if player is bearing off
            if sum(board[1:19] < 0) == 0: 
                if (board[25 - dice] < 0):
                    possible_moves.append(np.array([25 - dice, 28]))
                elif not game_over(board): # smá fix
                    # everybody's past the dice throw?
                    s = np.min(np.where(board[19:25] < 0)[0])
                    if (6 - s) < dice:
                        possible_moves.append(np.array([19 + s, 28]))

            # finding all other legal options
            possible_start_pips = np.where(board[0:25] < 0)[0]
            for s in possible_start_pips:
                end_pip = s + dice
                if end_pip < 25:
                    if board[end_pip] < 2:
                        possible_moves.append(np.array([s, end_pip]))
        
    return possible_moves

def legal_moves(board, dice, player):
    # return all possible pair of legal moves if there exists, empty list otherwise

    moves = []

    # try using the first dice, then the second dice
    possible_first_moves = legal_move(board, dice[0], player)
    for m1 in possible_first_moves:
        temp_board = update_board(board, m1, player)
        possible_second_moves = legal_move(temp_board, dice[1], player)
        for m2 in possible_second_moves:
            moves.append(np.array([m1, m2]))
        
    if dice[0] != dice[1]:
        # try using the second dice, then the first one
        possible_first_moves = legal_move(board, dice[1], player)
        for m1 in possible_first_moves:
            temp_board = update_board(board, m1, player)
            possible_second_moves = legal_move(temp_board, dice[0], player)
            for m2 in possible_second_moves:
                moves.append(np.array([m1, m2]))
            
    # if there's no pair of moves available, allow one move:
    if len(moves) == 0: 
        # first dice:
        possible_first_moves = legal_move(board, dice[0], player)
        for m in possible_first_moves:
            moves.append(np.array([m]))
            
        # second dice:
        if dice[0] != dice[1]:
            possible_first_moves = legal_move(board, dice[1], player)
            for m in possible_first_moves:
                moves.append(np.array([m]))
            
    return moves

def update_board(board, move, player):
    # updates the board (play a move)

    board_to_update = copy.deepcopy(board) 

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
    # simulate a game with randomized moves

    board = init_board()
    player = np.random.randint(2)*2 - 1
    beginner = player
    dice_rolls = 0

    while not game_over(board):
        dice = roll_dice()
        dice_rolls += 1
            
        # make a move (2 moves if the same number appears on the dice)
        for _ in range(1 + int(dice[0] == dice[1])):
            board_copy = np.copy(board) 

            possible_moves = legal_moves(board_copy, dice, player)
            if len(possible_moves) != 0:
                move = random.choice(possible_moves)
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

    winner = -player
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
       
    return winners, beginners, dice_rolls//2
    
def main():
    games = 10000

    winners = {"orange": [0, 0, 0, 0], "blue": [0, 0, 0, 0]} # Collecting stats of the games
    beginners = {"orange": [0, 0], "blue": [0,0]}
    mean_dice_rolls = 0
    mean_run_time = 0
    
    for _ in range(games):
        startTime = time.time()

        winners, beginners, dice_rolls = play_a_game(winners, beginners)
        mean_dice_rolls += dice_rolls

        runTime = time.time() - startTime
        mean_run_time += runTime

    mean_dice_rolls = mean_dice_rolls//games
    mean_run_time = mean_run_time/games

    print(f"Out of {games} games between blue and orange:\n")
    print(f"Player orange won {winners['orange'][0]} times ({round(100*winners['orange'][0]/games, 2)}%) and won " \
          f"{winners['orange'][1] + winners['orange'][2]*2 + winners['orange'][3]*3} points.")
    print(f"Player blue won {winners['blue'][0]} times ({round(100*winners['blue'][0]/games, 2)}%) and won " \
          f"{winners['blue'][1] + winners['blue'][2]*2 + winners['blue'][3]*3} points.\n")
    print(f"Player orange won {winners['orange'][1]} 1-point plays, {winners['orange'][2]} 2-point plays " \
          f"and {winners['orange'][3]} 3-point plays.")
    print(f"Player blue won {winners['blue'][1]} 1-point plays, {winners['blue'][2]} 2-point plays " \
          f"and {winners['blue'][3]} 3-point plays.\n")
    print(f"Player orange started {beginners['orange'][0]} times ({round(100*beginners['orange'][0]/games, 2)}%) and won " \
          f"{round(100*beginners['orange'][1]/beginners['orange'][0], 2)}% of started games.")
    print(f"Player blue started {beginners['blue'][0]} times ({round(100*beginners['blue'][0]/games, 2)}%) and won " \
          f"{round(100*beginners['blue'][1]/beginners['blue'][0], 2)}% of started games.\n")
    print(f"On average, a game last {round(mean_run_time, 3)}s and is played in {mean_dice_rolls} dice rolls.\n")
    
if __name__ == '__main__':
    main()