import pygame
import sys
import time

from const import *
from game import Game
from square import Square
from move import Move
from piece import *
from board import *
from ai import *

class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
        pygame.display.set_caption("Chess")
        self.game = Game()

    def mainloop(self):
        
        game = self.game
        screen = self.screen
        board = self.game.board
        dragger = self.game.dragger

        while True:

            game.show_background(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)

            game.show_hover(screen)

            if dragger.dragging:
                dragger.update_blit(screen)
            
            for event in pygame.event.get():
                if game.next_player == 'white':
                    # click
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        dragger.update_mouse(event.pos)

                        clicked_row = dragger.MouseY // SQSIZE
                        clicked_col = dragger.mouseX // SQSIZE

                        if board.squares[clicked_row][clicked_col].has_piece():
                            piece = board.squares[clicked_row][clicked_col].piece

                            if piece.color == game.next_player:
                                board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                                dragger.save_initial(event.pos)
                                dragger.drag_piece(piece)
                                game.show_background(screen)
                                game.show_last_move(screen)
                                game.show_moves(screen)
                                game.show_pieces(screen)
                
                    # mouse motion
                    elif event.type == pygame.MOUSEMOTION:
                        motion_row = event.pos[1] // SQSIZE
                        motion_col = event.pos[0] // SQSIZE

                        game.set_hover(motion_row, motion_col)

                        if dragger.dragging:
                            dragger.update_mouse(event.pos)
                            game.show_background(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)
                            game.show_hover(screen)
                            dragger.update_blit(screen)
                    
                    # click release
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if dragger.dragging:
                            dragger.update_mouse(event.pos)

                            released_row = dragger.MouseY // SQSIZE
                            released_col = dragger.mouseX // SQSIZE

                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, released_col)
                            move = Move(initial, final)

                            if isinstance(dragger.piece, Pawn):
                                board.set_true_en_passant(dragger.piece)  

                            if board.valid_move(dragger.piece, move):
                                if isinstance(dragger.piece, Pawn) and board.check_promotion(dragger.piece, move.final):
                                    new_piece = board.promote_pawn(dragger.piece, move.final)
                                    board.set_piece(dragger.piece, move.final, move.initial, new_piece)
                                    game.show_background(screen)
                                    game.show_last_move(screen)
                                    game.show_pieces(screen)
                                    game.next_turn()
                                else:            
                                    board.move(dragger.piece, move)
                                    game.show_background(screen)
                                    game.show_last_move(screen)
                                    game.show_pieces(screen)
                                    game.next_turn()

                        dragger.undrag_piece()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            game.reset() 
                            game = self.game
                            screen = self.screen
                            board = self.game.board
                            dragger = self.game.dragger  
                else:
                    piece_to_move, move_to_make = ai_random_move(board)
                    board.move(piece_to_move, move_to_make)
                    game.show_background(screen)
                    game.show_last_move(screen)
                    game.show_pieces(screen)
                    game.next_turn()


                # quit the application
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
            pygame.display.update()

main = Main()
main.mainloop()