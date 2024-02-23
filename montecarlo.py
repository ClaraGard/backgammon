import Backgammon
import math
import random
import copy
import hashlib

# NRPA 
# missing incrementation of visited_boards + points + play_game fonction

def code(board, move, player):
    board_copy = copy.deepcopy(board)
    board_copy = Backgammon.update_board(board_copy, move, player)
    text = ''.join(map(str, board_copy))

    sha1 = hashlib.sha1()
    sha1.update(text.encode('utf-8'))

    return sha1.hexdigest()

def randomMove(board, dice, policy, player):
    moves = Backgammon.legal_moves(board, dice, player)
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
        
def playout (board, dice, policy, player):
    board_copy = copy.deepcopy(board)
    while not Backgammon.game_over(board_copy):
        move = randomMove(board, dice, policy, player)
        board_copy = Backgammon.update_board(board_copy, move, player)
        player *= -1
    return board_copy

def adapt(policy, sequence, dice, player, alpha = 1):
    board = Backgammon.init_board()
    polp = copy.deepcopy(policy)
    for best in sequence:
        moves = Backgammon.legal_moves(board, dice, player)
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
        code_value = code(board, best, player)
        polp[code_value] += alpha
        board = Backgammon.update_board(board, best, player)
    return polp

def nrpa(level, policy, player, dice, N = 100):
    if level == 0:
        return playout(Backgammon.init_board(), dice, policy, player)
    best = -1000000.0
    seq = []
    for _ in range(N):
        pol = copy.deepcopy(policy)
        sc, s = nrpa(level - 1, pol, player, dice)
        if sc > best: # this need to be changed also
            best = sc
            seq = s
        policy = adapt(policy, seq, dice, player)
    return best, seq

player = random.randint(0,1)*2-1
dice = Backgammon.roll_dice()

# Choisir MaxLegalMoves:
# faire 1000 parties aléatoires, à chaque fois je prends le max du nombre de coups légaux possibles
# faire histogram des valeurs pour vérifier que ajouter 10% à la fin ca crée une valeur sup pas trop grande 
# Pour MaxCodeLegalMoves c'est facile et on espère que ce soit pas trop grand.