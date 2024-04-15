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

def legal_moves2(board, dice, player):
    # Essaye de faire les deux à la fois pour gagner du temps.
    # Situation 1 : aucun pip en prison ne peut sortir
    # Situation 2 : un pip en prison qui peut sortir. On commence par celui-là
    #      puis on appelle legal_move sur l'autre dé.
    # Situation 3 : finale : sum(board[7:25] > 0) == 0 
    #       alors on sort ce que l'on peut sortir
    # Situation 4 : pré-finale : sum(board[7:25] > 0) == 1
    #       on regarde si on peut jouer d'abord le seul pip, puis legal_move sur l'autre dé
    # Situation 5 : classique. On calcule les pips qui peuvent jouer le dé 1, puis
    #       ceux qui peuvent jouer le dé 2.
    #       On retourne alors tous les coups produit où ce ne sont pas les mêmes, ou bien
    #       lorsqu'il y a au moins 2 jetons sur le même pip de départ
    #       On rajoute enfin le cas où on déplace le même jeton sur les deux dés.
    moves = []
        
    if player == 1:
        # dead piece, needs to be brought back to life
        if board[25] >= 1: # S'il y a au moins un pion à sortir
            return(legal_moves(board, dice, player))
        if sum(board[7:25] > 0) <= 1: # finale ou pre finale
            return legal_moves(board,dice,player)
        # On est donc dans la situation classique où il y a au moins deux pions
        # dans la zone de mouvement.
        # first dice:
        possible_first_moves = legal_move(board, dice[0], player)
        possible_second_moves = legal_move(board, dice[1], player)
        # Il y aura d'autres moves si on bouge deux fois le même pion
        # et on enlève du produit cartésien si c'est le même pion au début
        if len(possible_first_moves) == 0:
            return(legal_moves(board, dice, player))
        if len(possible_second_moves) == 0:
            return(legal_moves(board, dice, player))
        # cas ou faire un des deux dés ouvre une possibilité auparavant inexistante pour l'autre dé
        
        if dice[0] != dice[1]:
            # création du produit cartésien, possible car mouvement commute
            for m1 in possible_first_moves:
                for m2 in possible_second_moves:
                    if m1[0] != m2[0] or board[m1[0]] >= 2:
                        moves.append([m1, m2])
            for m1 in possible_first_moves:
                if board[m1[1]] < 1: # nouvel endroit car sinon mouv déjà créer par legal moves
                    end_pip = m1[1] - dice[1]
                    if end_pip > 0:
                        if board[end_pip] > -2:
                            moves.append([m1, [m1[1], end_pip]])
            for m1 in possible_second_moves:
                if board[m1[1]] < 1:
                    end_pip = m1[1] - dice[0]
                    if end_pip > 0:
                        if board[end_pip] > -2:
                            moves.append([m1, [m1[1], end_pip]])
        # produit parfois quelques résultats équivalents (mais pas redondants)
        # redondant : faire 8 -> 4 puis 6 -> 3 et faire 6 -> 3 puis 8 -> 4
        # equivalent : donne le meme board mais les coups sont différents
        else: # produit cartésien différent (dés: 3, 4. 6 -> 3, 8 -> 4 et 8 -> 4, 6 -> 3 différent, mais pas si dés égaux)
            n = len(possible_first_moves)
            for i in range(n):
                for j in range(i, n): #  
                    m1 = possible_first_moves[i]
                    m2 = possible_first_moves[j]
                    if m1[0] != m2[0] or board[m1[0]] >= 2:
                        moves.append([m1, m2])
            for m1 in possible_first_moves:
                if board[m1[1]] < 1:
                    end_pip = m1[1] - dice[1]
                    if end_pip > 0:
                        if board[end_pip] > -2:
                            moves.append([m1, [m1[1], end_pip]])

    
    if player == -1:
        # dead piece, needs to be brought back to life
        if board[26] <= -1: # S'il y a au moins un pion à sortir
            return(legal_moves(board,dice,player))
        if sum(board[1:19] < 0) <= 1:
            return legal_moves(board,dice,player)
        # On est donc dans la situation classique où il y a au moins deux pions
        # dans la zone de mouvement.
        # first dice:
        possible_first_moves = legal_move(board, dice[0], player)
        possible_second_moves = legal_move(board, dice[1], player)
        # Il y aura d'autres moves si on bouge deux fois le même pion
        # et on enlève du produit cartésien si c'est le même pion au début
        if len(possible_first_moves) == 0:
            return(legal_moves(board, dice, player))
        if len(possible_second_moves) == 0:
            return(legal_moves(board, dice, player))
        
        if dice[0] != dice[1]:
            for m1 in possible_first_moves:
                for m2 in possible_second_moves:
                    if m1[0] != m2[0] or board[m1[0]] <= -2:
                        moves.append([m1, m2])
            for m1 in possible_first_moves:
                if board[m1[1]] > -1:
                    end_pip = m1[1] + dice[1]
                    if end_pip < 25:
                        if board[end_pip] < 2:
                            moves.append([m1, [m1[1], end_pip]])
            for m1 in possible_second_moves:
                if board[m1[1]] >- 1:
                    end_pip = m1[1] + dice[0]
                    if end_pip < 25:
                        if board[end_pip] <2:
                            moves.append([m1, [m1[1], end_pip]])
        else:
            n = len(possible_first_moves)
            for i in range(n):
                for j in range(i, n):
                    m1 = possible_first_moves[i]
                    m2 = possible_first_moves[j]
                    if m1[0] != m2[0] or board[m1[0]] <= -2:
                        moves.append([m1, m2])
            for m1 in possible_first_moves:
                if board[m1[1]] >- 1:
                    end_pip = m1[1] + dice[1]
                    if end_pip < 25:
                        if board[end_pip] < 2:
                            moves.append([m1, [m1[1], end_pip]])

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
    # distribute points to winner according to status of final board.
    if winner == 1:
        points = 1
        if board[28] == 0:
            points = 2
            if sum(board[1:13]) < 0:
                points = 3
    else:
        points = -1
        if board[27] == 0:
            points = -2
            if sum(board[13:25]) > 0:
                points = -3
    
    return points
    
