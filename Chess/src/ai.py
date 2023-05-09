from evaluate import *
from const import *
from game import Game
from square import Square
from move import Move
from piece import *
from board import *
import random

def ai_random_move(board):
    pieces = []
    piece_move = []
    counter = 0
    for row in range(ROWS):
        for col in range(COLS):
            if board.squares[row][col].piece != None and board.squares[row][col].piece.color  == 'black':
                board.calc_moves(board.squares[row][col].piece, row, col, bool=True)
                pieces.append(board.squares[row][col].piece)
    for piece in pieces:
        for move in piece.moves:
            if piece.moves != None:
                piece_move.append((piece, move))
                counter += 1
    choice = random.choice(piece_move)
    print(choice)
    print(counter)
    return (choice[0], choice[1])

