import pygame
from .piece import Piece
from .move_validator import MoveValidator
from .ai import ChessAI
from .constants import *

class ChessBoard:
    def __init__(self, create_ai=True, load_images=True):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.selected_piece = None
        self.selected_pos = None
        self.valid_moves = []
        self.current_turn = 'white'
        self.ai = ChessAI('black') if create_ai else None
        self.in_check = {'white': False, 'black': False}
        self.game_over = False
        self.last_move = None
        self.last_double_pawn = None
        self.game_over_time = None
        self.winner = None
        self.move_count = 0
        self.validator = MoveValidator(self)
        
        if load_images:
            self.initialize_board()

    def initialize_board(self):
        # Initialize pawns
        for col in range(8):
            self.board[1][col] = Piece('black', 'pawn')
            self.board[6][col] = Piece('white', 'pawn')

        # Initialize other pieces
        piece_order = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for col in range(8):
            self.board[0][col] = Piece('black', piece_order[col])
            self.board[7][col] = Piece('white', piece_order[col])

    def move_piece(self, from_pos, to_pos, checking_future=False):
        if not self.validator.is_valid_move(from_pos, to_pos, checking_future):
            return False

        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.board[from_row][from_col]
        target_piece = self.board[to_row][to_col]
        is_capture = target_piece is not None
        
        # Get the move notation before making any changes
        move_text = ''
        if piece:
            # Handle castling notation
            if piece.piece_type == 'king' and abs(from_col - to_col) == 2:
                move_text = 'O-O' if to_col == 6 else 'O-O-O'
            else:
                # Regular move notation
                if piece.piece_type != 'pawn':
                    move_text += piece.piece_type[0].upper()
                
                # For pawn captures, add the file
                if piece.piece_type == 'pawn' and from_col != to_col:
                    move_text += 'abcdefgh'[from_col]
                    
                # Add capture symbol if applicable
                if is_capture:
                    move_text += 'x'
                    
                # Add destination square
                move_text += 'abcdefgh'[to_col] + '87654321'[to_row]
        
        # Handle castling
        if piece and piece.piece_type == 'king' and abs(from_col - to_col) == 2:
            # Kingside castling
            if to_col == 6:
                # Move rook
                self.board[to_row][5] = self.board[to_row][7]
                self.board[to_row][7] = None
                if self.board[to_row][5]:
                    self.board[to_row][5].has_moved = True
            # Queenside castling
            elif to_col == 2:
                # Move rook
                self.board[to_row][3] = self.board[to_row][0]
                self.board[to_row][0] = None
                if self.board[to_row][3]:
                    self.board[to_row][3].has_moved = True
        
        # Make the regular move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        if piece:
            piece.has_moved = True
        
        # Update game state if not checking future moves
        if not checking_future:
            # Store last move for en passant
            self.last_move = (from_pos, to_pos)
            if piece and piece.piece_type == 'pawn' and abs(to_row - from_row) == 2:
                self.last_double_pawn = (to_row, to_col)
            else:
                self.last_double_pawn = None
                
            # Switch turns
            self.current_turn = 'black' if piece.color == 'white' else 'white'
            
            # Check for check/checkmate
            opponent_color = 'black' if piece.color == 'white' else 'white'
            if self.validator.is_in_check(opponent_color):
                if self.validator.is_checkmate(opponent_color):
                    move_text += '#'
                    self.game_over = True
                    self.winner = piece.color.capitalize()
                    print(f"\nCheckmate! {self.winner} wins!")
                else:
                    move_text += '+'

            # Print the move
            if piece.color == 'white':
                print(f"{(self.move_count // 2) + 1}.{move_text}", end=' ')
            else:
                print(f"{move_text}")
                self.move_count += 1
                
        return True

    def _handle_castling(self, from_row, from_col, to_row, to_col):
        # Kingside castling
        if to_col == 6:
            self.board[to_row][5] = self.board[to_row][7]
            self.board[to_row][7] = None
            self.board[to_row][5].has_moved = True
        # Queenside castling
        elif to_col == 2:
            self.board[to_row][3] = self.board[to_row][0]
            self.board[to_row][0] = None
            self.board[to_row][3].has_moved = True

    def _is_en_passant_capture(self, piece, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        return (piece.piece_type == 'pawn' and 
                abs(from_col - to_col) == 1 and 
                not self.board[to_row][to_col])

    def _should_promote_pawn(self, piece, row):
        return piece.piece_type == 'pawn' and (row == 0 or row == 7)

    def _update_game_state(self):
        # Switch turns
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

        # Update check status
        self.in_check['white'] = self.validator.is_in_check('white')
        self.in_check['black'] = self.validator.is_in_check('black')

        # Check for checkmate
        if self.validator.is_checkmate(self.current_turn):
            self.winner = 'White' if self.current_turn == 'black' else 'Black'
            print(f"\n{'='*50}")
            print(f"CHECKMATE! {self.winner} wins!")
            print(f"{'='*50}\n")
            self.game_over = True
            self.game_over_time = pygame.time.get_ticks()

    def make_ai_move(self):
        if self.ai and not self.game_over:
            move = self.ai.get_best_move(self)
            if move:
                from_pos, to_pos = move
                self.selected_piece = self.board[from_pos[0]][from_pos[1]]
                self.selected_pos = from_pos
                self.valid_moves = [to_pos]
                
                pygame.time.wait(AI_MOVE_DELAY)
                
                self.move_piece(from_pos, to_pos)
                
                self.selected_piece = None
                self.selected_pos = None
                self.valid_moves = []

    def get_valid_moves(self, row, col, checking_future=False):
        return self.validator.get_valid_moves((row, col), checking_future)

    def get_piece(self, pos):
        row, col = pos
        return self.board[row][col]

    def copy(self):
        """Create a copy of the board for move validation"""
        new_board = ChessBoard(create_ai=False, load_images=False)
        new_board.board = self.validator._create_board_copy()
        new_board.current_turn = self.current_turn
        new_board.last_move = self.last_move
        new_board.last_double_pawn = self.last_double_pawn
        return new_board

    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.piece_type == 'king' and piece.color == color:
                    return (row, col)
        return None