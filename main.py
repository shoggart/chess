import pygame
from src.constants import *
from src.board import ChessBoard
from src.ui import ChessUI

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Chess")
    
    chess_board = ChessBoard()
    ui = ChessUI(screen)
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif (event.type == pygame.MOUSEBUTTONDOWN and 
                  chess_board.current_turn == 'white' and 
                  not chess_board.game_over):
                x, y = pygame.mouse.get_pos()
                col = x // SQUARE_SIZE
                row = y // SQUARE_SIZE
                
                if chess_board.selected_piece:
                    if (row, col) in chess_board.valid_moves:
                        chess_board.move_piece(chess_board.selected_pos, (row, col))
                        chess_board.selected_piece = None
                        chess_board.valid_moves = []
                        # AI makes its move after player's move
                        if not chess_board.game_over:
                            chess_board.make_ai_move()
                    else:
                        chess_board.selected_piece = None
                        chess_board.valid_moves = []
                
                elif (chess_board.board[row][col] and 
                      chess_board.board[row][col].color == chess_board.current_turn):
                    chess_board.selected_piece = chess_board.board[row][col]
                    chess_board.selected_pos = (row, col)
                    chess_board.valid_moves = chess_board.get_valid_moves(row, col)
            
            # Add ability to restart game with spacebar when game is over
            elif event.type == pygame.KEYDOWN and chess_board.game_over:
                if event.key == pygame.K_SPACE:
                    chess_board = ChessBoard()  # Reset the game

        # Draw the board
        ui.draw_board(chess_board)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()