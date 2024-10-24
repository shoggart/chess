import pygame
import os
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 800
SQUARE_SIZE = WINDOW_SIZE // 8
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
HIGHLIGHT = (255, 255, 0, 100)
CHECK_HIGHLIGHT = (255, 0, 0, 100)
LAST_MOVE_HIGHLIGHT = (0, 255, 0, 100)

# Set up the display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Chess")

# AI Constants
DEPTH = 3  # AI looks 3 moves ahead

# Piece values for AI evaluation
PIECE_VALUES = {
    'pawn': 100,
    'knight': 320,
    'bishop': 330,
    'rook': 500,
    'queen': 900,
    'king': 20000
}

# Position evaluation tables
PAWN_TABLE = [
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [ 5,  5, 10, 25, 25, 10,  5,  5],
    [ 0,  0,  0, 20, 20,  0,  0,  0],
    [ 5, -5,-10,  0,  0,-10, -5,  5],
    [ 5, 10, 10,-20,-20, 10, 10,  5],
    [ 0,  0,  0,  0,  0,  0,  0,  0]
]

KNIGHT_TABLE = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

BISHOP_TABLE = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]

ROOK_TABLE = [
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [ 0,  0,  0,  5,  5,  0,  0,  0]
]

QUEEN_TABLE = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [ -5,  0,  5,  5,  5,  5,  0, -5],
    [  0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
]

def load_piece_image(piece_type, color):
    """Load PNG piece image"""
    color_prefix = 'w' if color == 'white' else 'b'
    file_path = os.path.join('pieces', f'{piece_type}-{color_prefix}.png')
    
    try:
        # Load PNG directly
        image = pygame.image.load(file_path)
        # Scale image to fit square
        return pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
    except Exception as e:
        print(f"Error loading piece image: {e}")
        return create_fallback_piece(piece_type, color)

