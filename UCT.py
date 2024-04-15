
from Backgammon import *
import copy
import random
import time
import math
import GRAVE


def add (board_number):
    nplayouts = {}
    nwins = {}
    Table [board_number] = [0, nplayouts, nwins]

def look (board_number):
    return Table.get(board_number, None)

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


def playout(board, dice, player):
    board_copy = copy.deepcopy(board)
    # pretty_print(board)

    while not game_over(board_copy):
        for _ in range(1 + int(dice[0] == dice[1])):
            moves = legal_moves2(board_copy, dice, player)

            if len(moves) != 0:
                move = random.choice(moves)
                for m in move:
                    board_copy = update_board(board_copy, m, player)

            # print(dice, move, player)
            # pretty_print(board_copy)

        player = -player
        dice = roll_dice()

    score = winner_gains(-player, board_copy)
    return score

def uct(board, dice, player, seen_boards, c = 0.4):
    if game_over(board):
        return winner_gains(-player, board)
    board_number = next((i for i, b in enumerate(seen_boards) if np.array_equal(b, board)), None)
    t = look(board_number)
    if t is not None:
        bestValue = 0
        bestMove = 0
        moves = legal_moves2(board, dice, player)

        if len(moves) == 0:
            bestMove = None
        for m in range(len(moves)):
            val = 1000000.0
            if m not in t[1]:
                t[1][m] = 0
                t[2][m] = 0
            n = t[0]
            ni = t[1][m]
            wi = t[2][m]
            if ni > 0:
                Q = wi/ni
                if player == -1:
                    Q = 1 - Q
                val = Q + c*math.sqrt(math.log(n)/ni)
            if val > bestValue:
                bestValue = val
                bestMove = m
        if bestMove is not None:
            for m in moves[bestMove]:
                board = update_board(board, m, player)
            if not any(np.array_equal(board, b) for b in seen_boards):
                seen_boards.append(board)
        player = -player
        dice = roll_dice()
        res = uct(board, dice, player, seen_boards)
        t[0] += 1
        if bestMove is not None:
            t[1][bestMove] += 1
            t[2][bestMove] += res
    else:
        add(board_number)
        res = playout(board, dice, player)

    return res

def bestMoveUct(board, dice, player, N, seen_boards):
    global Table
    Table = {}
    for i in range(N):
        b1 = copy.deepcopy(board)
        res = uct(b1, dice, player, seen_boards)
    board_number = next((i for i, b in enumerate(seen_boards) if np.array_equal(b, board)), None)
    t = look(board_number)
    moves = legal_moves2(board, dice, player)
    if len(moves) == 0:
        return []
    best = moves[0]
    bestValue = t[1][0]
    for i in range(1, len(moves)):
        if (t[1][i] > bestValue):
            bestValue = t[1][i]
            best = moves[i]
    return best

def main7():
    N = 50
    games = 10
    c = 0.4

    winners = {"flatMC": [0, 0, 0, 0], "random": [0, 0, 0, 0]}
    mean_dice_rolls = 0
    mean_run_time = 0

    for _ in range(games):
        startTime = time.time()

        board = init_board()
        #pretty_print(board)
        player = 1

        i = 0
        while not game_over(board):
            seen_boards = []
            dice = roll_dice()
            while i == 0 and dice[0] == dice[1]:
                dice = roll_dice()
            mean_dice_rolls += 1
            beginning_dices = [[1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [2, 3], [2, 4], [2, 5], [2, 6], [3, 4], [3, 5], [3, 6], [4, 5], [4, 6], [5, 6]]
            #dice = beginning_dices[11] # study on opening move
            print(dice)

            for _ in range(1 + int(dice[0] == dice[1])):
                move_MC = GRAVE.BestMoveGRAVE(board, dice, player, seen_boards, N)
                if len(move_MC) != 0:
                    for m in move_MC:
                        board = update_board(board, m, player)
                print(f"Turn: {i}, best move grave: {move_MC}\n")
                pretty_print(board)
                if game_over(board):
                    break

            if game_over(board):
                player = -player
                break
            #inp = input() # study on opening move
            player = -player

            seen_boards = []

            #dice = roll_dice()
            for _ in range(1 + int(dice[0] == dice[1])):
                move_MC = bestMoveUct(board, dice, player, N, seen_boards)
                if len(move_MC) != 0:
                    for m in move_MC:
                        board = update_board(board, m, player)
                print(f"Turn: {i}, best move uct: {move_MC}\n")
                pretty_print(board)

            player = -player
            i += 1

        runTime = time.time() - startTime
        mean_run_time += runTime

        winner = -player
        print(winner)
        pretty_print(board)
        points = winner_gains(winner, board)
        if winner == 1:
            winners["flatMC"][0] += 1
            if points == 1:
                winners["flatMC"][1] += 1
            elif points == 2:
                winners["flatMC"][2] += 1
            else:
                winners["flatMC"][3] += 1
        else:
            winners["random"][0] += 1
            if points == -1:
                winners["random"][1] += 1
            elif points == -2:
                winners["random"][2] += 1
            else:
                winners["random"][3] += 1

    mean_dice_rolls = mean_dice_rolls//games
    mean_run_time = mean_run_time/games

    print(f"Out of {games} games between flatMC and random (N = {N}):\n")
    print(f"grave won {winners['flatMC'][0]} times ({round(100*winners['flatMC'][0]/games, 2)}%).")
    print(f"uct won {winners['random'][3]} times ({round(100*winners['random'][3]/games, 2)}%).\n")
    print(f"On average, a game last {round(mean_run_time, 3)}s and is played in {mean_dice_rolls} dice rolls.\n")