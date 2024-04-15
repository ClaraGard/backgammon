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
from numba import jit

class Player:
    def __init__(self, name, id, jail, passed, start, goal, reverse_sort):
        self.name = name
        self.id = id
        self.jail = jail
        self.passed = passed
        self.start = start
        self.goal = goal
        self.reverse_sort = reverse_sort
        self.opponent :Player = None

BLACK = Player("BLACK", 1, 25, 27, -1, 24, False)
WHITE = Player("WHITE", -1, 24, 26, 24, -1, True)
BLACK.opponent = WHITE
WHITE.opponent = BLACK

class BackGammon:
    def __init__(self, board=None, checkers = None):
        if board is not None:
            assert checkers is not None
            self.board = copy.deepcopy(board)
            self.checkers = copy.deepcopy(checkers)
        else:
            self.init_board()

    def init_board(self):
        # initializes the game board
        self.checkers = {}
        self.board = [0] * 28
        self.board[0] = 2
        self.board[11] = 5
        self.board[16] = 3
        self.board[18] = 5
        self.checkers[BLACK.id] = [0, 11, 16, 18]
        self.board[5] = -5
        self.board[7] = -3
        self.board[12] = -5
        self.board[23] = -2
        self.checkers[WHITE.id] = [23, 12, 7, 5]

    def game_over(self):
    # returns True if the game is over   
        return self.board[BLACK.passed] == 15*BLACK.id or self.board[WHITE.passed] == 15*WHITE.id
    
    def score(self):
        if self.game_over():
            if self.board[BLACK.passed] == 15*BLACK.id:
                return 1
            return 0
        return 0.5

    def pretty_print(self):
        print(self.board[0:12])
        print(self.board[23:11:-1])
        print(self.board[24:28])
        print(self.checkers)
        print("")

    @staticmethod
    def roll_dice():
        # rolls the dice
        return np.random.randint(1, 7, 2)

    def can_go(self, player :Player, destination):
        return -self.board[destination]*player.id < 2

    def is_bearing_off(self, player :Player):
        if player == WHITE:
            return self.checkers[WHITE.id][0] < 6
        return self.checkers[BLACK.id][0] > 17

    def has_checkers_in_jail(self, player :Player):
        return self.board[player.jail]*player.id > 0

    def has_checker_in_case(self, player: Player, case):
        return self.board[case]*player.id > 0

    def can_win(self, player :Player, die):
        return self.is_bearing_off(player) and self.has_checker_in_case(player, player.goal + (-die * player.id))

    def has_mandatory_action(self, player :Player, die):
        return self.has_checkers_in_jail(player) or self.can_win(player, die)

    def get_jail_move(self, player :Player, die):
        destination = player.start + die * player.id
        if self.can_go(player, destination):
            return [player.jail, destination]
        return None

    def get_bearing_off_moves(self, player :Player, die):
        #if there is a checker exactly on the die number
        if self.can_win(player, die):
            return self.get_trivial_win_move(player, die)
        return self.get_other_win_move(player, die)
    
    def get_trivial_win_move(self, player :Player, die):
        return [(-player.id*die)+player.goal, player.passed]
    
    def get_other_win_move(self, player :Player, die):
        if ((self.checkers[player.id][0] + player.id * die) -player.goal)*player.id >= 0:
            return [self.checkers[player.id][0], player.passed]
        return None
    
    def get_other_moves(self, player :Player, die):
        possible_moves = []
        # finding all other legal options
        if self.can_win(player, die):
            return []
        for start in self.checkers[player.id]:
            destination = start+die*player.id
            if destination >= 0 and destination < 24:
                if self.can_go(player, destination):
                    possible_moves.append([start, destination])
        return possible_moves


    def legal_move(self, player :Player, die):
        # finds legal moves (from, to) for a board and one dice, returns empty list if none
        if self.has_checkers_in_jail(player): 
            return [self.get_jail_move(player, die)]
        if self.is_bearing_off(player):
            bearing_off_move = self.get_bearing_off_moves(player, die)
            if bearing_off_move:
                return [bearing_off_move]
        return self.get_other_moves(player, die)

    def play(self, player :Player, move):
        if not move: return
        start = move[0]
        dest = move[1]
        # moving the dead piece if the move kills a piece
        if self.board[dest] == (player.opponent.id):
            self.board[player.opponent.jail] += player.opponent.id
            self.board[dest] = 0
            self.checkers[-player.id].remove(dest)

        self.board[start] -= player.id
        if self.board[start] == 0 and start < 24:
            self.checkers[player.id].remove(start)

        if not self.has_checker_in_case(player, dest) and dest < 24:
            self.checkers[player.id].append(dest)
            self.checkers[player.id].sort(reverse = player.reverse_sort)
        
        self.board[dest] += player.id
        npboard = np.array(self.board[0:24])
        npboard2 = np.array(self.board)
        bc = np.where(npboard>0)[0]
        wc = np.sort(np.where(npboard<0)[0])[::-1]
        #print(str(bc) + str(self.checkers[BLACK.id]) +"\n" + str(wc) + str(self.checkers[WHITE.id]) +"\n"+ str(self.board) + "\n"+ str(move))
        assert sum(npboard2[npboard2 > 0]) == 15 and sum(npboard2[npboard2 < 0]) == -15, \
        str(bc) + str(self.checkers[BLACK.id]) +"\n" + str(wc) + str(self.checkers[WHITE.id]) +"\n"+ str(self.board) + "\n"+ str(move)
        assert bc.tolist() == self.checkers[BLACK.id] and wc.tolist() == self.checkers[WHITE.id], \
        str(bc) + str(self.checkers[BLACK.id]) +"\n" + str(wc) + str(self.checkers[WHITE.id]) +"\n"+ str(self.board) + "\n"+ str(move)


    def legal_moves(self, player :Player, dice):
        moves = []
        bearing_off_move = self.get_bearing_off_moves(player, dice[0])
        if self.has_checkers_in_jail(player):
            jail_move = self.get_jail_move(player, dice[0])
            if jail_move is not None:
                game_after_move = BackGammon(self.board, self.checkers)
                game_after_move.play(player, jail_move)
                for lm in game_after_move.legal_move(player, dice[1]):
                    moves.append([jail_move, lm])
        #canwin
        elif bearing_off_move:
            game_after_move = BackGammon(self.board, self.checkers)
            game_after_move.play(player, bearing_off_move)
            if not game_after_move.game_over():
                for lm in game_after_move.legal_move(player, dice[1]):
                    moves.append([bearing_off_move, lm])
            else:
                moves.append([bearing_off_move, None])
        else:
            other_moves = self.get_other_moves(player, dice[0])
            other_moves2 = self.get_other_moves(player, dice[1])
            for m in other_moves:
                game_after_move = BackGammon(self.board, self.checkers)
                game_after_move.play(player, m)
                destination = m[1]+dice[1]*player.id
                bearing_off_move = game_after_move.get_bearing_off_moves(player, dice[1])
                if bearing_off_move:
                    moves.append([m, bearing_off_move])
                elif destination >= 0 and destination < 24 and game_after_move.can_go(player, destination):
                    moves.append([m, [m[1], destination]])
                if not bearing_off_move:
                    for m2 in other_moves2:
                        if game_after_move.has_checker_in_case(player, m2[0]):
                            moves.append([m, m2])

        if dice[0] != dice[1]:
            bearing_off_move = self.get_bearing_off_moves(player, dice[1])
            if self.has_checkers_in_jail(player):
                jail_move = self.get_jail_move(player, dice[1])
                if jail_move is not None:
                    game_after_move = BackGammon(self.board, self.checkers)
                    game_after_move.play(player, jail_move)
                    for lm in game_after_move.legal_move(player, dice[0]):
                        moves.append([jail_move, lm])
            #canwin
            elif bearing_off_move:
                game_after_move = BackGammon(self.board, self.checkers)
                game_after_move.play(player, bearing_off_move)
                if not game_after_move.game_over():
                    for lm in game_after_move.legal_move(player, dice[0]):
                        moves.append([bearing_off_move, lm])
                else:
                    moves.append([bearing_off_move, None])
            other_moves = self.get_other_moves(player, dice[1])
            for m in other_moves:
                game_after_move = BackGammon(self.board, self.checkers)
                game_after_move.play(player, m)
                destination = m[1]+dice[1]*player.id
                bearing_off_move = game_after_move.get_bearing_off_moves(player, dice[1])
                if bearing_off_move:
                    moves.append([m, bearing_off_move])
                elif destination >= 0 and destination < 24 and game_after_move.can_go(player, destination):
                    moves.append([m, [m[1], destination]])
        return moves
    
def play_a_game(winners, nb_legal_moves = {}):
    # simulate a game with randomized moves
    game = BackGammon()
    player = BLACK
    dice_rolls = 0
    while not game.game_over():
        dice = BackGammon.roll_dice()
        dice_rolls += 1
        #print("dice roll", dice)
        #print(game.board[BLACK.passed], game.board[WHITE.passed])
        # make a move (2 moves if the same number appears on the dice)
        for _ in range(1 + int(dice[0] == dice[1])):
            if game.game_over(): break
            possible_moves = game.legal_moves(player, dice)
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
            print(possible_moves)
            if len(possible_moves) != 0:
                move = random.choice(possible_moves)
                #print(player.name, "plays", move)
                for m in move:
                    #print(player.name, "plays", m, flush=True)
                    game.play(player, m)
            #game.pretty_print()

        # players take turns 
        player = player.opponent

    # if game_over(board):
    #     print("final move, dice and board:")
    #     print(move)
    #     print(dice)
    #     pretty_print(board)
        
    # updates of statistics
    winner = player.opponent
    points = game.score()
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