def play_a_game(winners, nb_legal_moves = {}):
    # simulate a game with randomized moves

    board = init_board()
    player = 1
    dice_rolls = 0

    while not game_over(board):
        dice = roll_dice()
        dice_rolls += 1
            
        # make a move (2 moves if the same number appears on the dice)
        for _ in range(1 + int(dice[0] == dice[1])):
            board_copy = np.copy(board) 

            possible_moves = legal_moves(board_copy, dice, player)
            # pm2 = legal_moves(board_copy, dice, player)
            # if not compare(possible_moves, pm2):
            #     print(f"C'est au coup {dice_rolls}, les des ont donné {dice}\n")
            #     pretty_print(board)
            #     print(possible_moves)
            #     print(pm2)
            #     print("\n\n")

            # Study of the distribution of number of legal moves
            # nb_moves = len(possible_moves)
            # if nb_moves >= 170:
            #     print(dice)
            #     print(player)
            #     pretty_print(board_copy)

            # if nb_moves not in nb_legal_moves.keys():
            #     nb_legal_moves[nb_moves] = 1
            # else:
            #     nb_legal_moves[nb_moves] += 1

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
    winner = -player
    points = winner_gains(winner, board) 
    if winner == 1:
        winners["orange"][0] += 1
        if points == 1:
            winners["orange"][1] += 1
        elif points == 2:
            winners["orange"][2] += 1
        else:
            winners["orange"][3] += 1
    else:
        winners["blue"][0] += 1
        if points == -1:
            winners["blue"][1] += 1
        elif points == -2:
            winners["blue"][2] += 1
        else:
            winners["blue"][3] += 1       
       
    return winners, dice_rolls/2, nb_legal_moves

