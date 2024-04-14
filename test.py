
import numpy as np
board = np.array([1,2,3])
seen_boards = {}

def getboard_code(board):
    strboard = str(board)
    if strboard not in seen_boards:
        seen_boards[str(board)] = len(seen_boards)
    board_number = seen_boards[str(board)]
    return board_number

print(getboard_code(board))