import copy
import pygame

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


    def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final

        en_passant_empty = self.squares[final.row][final.col].isempty()

        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        # pawn promotion
        if isinstance(piece, Pawn):
            self.check_promotion(piece, final)
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                # console board move update
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece

        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
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
                return True
        return False
    
    def promote_pawn(self, piece, final):       
        # Disable mouse input while the player selects their promotion piece
        pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
        
        choice = None
        while choice not in ["1", "2", "3", "4"]:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.unicode in ["1", "2", "3", "4"]:
                        choice = event.unicode
                        
        # Re-enable mouse input now that the player has made their choice
        pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)
        
        if choice == "1":
            return Queen(piece.color)
        elif choice == "2":
            return Knight(piece.color)
        elif choice == "3":
            return Bishop(piece.color)
        else:
            return Rook(piece.color)
        

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2
    
    def set_true_en_passant(self, piece):
      
        if not isinstance(piece, Pawn):
            return False
        
        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False
        
        piece.en_passant = True
    
    def in_check(self, piece, move):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)

        temp_board.move(temp_piece, move, testing=True)

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_rival_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool=False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True
                        
        return False
    
    def square_under_attack(self, squares, piece, move):
        '''
            Check if a square is under attack by a rival piece of the given color
        '''
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)

        temp_board.move(temp_piece, move, testing=True)
        color = 'white' if piece.color == 'white' else 'black'

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_rival_piece(color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool=False)
                    for m in p.moves:
                        attacking = (m.final.row, m.final.col)
                        if attacking in squares:
                            return True
        return False

    def calc_moves(self, piece, row, col, bool=True):
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
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        # create new move
                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else: break
                        else:
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
                        final_piece = self.squares[move_row][col].piece
                        final = Square(move_row, col, final_piece)
                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
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
                        final_piece = self.squares[move_row][move_col].piece
                        final = Square(move_row, move_col)
                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

            # en passant moves
            r = 3 if piece.color == 'white' else 4
            fr = 2 if piece.color == 'white' else 5
            # left en pessant
            if Square.in_range(col-1) and row == r:
                if self.squares[row][col-1].has_rival_piece(piece.color):
                    p = self.squares[row][col-1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            initial = Square(row, col)
                            final = Square(fr, col-1, p)
                            move = Move(initial, final)
                            
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
            
            # right en pessant
            if Square.in_range(col+1) and row == r:
                if self.squares[row][col+1].has_rival_piece(piece.color):
                    p = self.squares[row][col+1].piece
                    if isinstance(p, Pawn):
                        print("Ik kom hier")
                        if p.en_passant:
                            initial = Square(row, col)
                            final = Square(fr, col+1, p)
                            move = Move(initial, final)
                            
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                        
        def straightline_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                move_row = row + row_incr
                move_col = col + col_incr

                while True:
                    if Square.in_range(move_row, move_col):
                        initial = Square(row, col)
                        final_piece = self.squares[move_row][move_col].piece
                        final = Square(move_row, move_col, final_piece)                  
                        move = Move(initial, final)
                        if self.squares[move_row][move_col].isempty():
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                    
                        elif self.squares[move_row][move_col].has_rival_piece(piece.color):
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                            break
                        
                        elif self.squares[move_row][move_col].has_team_piece(piece.color):
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
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else: break
                        else:
                            piece.add_move(move)

             if not piece.moved:
                 # Queen Castling
                 left_rook = self.squares[row][0].piece
                 if isinstance(left_rook, Rook):
                     if not left_rook.moved:
                        squares = [(7,1), (7,2), (7, 3)] if piece.color == 'white' else [(0,1), (0,2), (0,3)]
                        for c in range(1, 4):
                            if self.squares[row][c].has_piece():
                                break
                            if c == 3:
                                piece.left_rook = left_rook

                                # rook move
                                initial = Square(row, 0)
                                final = Square(row, 3)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col)
                                final = Square(row, 2)
                                moveK = Move(initial, final)

                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(left_rook, moveR) and not self.square_under_attack(squares, piece, moveK):
                                        piece.add_move(moveK)
                                        left_rook.add_move(moveR)
                                else:
                                    piece.add_move(moveK)
                                    left_rook.add_move(moveR)

                # King Castling
                 right_rook = self.squares[row][7].piece
                 if isinstance(right_rook, Rook):
                     if not right_rook.moved:
                        squares = [(7,5), (7,6)] if piece.color == 'white' else [(0,5), (0,6)]
                        for c in range(5, 7):
                            if self.squares[row][c].has_piece():
                                break
                            if c == 6:
                                piece.right_rook = right_rook

                                # rook move
                                initial = Square(row, 7)
                                final = Square(row, 5)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col)
                                final = Square(row, 6)
                                moveK = Move(initial, final)

                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(right_rook, moveR) and not self.square_under_attack(squares, piece, moveK):
                                        piece.add_move(moveK)
                                        right_rook.add_move(moveR)
                                else:
                                    piece.add_move(moveK)
                                    right_rook.add_move(moveR)
                

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
    
    def set_piece(self, piece, final, initial, new_piece):
        self.squares[final.row][final.col].piece = new_piece
        new_piece.color = piece.color
        self.squares[initial.row][initial.col].piece = None
    
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