
from Backgammon import *
import copy
import random
import time
import flatMC

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

def addAMAF(board_number):
    nplayouts = {}
    nwins = {}
    amafwins = {}
    amafplayouts = {}
    Table [board_number] = [0, nplayouts, nwins, amafplayouts, amafwins]

def updateAMAF(t, played, res):
    for i in range(len(played)):
        if played[:i].count(played[i]) == 0:
            if played[i] in t[3]:
                t[3][played[i]] += 1
                t[4][played[i]] += res
            else:
                t[3][played[i]] = 1
                t[4][played[i]] = res

def playoutAMAF(board, dice, player, played):
    board_copy = copy.deepcopy(board)
    # pretty_print(board)

    while not game_over(board_copy):
        for _ in range(1 + int(dice[0] == dice[1])):
            moves = legal_moves2(board_copy, dice, player)

            if len(moves) != 0:
                move = random.choice(moves)
                code_move = code(dice, move)
                played.append(code_move)
                for m in move:
                    board_copy = update_board(board_copy, m, player)

            # print(dice, move, player)
            # pretty_print(board_copy)

        player = -player
        dice = roll_dice()

    score = winner_gains(-player, board_copy)
    return score

def GRAVE (board, dice, player, played, tref, seen_boards):
    if game_over(board):
        score = winner_gains(-player, board)
        return score
    board_number = next((i for i, b in enumerate(seen_boards) if np.array_equal(b, board)), None)
    t = look(board_number)
    if t != None:
        tr = tref
        if t [0] > 50:
            tr = t
        bestValue = 0
        best = 0
        moves = legal_moves2(board, dice, player)
        if len(moves) == 0:
            best = None
        else:
            bestcode = code(dice, moves[0])
            for i in range (0, len (moves)):
                val = 1000000.0
                code_m = code(dice, moves[i])
                if code_m in tr[3]:
                    if tr [3] [code_m] > 0:
                        if i not in t[1]:
                            t[1][i] = 0
                            t[2][i] = 0
                        beta = tr [3][code_m] / (t [1] [i] + tr [3] [code_m] + 1e-5 * t [1] [i] * tr [3] [code_m])
                        Q = 1
                        if t [1] [i] > 0:
                            Q = t [2] [i] / t [1] [i]
                            if player == -1:
                                Q = 1 - Q
                        AMAF = tr [4] [code_m] / tr [3] [code_m]
                        if player == -1:
                            AMAF = 1 - AMAF
                        val = (1.0 - beta) * Q + beta * AMAF
                    if val > bestValue:
                        bestValue = val
                        best = i
                        bestcode = code_m
        if best is not None:
            for m in moves[best]:
                board = update_board(board, m, player)
            played.append(bestcode)
            if not any(np.array_equal(board, b) for b in seen_boards):
                seen_boards.append(board)
        dice = roll_dice()
        player = -player
        res = GRAVE(board, dice, player, played, tr, seen_boards)
        t [0] += 1
        if best is not None:
            if best in t[1]:
                t [1] [best] += 1
                if res < 0:
                    victory = 0
                else:
                    victory = 1
                t [2] [best] += victory
            else:
                t [1] [best] = 1
                if res < 0:
                    victory = 0
                else:
                    victory = 1
                t [2] [best] = victory
            updateAMAF (t, played, res)
        return res
    else:
        addAMAF (board_number)
        return playoutAMAF (board, dice, player, played)

def BestMoveGRAVE (board, dice, player, seen_boards, n):
    global Table
    Table = {}
    board_number = next((i for i, b in enumerate(seen_boards) if np.array_equal(b, board)), None)
    print(board_number)
    addAMAF (board_number)
    for i in range (n):
        root = look (board_number)
        b1 = copy.deepcopy (board)
        res = GRAVE (b1, dice, player, [], root, seen_boards)
    root = look (board_number)
    moves = legal_moves2(board, dice, player)
    if len(moves) == 0:
        return []
    best = moves [0]
    bestValue = root [1] [0]

    for i in range (1, len(moves)):
        if i not in root[1]: root[1][i] =0
        if (root [1] [i] > bestValue):
            bestValue = root [1] [i]
            best = moves [i]
    return best


def main():
    N = 50
    games = 10

    winners = {"flatMC": [0, 0, 0, 0], "random": [0, 0, 0, 0]}
    mean_dice_rolls = 0
    mean_run_time = 0

    for _ in range(games):
        startTime = time.time()

        board = init_board()
        pretty_print(board)

        player = 1

        i = 0
        while not game_over(board):
            seen_boards = []
            dice = roll_dice()
            mean_dice_rolls += 1
            beginning_dices = [[1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [2, 3], [2, 4], [2, 5], [2, 6], [3, 4], [3, 5], [3, 6], [4, 5], [4, 6], [5, 6]]
            #dice = beginning_dices[11] # study on opening move
            print(dice)

            for _ in range(1 + int(dice[0] == dice[1])):
                move_MC = BestMoveGRAVE(board, dice, player, seen_boards, N)
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

            #dice = roll_dice()
            for _ in range(1 + int(dice[0] == dice[1])):
                move_MC = flatMC(board, dice, player, N)
                if len(move_MC) != 0:
                    for m in move_MC:
                        board = update_board(board, m, player)
                    print(f"Turn: {i}, best move flat: {move_MC}\n")
                else: print(f"Turn: {i}, best move flat:  no available move\n")
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
    print(f"GRAVE won {winners['flatMC'][0]} times ({round(100*winners['flatMC'][0]/games, 2)}%).")
    print(f"flat won {winners['random'][3]} times ({round(100*winners['random'][3]/games, 2)}%).\n")
    print(f"On average, a game last {round(mean_run_time, 3)}s and is played in {mean_dice_rolls} dice rolls.\n")