def getboard_code(seen_boards, board, move):
    strboard = str(board)+str(move)
    if not strboard in seen_boards:
        seen_boards[strboard] = len(seen_boards)
    board_number = seen_boards[strboard]
    return board_number
    
def main():
    games = 100

    winners = {"orange": [0, 0, 0, 0], "blue": [0, 0, 0, 0]} # Collecting stats of the games
    mean_dice_rolls = 0
    mean_run_time = 0
    nb_legal_moves = {}
    
    for i in range(games):
        print(i)
        startTime = time.time()

        winners, dice_rolls, nb_legal_moves = play_a_game(winners, nb_legal_moves)
        mean_dice_rolls += dice_rolls

        runTime = time.time() - startTime
        mean_run_time += runTime

    mean_dice_rolls = mean_dice_rolls/games
    mean_run_time = mean_run_time/games

    # Plotting the distribution of the number of legal moves
    # nb_legal_moves = dict(sorted(nb_legal_moves.items()))
    # max_key = max(nb_legal_moves.keys())
    # completed_dict = {i: nb_legal_moves.get(i, 0) for i in range(max_key + 1)}
    
    # plt.bar(completed_dict.keys(), completed_dict.values(), color = 'blue')
    # plt.xlabel('Number of legal moves')
    # plt.ylabel('Distribution')
    # plt.title(f'Distribution of the number of legal moves over {games} games (about {mean_dice_rolls*games} turns).')
    # plt.grid(True)
    # plt.show()

    print(f"Out of {games} games between blue and orange, with orange always beginning:\n")
    print(f"Player orange won {winners['orange'][0]} times ({round(100*winners['orange'][0]/games, 2)}%) and won " \
          f"{winners['orange'][1] + winners['orange'][2]*2 + winners['orange'][3]*3} points.")
    print(f"Player blue won {winners['blue'][0]} times ({round(100*winners['blue'][0]/games, 2)}%) and won " \
          f"{winners['blue'][1] + winners['blue'][2]*2 + winners['blue'][3]*3} points.\n")
    print(f"Player orange won {winners['orange'][1]} 1-point plays, {winners['orange'][2]} 2-point plays " \
          f"and {winners['orange'][3]} 3-point plays.")
    print(f"Player blue won {winners['blue'][1]} 1-point plays, {winners['blue'][2]} 2-point plays " \
          f"and {winners['blue'][3]} 3-point plays.\n")
    print(f"On average, a game last {round(mean_run_time, 3)}s and is played in {round(mean_dice_rolls, 2)} dice rolls.\n")

# def compare(L1,L2):
#     for x in L1:
#         ok=False
#         for y in L2:
#             if len(x)==len(y):
#                 if len(x)==1:
#                     if list(x[0])==list(y[0]):
#                         ok=True
#                 else:
#                     cx1,cx2=list(x[0]), list(x[1])
#                     cy1,cy2=list(y[0]), list(y[1])
#                     if cx1==cy1 and cx2==cy2:
#                         ok=True
#                     if cx1==cy2 and cx2==cy1:
#                         ok=True
#         if not ok:
#             print(f"{x} n'est pas trouvé dans la deuxième liste")
#             return False
#     for x in L2:
#         ok=False
#         for y in L1:
#             if len(x)==len(y):
#                 if len(x)==1:
#                     if list(x[0])==list(y[0]):
#                         ok=True
#                 else:
#                     cx1,cx2=list(x[0]), list(x[1])
#                     cy1,cy2=list(y[0]), list(y[1])
#                     if cx1==cy1 and cx2==cy2:
#                         ok=True
#                     if cx1==cy2 and cx2==cy1:
#                         ok=True
#         if not ok:
#             print(f"{x} n'est pas trouvé dans la première liste")
#             return False
#     return True

if __name__ == '__main__':
    main()



