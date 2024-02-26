import Backgammon
import copy
import random
import time

def playout(board, dice, player):
    board_copy = copy.deepcopy(board)

    while not Backgammon.game_over(board_copy):
        moves = Backgammon.legal_moves(board_copy, dice, player)

        if len(moves) != 0:
            move = random.choice(moves)
            for m in move:
                board_copy = Backgammon.update_board(board_copy, m, player)

        player = -player
        dice = Backgammon.roll_dice()

    score = Backgammon.winner_gains(-player, board_copy)
    return score

def flatMC(board, dice, player, n):
    bestScore = 0
    bestMove = 0

    moves = Backgammon.legal_moves(board, dice, player)
    if len(moves) == 0:
        return []
    
    for i in range(len(moves)):
        board_copy = copy.deepcopy(board)
        move = moves[i]
        for m in move:
            board_copy = Backgammon.update_board(board_copy, m, player)

        sum = 0
        for _ in range(n//len(moves)):
            score = playout(board_copy, dice, player)
            sum = sum + score

        if sum > bestScore:
            bestScore = sum
            bestMove = i
    
    return moves[bestMove]
    
def main():
    N = 200
    games = 30

    winners = {"flatMC": [0, 0, 0, 0], "random": [0, 0, 0, 0]}
    mean_dice_rolls = 0
    mean_run_time = 0

    for _ in range(games):
        startTime = time.time()

        board = Backgammon.init_board()
        player = 1

        while not Backgammon.game_over(board):
            dice = Backgammon.roll_dice()
            mean_dice_rolls += 1

            move_MC = flatMC(board, dice, player, N)
            if len(move_MC) != 0:
                for m in move_MC:
                    board = Backgammon.update_board(board, m, player)
            if Backgammon.game_over(board):
                break

            dice = Backgammon.roll_dice()
            moves = Backgammon.legal_moves(board, dice, player)
            if len(moves) != 0:
                move_random = random.choice(moves)
                for m in move_random:
                    board = Backgammon.update_board(board, m, player)

            player = -player

        runTime = time.time() - startTime
        mean_run_time += runTime

        winner = -player
        points = Backgammon.winner_gains(winner, board)
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
            if points == 1:
                winners["random"][1] += 1
            elif points == 2:
                winners["random"][2] += 1
            else:
                winners["random"][3] += 1

    mean_dice_rolls = mean_dice_rolls//games
    mean_run_time = mean_run_time/games

    print(f"Out of {games} games between flatMC and random:\n")
    print(f"FlatMC won {winners['flatMC'][0]} times ({round(100*winners['flatMC'][0]/games, 2)}%) and won " \
          f"{winners['flatMC'][1] + winners['flatMC'][2]*2 + winners['flatMC'][3]*3} points.")
    print(f"Random won {winners['random'][0]} times ({round(100*winners['random'][0]/games, 2)}%) and won " \
          f"{winners['random'][1] + winners['random'][2]*2 + winners['random'][3]*3} points.\n")
    print(f"FlatMC won {winners['flatMC'][1]} 1-point plays, {winners['flatMC'][2]} 2-point plays " \
          f"and {winners['flatMC'][3]} 3-point plays.")
    print(f"Random won {winners['random'][1]} 1-point plays, {winners['random'][2]} 2-point plays " \
          f"and {winners['random'][3]} 3-point plays.\n")
    print(f"On average, a game last {round(mean_run_time, 3)}s and is played in {mean_dice_rolls} dice rolls.\n")

if __name__ == '__main__':
    main()