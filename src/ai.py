import random
from .constants import *

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
            row = 7 - row
            
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
        random.shuffle(possible_moves)
        
        for move in possible_moves:
            new_board = self.simulate_move(board, move)
            value = self.minimax(new_board, AI_DEPTH - 1, alpha, beta, False)
            
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
        new_board = board.copy()
        from_pos, to_pos = move
        new_board.move_piece(from_pos, to_pos, checking_future=True)
        return new_board