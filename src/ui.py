import pygame
from .constants import *

class ChessUI:
    def __init__(self, screen):
        self.screen = screen

    def draw_board(self, chess_board):
        # Draw squares
        for row in range(8):
            for col in range(8):
                color = WHITE if (row + col) % 2 == 0 else GRAY
                pygame.draw.rect(self.screen, color, 
                            (col * SQUARE_SIZE, row * SQUARE_SIZE, 
                             SQUARE_SIZE, SQUARE_SIZE))
                
                piece = chess_board.board[row][col]
                if piece:
                    self.screen.blit(piece.image, 
                                 (col * SQUARE_SIZE, row * SQUARE_SIZE))

        # Draw highlights
        self._draw_move_highlights(chess_board)
        self._draw_check_highlights(chess_board)
        self._draw_last_move_highlight(chess_board)
        
        if chess_board.game_over:
            self._draw_game_over_banner(chess_board)

    def _draw_move_highlights(self, chess_board):
        for row, col in chess_board.valid_moves:
            highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), 
                                            pygame.SRCALPHA)
            pygame.draw.rect(highlight_surface, HIGHLIGHT, 
                           (0, 0, SQUARE_SIZE, SQUARE_SIZE))
            self.screen.blit(highlight_surface, 
                           (col * SQUARE_SIZE, row * SQUARE_SIZE))

    def _draw_check_highlights(self, chess_board):
        for row in range(8):
            for col in range(8):
                piece = chess_board.board[row][col]
                if (piece and piece.piece_type == 'king' and 
                    chess_board.in_check[piece.color]):
                    highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), 
                                                     pygame.SRCALPHA)
                    pygame.draw.rect(highlight_surface, CHECK_HIGHLIGHT, 
                                   (0, 0, SQUARE_SIZE, SQUARE_SIZE))
                    self.screen.blit(highlight_surface, 
                                   (col * SQUARE_SIZE, row * SQUARE_SIZE))

    def _draw_last_move_highlight(self, chess_board):
        if chess_board.last_move:
            from_pos, to_pos = chess_board.last_move
            for pos in [from_pos, to_pos]:
                highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), 
                                                pygame.SRCALPHA)
                pygame.draw.rect(highlight_surface, LAST_MOVE_HIGHLIGHT, 
                               (0, 0, SQUARE_SIZE, SQUARE_SIZE))
                self.screen.blit(highlight_surface, 
                               (pos[1] * SQUARE_SIZE, pos[0] * SQUARE_SIZE))

    def _draw_game_over_banner(self, chess_board):
        banner_surface = pygame.Surface((WINDOW_SIZE, BANNER_HEIGHT), 
                                      pygame.SRCALPHA)
        pygame.draw.rect(banner_surface, BANNER_COLOR, 
                        (0, 0, WINDOW_SIZE, BANNER_HEIGHT))
        
        font = pygame.font.Font(None, 72)
        winner = "White" if chess_board.current_turn == 'black' else "Black"
        text = font.render(f"Checkmate! {winner} wins!", True, BANNER_TEXT_COLOR)
        text_rect = text.get_rect(center=(WINDOW_SIZE//2, BANNER_HEIGHT//2))
        
        self.screen.blit(banner_surface, 
                        (0, (WINDOW_SIZE - BANNER_HEIGHT)//2))
        self.screen.blit(text, 
                        (text_rect.x, (WINDOW_SIZE - BANNER_HEIGHT)//2 + 
                         text_rect.height//2))