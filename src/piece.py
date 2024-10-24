import os
import pygame
from .constants import *

def load_piece_image(piece_type, color):
    """Load PNG piece image"""
    color_prefix = 'w' if color == 'white' else 'b'
    file_path = os.path.join('pieces', f'{piece_type}-{color_prefix}.png')
    
    try:
        image = pygame.image.load(file_path)
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