def create_fallback_piece(piece_type, color):
    """Create a basic piece shape if PNG loading fails"""
    surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
    piece_color = WHITE if color == 'white' else BLACK
    text = piece_type[0].upper() if color == 'white' else piece_type[0].lower()
    font = pygame.font.Font(None, 40)
    text_surface = font.render(text, True, piece_color)
    text_rect = text_surface.get_rect(center=(SQUARE_SIZE//2, SQUARE_SIZE//2))
    surface.blit(text_surface, text_rect)
    return surface

class Piece:
    def __init__(self, color, piece_type, load_image=True):
        self.color = color
        self.piece_type = piece_type
        self.has_moved = False
        self.image = load_piece_image(piece_type, color) if load_image else None
    
    def copy(self):
        new_piece = Piece(self.color, self.piece_type, load_image=False)
        new_piece.has_moved = self.has_moved
        return new_piece

class ChessAI:
    def __init__(self, color):
        self.color = color
        self.opponent_color = 'white' if color == 'black' else 'black'

    def evaluate_position(self, board):
        score = 0
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece:
                    value = PIECE_VALUES[piece.piece_type]
                    position_bonus = self.get_position_bonus(piece, row, col)
                    
                    if piece.color == self.color:
                        score += value + position_bonus
                    else:
                        score -= value + position_bonus
        return score

    def get_position_bonus(self, piece, row, col):
        if piece.color == 'black':
            row = 7 - row  # Flip board for black pieces
            
        if piece.piece_type == 'pawn':
            return PAWN_TABLE[row][col]
        elif piece.piece_type == 'knight':
            return KNIGHT_TABLE[row][col]
        elif piece.piece_type == 'bishop':
            return BISHOP_TABLE[row][col]
        elif piece.piece_type == 'rook':
            return ROOK_TABLE[row][col]
        elif piece.piece_type == 'queen':
            return QUEEN_TABLE[row][col]
        return 0

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0:
            return self.evaluate_position(board)

        if maximizing_player:
            max_eval = float('-inf')
            for move in self.get_all_moves(board, self.color):
                new_board = self.simulate_move(board, move)
                eval = self.minimax(new_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_all_moves(board, self.opponent_color):
                new_board = self.simulate_move(board, move)
                eval = self.minimax(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, board):
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        possible_moves = self.get_all_moves(board, self.color)
        random.shuffle(possible_moves)  # Add some randomness to equal-valued moves
        
        for move in possible_moves:
            new_board = self.simulate_move(board, move)
            value = self.minimax(new_board, DEPTH - 1, alpha, beta, False)
            
            if value > best_value:
                best_value = value
                best_move = move
            
            alpha = max(alpha, value)
        
        return best_move

    def get_all_moves(self, board, color):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece and piece.color == color:
                    valid_moves = board.get_valid_moves(row, col, checking_future=True)
                    for move in valid_moves:
                        moves.append(((row, col), move))
        return moves

    def simulate_move(self, board, move):
        new_board = ChessBoard(create_ai=False, load_images=False)
        new_board.current_turn = board.current_turn
        new_board.last_move = board.last_move
        new_board.last_double_pawn = board.last_double_pawn
        
        # Copy board state manually
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece:
                    new_board.board[row][col] = piece.copy()
                else:
                    new_board.board[row][col] = None
        
        # Make the move
        from_pos, to_pos = move
        new_board.move_piece(from_pos, to_pos, checking_future=True)
        return new_board

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

    def is_in_check(self, color):
        # Find king position
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.piece_type == 'king' and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break

        # Check if any opponent piece can capture the king
        opponent_color = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == opponent_color:
                    valid_moves = self.get_raw_moves_without_castling(row, col)
                    if king_pos in valid_moves:
                        return True
        return False
    
    def get_raw_moves_without_castling(self, row, col):
        """Get valid moves without considering check or castling"""
        piece = self.board[row][col]
        if not piece:
            return []

        valid_moves = []
        
        if piece.piece_type == 'pawn':
            direction = 1 if piece.color == 'black' else -1
            
            # Forward move
            if 0 <= row + direction < 8 and not self.board[row + direction][col]:
                valid_moves.append((row + direction, col))
                
                # Initial two-square move
                if ((piece.color == 'black' and row == 1) or 
                    (piece.color == 'white' and row == 6)):
                    if not self.board[row + 2*direction][col]:
                        valid_moves.append((row + 2*direction, col))
            
            # Diagonal captures
            for dcol in [-1, 1]:
                new_row, new_col = row + direction, col + dcol
                if (0 <= new_row < 8 and 0 <= new_col < 8 and 
                    self.board[new_row][new_col] and 
                    self.board[new_row][new_col].color != piece.color):
                    valid_moves.append((new_row, new_col))

        elif piece.piece_type == 'rook':
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            valid_moves.extend(self.get_sliding_moves(row, col, directions))

        elif piece.piece_type == 'bishop':
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            valid_moves.extend(self.get_sliding_moves(row, col, directions))

        elif piece.piece_type == 'queen':
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            valid_moves.extend(self.get_sliding_moves(row, col, directions))

        elif piece.piece_type == 'knight':
            moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                    (1, 2), (1, -2), (-1, 2), (-1, -2)]
            for drow, dcol in moves:
                new_row, new_col = row + drow, col + dcol
                if (0 <= new_row < 8 and 0 <= new_col < 8 and
                    (not self.board[new_row][new_col] or 
                    self.board[new_row][new_col].color != piece.color)):
                    valid_moves.append((new_row, new_col))

        elif piece.piece_type == 'king':
            # Normal moves only, no castling
            moves = [(0, 1), (0, -1), (1, 0), (-1, 0),
                    (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for drow, dcol in moves:
                new_row, new_col = row + drow, col + dcol
                if (0 <= new_row < 8 and 0 <= new_col < 8 and
                    (not self.board[new_row][new_col] or 
                    self.board[new_row][new_col].color != piece.color)):
                    valid_moves.append((new_row, new_col))

        return valid_moves

    def get_valid_moves(self, row, col, checking_future=False):
        piece = self.board[row][col]
        if not piece:
            return []

        valid_moves = []
        raw_moves = self.get_raw_moves(row, col)

        # Only simulate future positions if we're not already checking a future position
        if not checking_future:
            for move in raw_moves:
                new_board = ChessBoard(create_ai=False, load_images=False)
                new_board.last_move = self.last_move
                new_board.last_double_pawn = self.last_double_pawn
                
                # Copy board state manually
                for r in range(8):
                    for c in range(8):
                        current_piece = self.board[r][c]
                        if current_piece:
                            new_board.board[r][c] = current_piece.copy()
                        else:
                            new_board.board[r][c] = None
                
                new_board.move_piece((row, col), move, checking_future=True)
                
                if not new_board.is_in_check(piece.color):
                    valid_moves.append(move)
        else:
            # If we're checking a future position, just return raw moves
            valid_moves = raw_moves

        return valid_moves

    def get_raw_moves(self, row, col, checking_attacks=False):
        piece = self.board[row][col]
        if not piece:
            return []

        valid_moves = []
        
        if piece.piece_type == 'pawn':
            direction = 1 if piece.color == 'black' else -1
            
            # Forward move
            if 0 <= row + direction < 8 and not self.board[row + direction][col]:
                valid_moves.append((row + direction, col))
                
                # Initial two-square move
                if ((piece.color == 'black' and row == 1) or 
                    (piece.color == 'white' and row == 6)):
                    if not self.board[row + 2*direction][col]:
                        valid_moves.append((row + 2*direction, col))
            
            # Diagonal captures
            for dcol in [-1, 1]:
                new_row, new_col = row + direction, col + dcol
                if (0 <= new_row < 8 and 0 <= new_col < 8):
                    # Normal capture
                    if (self.board[new_row][new_col] and 
                        self.board[new_row][new_col].color != piece.color):
                        valid_moves.append((new_row, new_col))
                    # En passant
                    elif self.last_double_pawn:
                        last_row, last_col = self.last_double_pawn
                        if (row == last_row and new_col == last_col and
                            ((piece.color == 'white' and row == 3) or 
                             (piece.color == 'black' and row == 4))):
                            valid_moves.append((new_row, new_col))

        elif piece.piece_type == 'rook':
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            valid_moves.extend(self.get_sliding_moves(row, col, directions))

        elif piece.piece_type == 'bishop':
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            valid_moves.extend(self.get_sliding_moves(row, col, directions))

        elif piece.piece_type == 'queen':
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                        (1, 1), (1, -1), (-1, 1), (-1, -1)]
            valid_moves.extend(self.get_sliding_moves(row, col, directions))

        elif piece.piece_type == 'knight':
            moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                    (1, 2), (1, -2), (-1, 2), (-1, -2)]
            for drow, dcol in moves:
                new_row, new_col = row + drow, col + dcol
                if (0 <= new_row < 8 and 0 <= new_col < 8 and
                    (not self.board[new_row][new_col] or 
                    self.board[new_row][new_col].color != piece.color)):
                    valid_moves.append((new_row, new_col))

        elif piece.piece_type == 'king':
            # Normal moves
            moves = [(0, 1), (0, -1), (1, 0), (-1, 0),
                    (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for drow, dcol in moves:
                new_row, new_col = row + drow, col + dcol
                if (0 <= new_row < 8 and 0 <= new_col < 8 and
                    (not self.board[new_row][new_col] or 
                    self.board[new_row][new_col].color != piece.color)):
                    valid_moves.append((new_row, new_col))

            # Only check castling if we're not checking for attacks
            if not checking_attacks:
                if not piece.has_moved and not self.is_in_check(piece.color):
                    # Kingside castling
                    if (self.can_castle_kingside(row, piece.color)):
                        valid_moves.append((row, 6))
                    
                    # Queenside castling
                    if (self.can_castle_queenside(row, piece.color)):
                        valid_moves.append((row, 2))

        return valid_moves

    def can_castle_kingside(self, row, color):
        king = self.board[row][4]
        rook = self.board[row][7]
        
        return (king and king.piece_type == 'king' and not king.has_moved and
                rook and rook.piece_type == 'rook' and not rook.has_moved and
                all(self.board[row][col] is None for col in range(5, 7)) and
                not any(self.is_square_attacked(row, col, color) for col in range(4, 7)))

    def can_castle_queenside(self, row, color):
        king = self.board[row][4]
        rook = self.board[row][0]
        
        return (king and king.piece_type == 'king' and not king.has_moved and
                rook and rook.piece_type == 'rook' and not rook.has_moved and
                all(self.board[row][col] is None for col in range(1, 4)) and
                not any(self.is_square_attacked(row, col, color) for col in range(2, 5)))

    def is_square_attacked(self, row, col, color):
        opponent_color = 'black' if color == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.color == opponent_color:
                    # Pass checking_attacks=True to avoid recursion
                    if (row, col) in self.get_raw_moves(r, c, checking_attacks=True):
                        return True
        return False

    def get_sliding_moves(self, row, col, directions):
        valid_moves = []
        piece = self.board[row][col]
        
        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target_piece = self.board[new_row][new_col]
                if not target_piece:
                    valid_moves.append((new_row, new_col))
                elif target_piece.color != piece.color:
                    valid_moves.append((new_row, new_col))
                    break
                else:
                    break
                new_row += drow
                new_col += dcol
        
        return valid_moves

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False

        # Check if any move can get out of check
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    valid_moves = self.get_valid_moves(row, col, checking_future=True)
                    if valid_moves:
                        return False
        return True

    def move_piece(self, from_pos, to_pos, checking_future=False):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.board[from_row][from_col]
        if not piece:
            return

        # Add logging for debugging
        if not checking_future:
            print(f"\nMoving {piece.color} {piece.piece_type} from {from_pos} to {to_pos}")
            print(f"Current turn: {self.current_turn}")

        # Store last move for en passant
        if not checking_future:
            self.last_move = (from_pos, to_pos)
            # Reset last_double_pawn unless this is a double pawn move
            if piece.piece_type == 'pawn' and abs(to_row - from_row) == 2:
                self.last_double_pawn = (to_row, to_col)
            else:
                self.last_double_pawn = None

        # Handle castling
        if piece.piece_type == 'king' and abs(from_col - to_col) == 2:
            # Kingside castling
            if to_col == 6:
                self.board[to_row][5] = self.board[to_row][7]  # Move rook
                self.board[to_row][7] = None
                self.board[to_row][5].has_moved = True
            # Queenside castling
            elif to_col == 2:
                self.board[to_row][3] = self.board[to_row][0]  # Move rook
                self.board[to_row][0] = None
                self.board[to_row][3].has_moved = True

        # Handle en passant capture
        if (piece.piece_type == 'pawn' and 
            abs(from_col - to_col) == 1 and 
            not self.board[to_row][to_col]):
            # Remove the captured pawn
            capture_row = from_row
            self.board[capture_row][to_col] = None

        # Make the move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.has_moved = True

        # Check for pawn promotion with logging
        if piece.piece_type == 'pawn' and (to_row == 0 or to_row == 7):
            if not checking_future:
                print(f"Promoting pawn at {to_row}, {to_col} to queen")
            self.board[to_row][to_col] = Piece(piece.color, 'queen', load_image=not checking_future)

        # Only do these checks if we're not simulating a future position
        if not checking_future:
            # Switch turns
            self.current_turn = 'black' if self.current_turn == 'white' else 'white'

            # Update check status
            self.in_check['white'] = self.is_in_check('white')
            self.in_check['black'] = self.is_in_check('black')

            # Check for checkmate
            if self.is_checkmate(self.current_turn):
                winner = 'White' if self.current_turn == 'black' else 'Black'
                print(f"Checkmate! {winner} wins!")
                self.game_over = True

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                color = WHITE if (row + col) % 2 == 0 else GRAY
                pygame.draw.rect(screen, color, 
                            (col * SQUARE_SIZE, row * SQUARE_SIZE, 
                                SQUARE_SIZE, SQUARE_SIZE))
                
                piece = self.board[row][col]
                if piece:
                    screen.blit(piece.image, 
                            (col * SQUARE_SIZE, row * SQUARE_SIZE))

        # Highlight selected piece's valid moves
        for row, col in self.valid_moves:
            highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), 
                                            pygame.SRCALPHA)
            pygame.draw.rect(highlight_surface, HIGHLIGHT, 
                        (0, 0, SQUARE_SIZE, SQUARE_SIZE))
            screen.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        # Highlight last move
        if self.last_move:
            from_pos, to_pos = self.last_move
            for pos in [from_pos, to_pos]:
                highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), 
                                                pygame.SRCALPHA)
                pygame.draw.rect(highlight_surface, LAST_MOVE_HIGHLIGHT, 
                            (0, 0, SQUARE_SIZE, SQUARE_SIZE))
                screen.blit(highlight_surface, 
                        (pos[1] * SQUARE_SIZE, pos[0] * SQUARE_SIZE))

        # Highlight king in check
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if (piece and piece.piece_type == 'king' and 
                    self.in_check[piece.color]):
                    check_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), 
                                                pygame.SRCALPHA)
                    pygame.draw.rect(check_surface, CHECK_HIGHLIGHT, 
                                (0, 0, SQUARE_SIZE, SQUARE_SIZE))
                    screen.blit(check_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))

    def make_ai_move(self):
        if self.ai and not self.game_over:
            move = self.ai.get_best_move(self)
            if move:
                from_pos, to_pos = move
                # Highlight the piece that's about to move
                self.selected_piece = self.board[from_pos[0]][from_pos[1]]
                self.selected_pos = from_pos
                self.valid_moves = [to_pos]
                
                # Force a redraw to show the highlight
                self.draw_board()
                pygame.display.flip()
                
                # Wait a moment to show the planned move
                pygame.time.wait(500)  # 500ms delay
                
                # Make the move
                self.move_piece(from_pos, to_pos)
                
                # Clear highlights
                self.selected_piece = None
                self.selected_pos = None
                self.valid_moves = []

def main():
    chess_board = ChessBoard()
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and chess_board.current_turn == 'white' and not chess_board.game_over:
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

        # Draw the board
        chess_board.draw_board()

        # Draw game over message
        if chess_board.game_over:
            winner = "White" if chess_board.current_turn == 'black' else "Black"
            text = font.render(f"Checkmate! {winner} wins!", True, (255, 0, 0))
            text_rect = text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2))
            screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()