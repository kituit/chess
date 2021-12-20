import pygame
import pygame.freetype
from chess import KING, QUEEN, BISHOP, ROOK, KNIGHT, PAWN, BLACK, STALEMATE, WHITE, Board, ROW, COL

BLACK_TEXT = (0, 0, 0)
BLACK_COLOUR = (189,183,107)
WHITE_COLOUR = (255, 255, 224)
MOVE_COLOUR = (0, 0, 150)
CHECK_COLOUR = (150, 0, 0)

BOARD_SIZE = 1000 # Must be divisible by 8 to display correctly, as needs to be evenly divided into 8 x 8 grid
DISPLAY_DIMENSIONS = (BOARD_SIZE, BOARD_SIZE + 100)
SQUARE_SIZE = BOARD_SIZE // 8

SPRITES_FILE = "img/sprites.png"

FPS = 10

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

def get_checking_pieces_pos(board):
    return [piece.get_pos() for piece in b.check[b.whose_turn()]['pieces_causing_check']]

def displayBoard(win, b, moves):
    
    # Clear display
    win.fill((255, 255, 255))
    
    # Create Checkered Grid
    for col in range(8):
        for row in range(8):
            if (row, col) in moves:
                colour = MOVE_COLOUR
            elif (row, col) in get_checking_pieces_pos(b):
                colour = CHECK_COLOUR
            elif (col + row) % 2 == 0:
                colour = BLACK_COLOUR
            else:
                colour = WHITE_COLOUR
            pygame.draw.rect(win, colour, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    # Diplay Pieces
    for piece in b.get_pieces(WHITE) + b.get_pieces(BLACK):
        colour = piece.get_colour()
        piece_type = piece.get_type()
        pos = piece.get_pos()
        row, col = pos[ROW], pos[COL]
        win.blit(sprites.get_image(*SPRITES_CORDS[colour][piece_type]['location'], *SPRITES_CORDS[colour][piece_type]['dimensions']), (col * SQUARE_SIZE, row * SQUARE_SIZE))

    # Adding Text
    if b.winner is None:
        text_str = f"Player {b.whose_turn()}"
    elif b.winner == STALEMATE:
        text_str = "Stalemate!!!"
    else:
        text_str = f"Player {b.winner} has won!"
    text_rect = ft_font.get_rect(text_str)
    text_rect.center = (win.get_rect().midbottom[0], win.get_rect().midbottom[1] - text_rect.height)
    ft_font.render_to(win, text_rect.topleft, text_str, BLACK_TEXT)

# initialize all imported pygame modules
pygame.init()
ft_font = pygame.freetype.SysFont('Sans', 50)

win = pygame.display.set_mode(DISPLAY_DIMENSIONS)

pygame.display.set_caption("Chess")

sprites = SpriteSheet()
b = Board()

run = True

clock = pygame.time.Clock()

selected_piece = None
moves = []
while run and b.winner is None:
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
                b.move_piece(*selected_piece.get_pos(), *square_coords)
                selected_piece = None
                moves = []
            # Has not already selected piece, choosing piece to move
            else:
                selected_piece = b.get_piece(square_coords[ROW], square_coords[COL])
                if selected_piece is not None and selected_piece.get_colour() == b.whose_turn():
                    moves = selected_piece.available_moves(b)
                    print(moves)
                else:
                    moves = []
    
    # Display Game Board
    displayBoard(win, b, moves)
    pygame.display.update()

while run:
    pygame.time.delay(5)

    # Get all events
    ev = pygame.event.get()
    for event in ev:

        # Quit Game
        if event.type == pygame.QUIT:
            run = False

