from Backgammon import *
import copy
import random
import time
import UCT

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


def sequentialHalving(board, dice, player, budget, seen_boards):
    global Table
    Table = {}
    board_number = next((i for i, b in enumerate(seen_boards) if np.array_equal(b, board)), None)
    add(board_number)
    moves = legal_moves2(board, dice, player)
    if len(moves) == 0:
        return []
    total = len(moves)
    nplayouts = {}
    nwins = {}
    while len(moves) > 1:
        for move in moves:
            code_move = code(dice, move)
            for i in range(int(budget//len(moves)*np.log2(total))):
                s = copy.deepcopy(board)
                for m in move:
                    s = update_board(s, m, player)
                res = UCT.uct(s, dice, player, seen_boards)
                if code_move not in nplayouts:
                    nplayouts[code_move] = 0
                    nwins[code_move] = 0
                nplayouts[code_move] += 1
                if player == 1:
                    nwins[code_move] += res
                else:
                    nwins[code_move] += 1.0 - res
        moves = bestHalf(board, dice, player, moves, nwins, nplayouts)
    return moves[0]

def bestHalf(board, dice, player, moves, nwins, nplayouts):
    half = []
    notused = {}
    for i in range(int(np.ceil(len(moves)/2))):
        best = -1.0
        bestMove = moves[0]
        for move in moves:
            code_move = code(dice, move)
            if code_move not in notused:
                notused[code_move] = True
            if notused[code_move]:
                if not code_move in nwins:
                    mu = 0
                else:
                    mu = nwins[code_move] / nplayouts[code_move]
                if mu > best:
                    best = mu
                    bestMove = move
        code_best = code(dice, bestMove)
        notused[code_best] = False
        half.append(bestMove)
    return half

# to check
def BestMoveHalving (board, dice, player, n, seen_boards):
    global Table
    Table = {}
    board_number = next((i for i, b in enumerate(seen_boards) if np.array_equal(b, board)), None)
    add(board_number)
    for i in range (n):
        b1 = copy.deepcopy (board)
        res = sequentialHalving (b1, dice, player, 10, seen_boards)
    root = look (board_number)
    moves = legal_moves2(board, dice, player)
    if len(moves) == 0:
        return []
    best = moves [0]
    bestValue = root [1] [0]
    for i in range (1, len(moves)):
        if (root [1] [i] > bestValue):
            bestValue = root [1] [i]
            best = moves [i]
    return best

def main():
    N = 50
    games = 1

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
            while i == 0 and dice [0] == dice[1]:
                dice = roll_dice()
            mean_dice_rolls += 1
            beginning_dices = [[1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [2, 3], [2, 4], [2, 5], [2, 6], [3, 4], [3, 5], [3, 6], [4, 5], [4, 6], [5, 6]]
            #dice = beginning_dices[12] # study on opening move
            #print(dice)

            for _ in range(1 + int(dice[0] == dice[1])):
                move_MC = BestMoveHalving(board, dice, player, N, seen_boards)
                if len(move_MC) != 0:
                    for m in move_MC:
                        board = update_board(board, m, player)
                print(f"Turn: {i}, best move MC: {move_MC}\n")
                pretty_print(board)
                if game_over(board):
                    break

            if game_over(board):
                player = -player
                break
            #inp = input() # study on opening move

            player = -player

            dice = roll_dice()
            for _ in range(1 + int(dice[0] == dice[1])):
                moves = legal_moves(board, dice, player)
                if len(moves) != 0:
                    move_random = random.choice(moves)
                    for m in move_random:
                        board = update_board(board, m, player)
                    print(f"Turn: {i}, best move random: {move_random}\n")
                else: print(f"Turn: {i}, best move random:  no available move\n")
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
    print(f"FlatMC won {winners['flatMC'][0]} times ({round(100*winners['flatMC'][0]/games, 2)}%).")
    print(f"Random won {winners['random'][3]} times ({round(100*winners['random'][3]/games, 2)}%).\n")
    print(f"On average, a game last {round(mean_run_time, 3)}s and is played in {mean_dice_rolls} dice rolls.\n")