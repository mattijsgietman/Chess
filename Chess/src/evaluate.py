from const import *

def evaluation(board):
    eval = 0
    for row in range(ROWS):
        for col in range(COLS):
            if board.squares[row][col].piece != None:
                eval += board.squares[row][col].piece.value
    return eval