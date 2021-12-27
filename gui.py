import os
os.environ['SDL_AUDIODRIVER'] = 'dsp'
import pygame
import pygame.freetype
from chess import KING, QUEEN, BISHOP, ROOK, KNIGHT, PAWN, BLACK, STALEMATE, WHITE, Board, ROW, COL

# Colours (r, g, b)
BLACK_TEXT = (0, 0, 0)
BLACK_COLOUR = (189,183,107)
WHITE_COLOUR = (255, 255, 224)
MOVE_COLOUR = (0, 0, 150)
CHECK_COLOUR = (150, 0, 0)

# GUI Size Constants
BOARD_SIZE = 1000 # Must be divisible by 8 to display correctly, as needs to be evenly divided into 8 x 8 grid
SQUARE_SIZE = BOARD_SIZE // 8
DISPLAY_DIMENSIONS = (BOARD_SIZE, BOARD_SIZE + SQUARE_SIZE)
FONT_SIZE = SQUARE_SIZE // 2

SPRITES_FILE = "img/sprites.png"

FPS = 10

# initialize all imported pygame modules
pygame.init()

SPRITES_CORDS = {
    WHITE : {
        KING: {'location': (21, 23), 'dimensions': (170, 170)},
        QUEEN: {'location': (227, 20), 'dimensions': (185, 172)},
        BISHOP: {'location': (449, 20), 'dimensions': (168, 172)},
        KNIGHT: {'location': (661, 27), 'dimensions': (165, 165)},
        ROOK: {'location': (888, 34), 'dimensions': (144, 159)},
        PAWN: {'location': (1106, 37), 'dimensions': (131, 158)}
    },
    BLACK : {
        KING: {'location': (21, 236), 'dimensions': (170, 170)},
        QUEEN: {'location': (227, 237), 'dimensions': (185, 175)},
        BISHOP: {'location': (449, 234), 'dimensions': (168, 172)},
        KNIGHT: {'location': (661, 241), 'dimensions': (165, 165)},
        ROOK: {'location': (888, 247), 'dimensions': (144, 159)},
        PAWN: {'location': (1106, 251), 'dimensions': (131, 158)}
    }
}

class SpriteSheet(object):
    """ Class used to grab images out of a sprite sheet. """

    def __init__(self):
        # Load the sprite sheet.
        self.sprite_sheet = pygame.image.load(SPRITES_FILE)

    def get_image(self, x, y, width, height):
        """ Grab a single image out of a larger spritesheet
            Pass in the x, y location of the sprite
            and the width and height of the sprite. """
        # Create a new blank image
        image = pygame.Surface([width, height], pygame.SRCALPHA)
        
        # Copy the sprite from the large sheet onto the smaller image
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        
        # Scale image to size of square
        image = pygame.transform.smoothscale(image, (SQUARE_SIZE, SQUARE_SIZE))
        
        # Return the image
        return image

class Gui():

    def __init__(self):
        self.win = pygame.display.set_mode(DISPLAY_DIMENSIONS)
        pygame.display.set_caption("Chess")
        self.sprites = SpriteSheet()
        self.font = pygame.freetype.SysFont('Sans', FONT_SIZE)

    def updateDisplay(self, board, moves):
        # Clear display
        self.win.fill((255, 255, 255))
        
        # Create Checkered Grid
        for col in range(8):
            for row in range(8):
                if (row, col) in moves:
                    colour = MOVE_COLOUR
                elif (row, col) in board.get_checking_pieces_pos(board.whose_turn()):
                    colour = CHECK_COLOUR
                elif (col + row) % 2 == 0:
                    colour = BLACK_COLOUR
                else:
                    colour = WHITE_COLOUR
                pygame.draw.rect(self.win, colour, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        
        # Diplay Pieces
        for piece in board.get_pieces(WHITE) + board.get_pieces(BLACK):
            colour = piece.get_colour()
            piece_type = piece.get_type()
            pos = piece.get_pos()
            row, col = pos[ROW], pos[COL]
            self.win.blit(self.sprites.get_image(*SPRITES_CORDS[colour][piece_type]['location'], *SPRITES_CORDS[colour][piece_type]['dimensions']), (col * SQUARE_SIZE, row * SQUARE_SIZE))

        # Adding Text
        if board.winner is None:
            text_str = f"Player {board.whose_turn()}"
        elif board.winner == STALEMATE:
            text_str = "Stalemate!!!"
        else:
            text_str = f"Player {board.winner} has won!"
        text_rect = self.font.get_rect(text_str)
        text_rect.center = (self.win.get_rect().midbottom[0], self.win.get_rect().midbottom[1] - text_rect.height)
        self.font.render_to(self.win, text_rect.topleft, text_str, BLACK_TEXT)

        # Update display
        pygame.display.update()

def game(gui, board, clock):

    selected_piece = None
    moves = []
    run = True
    while run and board.winner is None:
        clock.tick(FPS)

        # Get all events
        ev = pygame.event.get()
        for event in ev:

            # Quit Game
            if event.type == pygame.QUIT:
                run = False

            # Click on piece 
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                square_coords = (pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE)

                # If has already selected piece, choosing where to move piece
                if selected_piece is not None and square_coords in moves:
                    board.move_piece(*selected_piece.get_pos(), *square_coords)
                    selected_piece = None
                    moves = []
                # Has not already selected piece, choosing piece to move
                else:
                    selected_piece = board.get_piece(square_coords[ROW], square_coords[COL])
                    if selected_piece is not None and selected_piece.get_colour() == board.whose_turn():
                        moves = selected_piece.available_moves(board)
                        print(moves)
                    else:
                        moves = []
        
        # Display Game Board
        gui.updateDisplay(board, moves)
    
    return run

def epilogue(gui, clock):
    run = True
    while run:
        clock.tick(FPS)

        # Get all events
        ev = pygame.event.get()
        for event in ev:

            # Quit Game
            if event.type == pygame.QUIT:
                run = False

if __name__ == '__main__':
    gui = Gui()
    board = Board()
    clock = pygame.time.Clock()

    if game(gui, board, clock):
        epilogue(gui, clock)
