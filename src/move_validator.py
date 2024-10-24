class MoveValidator:
    def __init__(self, board):
        self.board = board

    def _get_raw_moves(self, pos, skip_king_check=False):
        """Get all possible moves for a piece without considering check"""
        piece = self.board.get_piece(pos)
        if not piece:
            return []

        moves = []
        if piece.piece_type == 'pawn':
            moves.extend(self._get_pawn_moves(pos))
        elif piece.piece_type == 'knight':
            moves.extend(self._get_knight_moves(pos))
        elif piece.piece_type == 'bishop':
            moves.extend(self._get_diagonal_moves(pos))
        elif piece.piece_type == 'rook':
            moves.extend(self._get_straight_moves(pos))
        elif piece.piece_type == 'queen':
            moves.extend(self._get_straight_moves(pos))
            moves.extend(self._get_diagonal_moves(pos))
        elif piece.piece_type == 'king':
            moves.extend(self._get_king_moves(pos, skip_king_check))

        return moves

    def is_in_check(self, color, board_state=None):
        """Check if the given color's king is in check"""
        if board_state is None:
            board = self.board.board
        else:
            board = board_state["board"]

        # Find king position
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece and piece.piece_type == 'king' and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        # Check if any opponent piece can attack the king
        opponent_color = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece and piece.color == opponent_color:
                    raw_moves = self._get_raw_moves((row, col), skip_king_check=True)
                    if king_pos in raw_moves:
                        return True
        return False

    def _get_king_moves(self, pos, skip_king_check=False):
        """Get all possible king moves including castling"""
        row, col = pos
        piece = self.board.get_piece(pos)
        moves = []
        
        # Normal moves
        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        
        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board.get_piece((new_row, new_col))
                if not target or target.color != piece.color:
                    moves.append((new_row, new_col))
        
        # Only check castling if not skipping king checks
        if not skip_king_check and not piece.has_moved and not self.is_in_check(piece.color):
            # Kingside castling
            rook = self.board.get_piece((row, 7))
            if (rook and not rook.has_moved and
                not any(self.board.get_piece((row, col)) for col in range(5, 7))):
                moves.append((row, 6))
            
            # Queenside castling
            rook = self.board.get_piece((row, 0))
            if (rook and not rook.has_moved and
                not any(self.board.get_piece((row, col)) for col in range(1, 4))):
                moves.append((row, 2))
        
        return moves
    
    def _get_pawn_moves(self, pos):
        """Get all possible pawn moves including captures and en passant"""
        row, col = pos
        piece = self.board.get_piece(pos)
        moves = []
        
        direction = 1 if piece.color == 'black' else -1
        
        # Forward move
        if 0 <= row + direction < 8 and not self.board.get_piece((row + direction, col)):
            moves.append((row + direction, col))
            
            # Initial two-square move
            if ((piece.color == 'black' and row == 1) or 
                (piece.color == 'white' and row == 6)):
                if not self.board.get_piece((row + 2*direction, col)):
                    moves.append((row + 2*direction, col))
        
        # Diagonal captures
        for dcol in [-1, 1]:
            new_row, new_col = row + direction, col + dcol
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                # Normal capture
                target = self.board.get_piece((new_row, new_col))
                if target and target.color != piece.color:
                    moves.append((new_row, new_col))
                
                # En passant
                elif self.board.last_double_pawn:
                    last_row, last_col = self.board.last_double_pawn
                    if (row == last_row and new_col == last_col and
                        ((piece.color == 'white' and row == 3) or 
                        (piece.color == 'black' and row == 4))):
                        moves.append((new_row, new_col))
        
        return moves

    def _get_knight_moves(self, pos):
        """Get all possible knight moves"""
        row, col = pos
        piece = self.board.get_piece(pos)
        moves = []
        
        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]
        
        for drow, dcol in knight_moves:
            new_row, new_col = row + drow, col + dcol
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board.get_piece((new_row, new_col))
                if not target or target.color != piece.color:
                    moves.append((new_row, new_col))
                    
        return moves

    def _get_diagonal_moves(self, pos):
        """Get all possible diagonal moves"""
        row, col = pos
        piece = self.board.get_piece(pos)
        moves = []
        
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board.get_piece((new_row, new_col))
                if not target:
                    moves.append((new_row, new_col))
                elif target.color != piece.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
                new_row += drow
                new_col += dcol
        
        return moves

    def _get_straight_moves(self, pos):
        """Get all possible straight moves"""
        row, col = pos
        piece = self.board.get_piece(pos)
        moves = []
        
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board.get_piece((new_row, new_col))
                if not target:
                    moves.append((new_row, new_col))
                elif target.color != piece.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
                new_row += drow
                new_col += dcol
        
        return moves

    def _can_castle_kingside(self, row, color):
        """Check if kingside castling is possible"""
        king = self.board.get_piece((row, 4))
        rook = self.board.get_piece((row, 7))
        
        if not (king and rook and 
                king.piece_type == 'king' and not king.has_moved and
                rook.piece_type == 'rook' and not rook.has_moved):
            return False
        
        # Check if squares between king and rook are empty
        if any(self.board.get_piece((row, col)) for col in range(5, 7)):
            return False
        
        # Check if squares the king moves through are attacked
        return not any(self.is_square_attacked((row, col), color) 
                    for col in range(4, 7))

    def _can_castle_queenside(self, row, color):
        """Check if queenside castling is possible"""
        king = self.board.get_piece((row, 4))
        rook = self.board.get_piece((row, 0))
        
        if not (king and rook and 
                king.piece_type == 'king' and not king.has_moved and
                rook.piece_type == 'rook' and not rook.has_moved):
            return False
        
        # Check if squares between king and rook are empty
        if any(self.board.get_piece((row, col)) for col in range(1, 4)):
            return False
        
        # Check if squares the king moves through are attacked
        return not any(self.is_square_attacked((row, col), color) 
                    for col in range(2, 5))

    def is_square_attacked(self, pos, color):
        """Check if a square is attacked by any opponent piece"""
        opponent_color = 'black' if color == 'white' else 'white'
        
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece((row, col))
                if piece and piece.color == opponent_color:
                    # Skip king check to avoid recursion
                    if pos in self._get_raw_moves((row, col), skip_king_check=True):
                        return True
        return False
    
    def get_valid_moves(self, pos, checking_future=False):
        """Get all valid moves for a piece, considering checks and pins"""
        piece = self.board.get_piece(pos)
        if not piece:
            return []

        valid_moves = []
        raw_moves = self._get_raw_moves(pos)

        # For each potential move, create a copy of the board and try the move
        for move in raw_moves:
            # Create a temporary board to test the move
            temp_board = self.board.copy()
            
            # Make the move on the temporary board
            from_row, from_col = pos
            to_row, to_col = move
            
            temp_board.board[to_row][to_col] = temp_board.board[from_row][from_col]
            temp_board.board[from_row][from_col] = None
            
            # If this move doesn't leave our king in check, it's valid
            if not self.would_move_cause_check(piece.color, temp_board):
                valid_moves.append(move)

        return valid_moves

    def would_move_cause_check(self, color, board):
        """Check if the given board state would result in the given color being in check"""
        # Find king position
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece and piece.piece_type == 'king' and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False

        # Check if any opponent piece can attack the king
        opponent_color = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece and piece.color == opponent_color:
                    # Get raw moves to avoid recursion
                    raw_moves = self._get_raw_moves((row, col), skip_king_check=True)
                    if king_pos in raw_moves:
                        return True
        return False

    def is_piece_pinned(self, pos):
        """Check if a piece is pinned to its king"""
        piece = self.board.get_piece(pos)
        if not piece or piece.piece_type == 'king':
            return False

        # Get the position of our king
        king_pos = None
        for row in range(8):
            for col in range(8):
                p = self.board.get_piece((row, col))
                if p and p.piece_type == 'king' and p.color == piece.color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break

        # Temporarily remove the piece and see if the king would be in check
        row, col = pos
        original_piece = self.board.board[row][col]
        self.board.board[row][col] = None
        
        is_pinned = self.is_in_check(piece.color)
        
        # Restore the piece
        self.board.board[row][col] = original_piece
        
        return is_pinned

    def is_checkmate(self, color):
        """Check if the given color is in checkmate"""
        # If not in check, can't be checkmate
        if not self.is_in_check(color):
            return False

        # Check all pieces of this color
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece((row, col))
                if piece and piece.color == color:
                    # If any piece has valid moves, not checkmate
                    if self.get_valid_moves((row, col)):
                        return False
        return True

    def is_stalemate(self, color):
        """Check if the given color is in stalemate"""
        # If in check, can't be stalemate
        if self.is_in_check(color):
            return False

        # Check all pieces of this color
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece((row, col))
                if piece and piece.color == color:
                    # If any piece has valid moves, not stalemate
                    if self.get_valid_moves((row, col)):
                        return False
        return True
    
    def is_valid_move(self, from_pos, to_pos, checking_future=False):
        """Check if a move is valid without causing infinite recursion"""
        piece = self.board.get_piece(from_pos)
        if not piece:
            return False

        from_row, from_col = from_pos
        to_row, to_col = to_pos

        # Special handling for castling
        if piece.piece_type == 'king' and abs(from_col - to_col) == 2:
            # Verify basic castling conditions
            if piece.has_moved:
                return False
            if self.is_in_check(piece.color):
                return False
                
            # Check kingside castling
            if to_col == 6:
                rook = self.board.get_piece((from_row, 7))
                if not rook or rook.has_moved:
                    return False
                # Check if squares between king and rook are empty and not attacked
                for col in range(5, 7):
                    if (self.board.get_piece((from_row, col)) or 
                        self.is_square_attacked((from_row, col), piece.color)):
                        return False
                return True
                
            # Check queenside castling
            elif to_col == 2:
                rook = self.board.get_piece((from_row, 0))
                if not rook or rook.has_moved:
                    return False
                # Check if squares between king and rook are empty and not attacked
                for col in range(1, 4):
                    if self.board.get_piece((from_row, col)):
                        return False
                for col in range(2, 5):
                    if self.is_square_attacked((from_row, col), piece.color):
                        return False
                return True

        # Regular move validation
        raw_moves = self._get_raw_moves(from_pos, skip_king_check=True)
        if to_pos not in raw_moves:
            return False

        # If we're checking a future position, just verify raw moves
        if checking_future:
            return True

        # Otherwise, make the move on a copy of the board and check if it leaves us in check
        temp_board = self._create_board_copy()
        self._make_simple_move(temp_board, from_pos, to_pos)
        return not self.is_in_check(piece.color, {"board": temp_board})
    
    def _create_board_copy(self):
        """Create a simple copy of the board state without recursive validation"""
        new_board = [[None for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                piece = self.board.board[row][col]
                if piece:
                    new_piece = piece.copy()
                    new_board[row][col] = new_piece
        return new_board

    def _make_simple_move(self, board, from_pos, to_pos):
        """Make a move on the board without validation"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        board[to_row][to_col] = board[from_row][from_col]
        board[from_row][from_col] = None
    
    def get_square_name(self, row, col):
        """Convert row, col coordinates to algebraic notation (e.g., e4)"""
        files = 'abcdefgh'
        ranks = '87654321'
        return files[col] + ranks[row]

    def get_piece_symbol(self, piece):
        """Get the symbol for a piece (empty for pawns)"""
        if piece.piece_type == 'pawn':
            return ''
        symbols = {
            'knight': 'N',
            'bishop': 'B',
            'rook': 'R',
            'queen': 'Q',
            'king': 'K'
        }
        return symbols[piece.piece_type]

    def get_move_notation(self, from_pos, to_pos, is_capture=False, is_check=False, is_checkmate=False):
        """Convert a move to algebraic notation"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Get the piece that's moving
        piece = self.board.get_piece(from_pos)
        if not piece:
            return "invalid"  # Or handle this case as you prefer
        
        # Get basic move notation
        notation = self.get_piece_symbol(piece)
        
        # Add starting square for pawns if it's a capture
        if piece.piece_type == 'pawn' and is_capture:
            notation += self.get_square_name(from_row, from_col)[0]
        
        # Add 'x' for captures
        if is_capture:
            notation += 'x'
        
        # Add destination square
        notation += self.get_square_name(to_row, to_col)
        
        # Handle pawn promotion
        if piece.piece_type == 'pawn' and (to_row == 0 or to_row == 7):
            notation += '=Q'  # Assuming always promoting to queen for now
        
        # Add check or checkmate symbol
        if is_checkmate:
            notation += '#'
        elif is_check:
            notation += '+'
        
        return notation