import copy
import random
import math

from Backgammon import *


class Policy (object):
    def __init__ (self):
        self.dict = {}
 
    def get (self, code):
        if not code in self.dict:
            self.dict[code] = {}
        w = self.dict[code]
        return w
 
    def put (self, code, w):
        self.dict [code] = w 

seen_boards = {}
Table = {}

def add (board_number):
    nplayouts = {}
    nwins = {}
    Table [board_number] = [0, nplayouts, nwins]

def look (board_number):
    return Table.get(board_number, None)

def getboard_code(board):
    strboard = str(board)
    if not strboard in seen_boards:
        seen_boards[str(board)] = len(seen_boards)
    board_number = seen_boards[str(board)]
    return board_number

def code(dice, move):
    if len(move) == 2:
        code_move = f"{dice[0]}{dice[1]}{move[0][1]}{move[1][1]}"
    elif len(move) == 3:
        code_move = f"{dice[0]}{dice[1]}{move[0][1]}{move[1][1]}{move[2][1]}"
    elif len(move) == 4:
        code_move = f"{dice[0]}{dice[1]}{move[0][1]}{move[1][1]}{move[2][1]}{move[3][1]}"
    else:
        code_move = f"{dice[0]}{dice[1]}{move[0][1]}"
    return code_move


def playout (board, dice, player, policy :Policy):
    p = []
    d = []
    while not game_over(board):
        for _ in range(1 + dice[0] == dice[1]):
            code_board = getboard_code(board)
            policy_board = policy.get(code_board)
            l = legal_moves2(board, dice, player)
            if len(l) != 0:
                z = 0
                for i in range (len (l)):
                    code_m = code(dice, l[i])
                    if not code_m in policy_board:
                        policy_board[code_m] = 0
                    z = z + math.exp(policy_board[code_m])
                stop = random.random () * z
                move = 0
                z = 0
                while True:
                    code_m = code(dice, l[move])
                    z = z + math.exp(policy_board[code_m])
                    if z >= stop:
                        break
                    move = move + 1
                for m in l[move]:
                    update_board(board, m, player)
                p.append(l[move])
                d.append(dice)

        dice = roll_dice()
        player = -player
    return winner_gains(-player, board), p, d

def adapt (s, winner, board, player, p, d, policy):
    polp = copy.deepcopy (policy)
    alpha = 0.32
    for a in range(len(p)):
    #while not game_over(s):
        for _ in range(1 + d[a][0] == d[a][1]):
            l = legal_moves2(s, d[a], player)
            move = p[a]
            code_board = getboard_code(board)
            policy_board = policy.get(code_board)
            polp_board = polp.get(code_board)
            if player == winner:
                z = 0
                for i in range (len (l)):
                    code_m = code(d[a], l[i])
                    z = z + math.exp (policy_board[code_m])
                polp.put (code_m, polp_board[code_m] + alpha)
                for i in range (len (l)):
                    code_m = code(d[a], l[i])
                    proba = math.exp (policy.get (code_m)) / z
                    polp.put (code_m, polp_board[code_m] - alpha * proba)
            for m in move:
                update_board(board, m, player)
        player = -player
    return polp

def PPAF(board, dice, player, p, d, policy):
    if game_over(board):
        return winner_gains(-player, board)
    t = look (getboard_code(board))
    if t != None:
        bestValue = -1000000.0
        best = 0
        moves = legal_moves2(board, dice, player)
        if len(moves) == 0:
            best = None
        for i in range (0, len (moves)):
            val = 1000000.0
            if t [1] [i] > 0:
                Q = t [2] [i] / t [1] [i]
                if player == -1:
                    Q = 1 - Q
                val = Q + 0.4 * math.sqrt (math.log (t [0]) / t [1] [i])
            if val > bestValue:
                bestValue = val
                best = i
        if best is not None:
            for m in moves[best]:
                update_board(board, m, player)
        dice = roll_dice()
        player = -player
        res = PPAF (board, dice, player, policy)
        t [0] += 1
        if best is not None:
            if best not in t[1]:
                t[1][best] = 0
                t[2][best] = 0
            t [1] [best] += 1
            t [2] [best] += res
            p.append(moves[best])
            d.append(dice)
        return res, p, d
    else:
        add (board)
        return playout (board, dice, player, policy)

def BestMovePPAF (board, dice, player, n):
    global Table
    Table = {}
    global seen_boards
    seen_boards = {}
    policy = Policy()
    for i in range (n):
        b1 = copy.deepcopy (board)
        res, p = PPAF (b1, dice, player, policy)
        b2 = copy.deepcopy (board)
        if res == 1:
            policy = adapt (b2, 1, b1, p, policy)
        else:
            policy = adapt (b2, -1, b1, p, policy)
    t = look (board)
    moves = legal_moves2(board, dice, player)
    best = moves [0]
    bestValue = t [1] [0]
    for i in range (1, len(moves)):
        if (t [1] [i] > bestValue):
            bestValue = t [1] [i]
            best = moves [i]
    return best