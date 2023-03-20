from const import *
from square import Square
from piece import *
from move import Move

class Board:

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')


    def move(self, piece, move):
        initial = move.initial
        final = move.final

        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        # pawn promotion
        if isinstance(piece, Pawn):
            self.check_promotion(piece, final)

        if isinstance(piece, King):
            if self.castling(initial, final):
                diff = final.col - initial.col
                rook = piece.left_rook if (diff < 0) else piece.right_rook
                self.move(rook, rook.moves[-1])

        piece.moved = True
        piece.clear_moves()
        self.last_move = move


    def valid_move(self, piece, move):
        return move in piece.moves
    
    def check_promotion(self, piece, final):
        if final.row  == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2


    def calc_moves(self, piece, row, col):
        '''
            Calculate all the possible (valid) moves of a specific piece on a specific position
        '''

        def knight_moves():
            # at max 8 possible moves
            possible_moves = [
                (row-2, col + 1),
                (row-1, col + 2),
                (row+1, col + 2),
                (row+2, col + 1),
                (row-2, col - 1),
                (row-1, col - 2),
                (row+1, col - 2),
                (row+2, col - 1)
            ]

            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_rival(piece.color):
                        # create squares of new move
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)
                        # create new move
                        move = Move(initial, final)
                        piece.add_move(move)

        def pawn_moves():
            steps = 1 if piece.moved else 2

            # vertical
            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for move_row in range(start, end, piece.dir):
                if Square.in_range(move_row):
                    if self.squares[move_row][col].isempty():
                        initial = Square(row, col)
                        final = Square(move_row, col)
                        move = Move(initial, final)
                        piece.add_move(move)
                    else:
                        break
                else:
                    break

            # diagonal
            move_row = row + piece.dir
            move_cols = [col-1, col + 1]
            for move_col in move_cols:
                if Square.in_range(move_row, move_col):
                    if self.squares[move_row][move_col].has_rival_piece(piece.color):
                        initial = Square(row, col)
                        final = Square(move_row, move_col)
                        move = Move(initial, final)
                        piece.add_move(move)
                        
        def straightline_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                move_row = row + row_incr
                move_col = col + col_incr

                while True:
                    if Square.in_range(move_row, move_col):
                        initial = Square(row, col)
                        final = Square(move_row, move_col)
                        move = Move(initial, final)
                        if self.squares[move_row][move_col].isempty():
                            piece.add_move(move)
                    
                        if self.squares[move_row][move_col].has_rival_piece(piece.color):
                            piece.add_move(move)
                            break
                        
                        if self.squares[move_row][move_col].has_team_piece(piece.color):
                            break

                    else: break

                    move_row = move_row + row_incr
                    move_col = move_col + col_incr

        def king_moves():
             adjs = [
                 (row - 1, col),
                 (row - 1, col + 1),
                 (row, col + 1),
                 (row + 1, col + 1),
                 (row + 1, col),
                 (row + 1, col - 1),
                 (row, col - 1),
                 (row - 1, col - 1)
             ]

             for possible_move in adjs:
                 move_row, move_col = possible_move

                 if Square.in_range(move_row, move_col):
                     if self.squares[move_row][move_col].isempty_or_rival(piece.color):
                        initial = Square(row, col)
                        final = Square(move_row, move_col)
                        move = Move(initial, final)
                        piece.add_move(move)

             if not piece.moved:
                 # Queen Castling
                 left_rook = self.squares[row][0].piece
                 if isinstance(left_rook, Rook):
                     if not left_rook.moved:
                         for c in range(1, 4):
                             if self.squares[row][c].has_piece():
                                 break
                             if c == 3:
                                 piece.left_rook = left_rook

                                 # rook move
                                 initial = Square(row, 0)
                                 final = Square(row, 3)
                                 move = Move(initial, final)
                                 left_rook.add_move(move)

                                 # king move
                                 initial = Square(row, col)
                                 final = Square(row, 2)
                                 move = Move(initial, final)
                                 piece.add_move(move)

                # King Castling
                 right_rook = self.squares[row][7].piece
                 if isinstance(right_rook, Rook):
                     if not right_rook.moved:
                         for c in range(5, 7):
                             if self.squares[row][c].has_piece():
                                 break
                             if c == 6:
                                 piece.right_rook = right_rook

                                 # rook move
                                 initial = Square(row, 7)
                                 final = Square(row, 5)
                                 move = Move(initial, final)
                                 right_rook.add_move(move)

                                 # king move
                                 initial = Square(row, col)
                                 final = Square(row, 6)
                                 move = Move(initial, final)
                                 piece.add_move(move)
                

        if isinstance(piece, Pawn):
            pawn_moves()

        elif isinstance(piece, Knight):
            knight_moves()

        elif isinstance(piece, Bishop):
            straightline_moves([
                (-1, 1),
                (-1, -1),
                (1, 1),
                (1, -1)
            ])

        elif isinstance(piece, Rook):
            straightline_moves([
                (-1, 0),
                (1, 0),
                (0,1),
                (0,-1)
            ])

        elif isinstance(piece, Queen):
            straightline_moves([
                (-1, 0),
                (1, 0),
                (0,1),
                (0,-1),
                (-1, 1),
                (-1, -1),
                (1, 1),
                (1, -1)
            ])

        elif isinstance(piece, King):
            king_moves()

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = (6,7) if color == 'white' else (1,0)

        # pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        # knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # Bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        # Rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        #Queen
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # King
        self.squares[row_other][4] = Square(row_other, 4, King(color))   