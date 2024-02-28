import Backgammon
import copy
import random
import time

def playout(board, dice, player):
    board_copy = copy.deepcopy(board)
    # Backgammon.pretty_print(board)

    while not Backgammon.game_over(board_copy):
        for _ in range(1 + int(dice[0] == dice[1])):
            moves = Backgammon.legal_moves(board_copy, dice, player)

            if len(moves) != 0:
                move = random.choice(moves)
                for m in move:
                    board_copy = Backgammon.update_board(board_copy, m, player)
            
            # print(dice, move, player)
            # Backgammon.pretty_print(board_copy)

        player = -player
        dice = Backgammon.roll_dice()

    score = Backgammon.winner_gains(-player, board_copy)
    return score

def flatMC(board, dice, player, n):
    bestScore = 0
    bestMove = 0
    comparison = {} # study on opening move

    moves = Backgammon.legal_moves(board, dice, player)
    if len(moves) == 0:
        return []

    for i in range(len(moves)):
        board_copy = copy.deepcopy(board)

        sum = 0
        victory = 0
        for _ in range(n):
            score = playout(board_copy, dice, player)
            # sum = sum + score # study on points rather than victory

            if score > 0:
                victory += 1
                sum += 1
        
        proba_victory = victory/(n)
        comparison[str(moves[i])] = proba_victory

        if sum > bestScore:
            bestScore = sum
            bestMove = i

    for move in comparison.keys(): # study on opening move
        print(f"Move: {move}, proba:{comparison[move]}")
    values = comparison.values()
    dif = max(values) - min(values)
    l = len(values)
    print(f"dice: {dice}, Diff: {dif}, len: {l}\n")
    
    return moves[bestMove]
    
def main():
    N = 1000
    games = 100

    winners = {"flatMC": [0, 0, 0, 0], "random": [0, 0, 0, 0]}
    mean_dice_rolls = 0
    mean_run_time = 0

    for _ in range(games):
        startTime = time.time()

        board = Backgammon.init_board()
        Backgammon.pretty_print(board)
        player = 1

        i = 0
        while not Backgammon.game_over(board):
            dice = Backgammon.roll_dice()
            mean_dice_rolls += 1
            dice = [5, 6] # study on opening move

            for _ in range(1 + int(dice[0] == dice[1])):
                move_MC = flatMC(board, dice, player, N)
                if len(move_MC) != 0:
                    for m in move_MC:
                        board = Backgammon.update_board(board, m, player)
                print(f"Turn: {i}, best move MC: {move_MC}\n")
                Backgammon.pretty_print(board)
                if Backgammon.game_over(board):
                    break

            inp = input() # study on opening move
            player = -player

            dice = Backgammon.roll_dice()
            for _ in range(1 + int(dice[0] == dice[1])):
                moves = Backgammon.legal_moves(board, dice, player)
                if len(moves) != 0:
                    move_random = random.choice(moves)
                    for m in move_random:
                        board = Backgammon.update_board(board, m, player)
                    print(f"Turn: {i}, best move random: {move_random}\n")
                else: print(f"Turn: {i}, best move random:  no available move\n")
                Backgammon.pretty_print(board)

            player = -player
            i += 1

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
            if points == -1:
                winners["random"][1] += 1
            elif points == -2:
                winners["random"][2] += 1
            else:
                winners["random"][3] += 1

    mean_dice_rolls = mean_dice_rolls//games
    mean_run_time = mean_run_time/games

    print(f"Out of {games} games between flatMC and random (N = {N}):\n")
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