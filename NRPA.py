import Backgammon
import math
import random
import copy
import hashlib
import time

# NRPA 
# missing incrementation of visited_boards + points + play_game fonction

def code(board, move, player):
    board_copy = copy.deepcopy(board)
    if len(move) != 0:
        for m in move:
            board_copy = Backgammon.update_board(board_copy, m, player)
    text = ''.join(map(str, board_copy))+str(player)

    return text

def randomMove(board, dice, policy, player):
    moves = Backgammon.legal_moves(board, dice, player)[0]
    z = 0.0
    for m in moves:
        code_value = code(board, m, player)
        if policy.get(code_value) == None:
            policy[code_value] = 0.0
        z = z + math.exp(policy[code_value])
    stop = random.random()*z # chooses a move randomly with non uniform probability
    sum = 0.0
    for m in moves:
        sum = sum + math.exp(policy[code_value])
        if sum >= stop:
            return m
    return []
        
def playout (board, dice, policy, player):
    print("playout")
    board_copy = copy.deepcopy(board)
    sequence = []
    while not Backgammon.game_over(board_copy):
        move = randomMove(board_copy, dice, policy, player)
        sequence.append(move)
        if len(move) != 0:
            for m in move:
                board_copy = Backgammon.update_board(board_copy, m, player)
        player *= -1
        dice = Backgammon.roll_dice()
    score = Backgammon.winner_gains(-player, board_copy)
    print("playout finish")
    return score, sequence

def adapt(policy, state, sequence, dice, player, alpha = 1):
    print("adapt")
    board = copy.deepcopy(state)
    polp = copy.deepcopy(policy)
    print("sequence length", len(sequence))
    for best in sequence:
        best_code = code(board, best, player)
        if not best_code in polp:
            polp[best_code] = 0
        polp[best_code] = polp[best_code] + alpha
        moves = Backgammon.legal_moves(board, dice, player)[0]
        #we're doing a lot of illegal moves here since we don't reroll the dice
        print("legal moves length", len(moves))
        z = 0.0
        for m in moves:
            code_value = code(board, m, player)
            if policy.get(code_value) == None:
                policy[code_value] = 0.0
            z = z + math.exp(policy[code_value])
        for m in moves:
            code_value = code(board, m, player)
            if polp.get(code_value) == None:
                polp[code_value] = 0.0
            polp[code_value] -= alpha*math.exp(policy[code_value])/z
        if len(best) != 0:
            for m in best:
                board = Backgammon.update_board(board, m, player)
    print("adapt finish")
    return polp

def nrpa(level, policy, board, player, dice, N = 10):
    if level == 0:
        return playout(board, dice, policy, player)
    best = -1000000.0
    seq = []
    for i in range(N):
        print(i)
        pol = copy.deepcopy(policy)
        sc, s = nrpa(level - 1, pol, board, player, dice)
        if sc > best: # this need to be changed also
            best = sc
            seq = s
        policy = adapt(policy, board, seq, dice, player)
    print("policy length", len(policy))
    return best, seq

startTime = time.time()
board = Backgammon.init_board()
player = random.randint(0,1)*2-1
dice = Backgammon.roll_dice()
print(dice)
sc, s = nrpa(2, {}, board, player, dice)
print(sc, s)
runTime = time.time()-startTime
print("runTime:", runTime)

# Choisir MaxLegalMoves:
# faire 1000 parties aléatoires, à chaque fois je prends le max du nombre de coups légaux possibles
# faire histogram des valeurs pour vérifier que ajouter 10% à la fin ca crée une valeur sup pas trop grande 
# Pour MaxCodeLegalMoves c'est facile et on espère que ce soit pas trop grand.
