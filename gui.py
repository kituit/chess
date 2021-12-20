import pygame
import time
from chess import KING, QUEEN, BISHOP, ROOK, KNIGHT, PAWN, BLACK, WHITE, Board, ROW, COL

BLACK_COLOUR = (189,183,107)
WHITE_COLOUR = (255, 255, 224)
MOVE_COLOUR = (0, 0, 150)
BOARD_SIZE = 1000 # Must be divisible by 8 to display correctly, as needs to be evenly divided into 8 x 8 grid
SQUARE_SIZE = BOARD_SIZE // 8
SPRITES_FILE = "img/sprites.png"

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



pygame.init()

win = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))

pygame.display.set_caption("Chess")

sprites = SpriteSheet()
b = Board()

run = True

def displayBoard(win, b, moves):
    win.fill((0,0,0))
    for x in range(8):
        for y in range(8):
            if (y, x) in moves:
                colour = MOVE_COLOUR
            elif (x + y) % 2 == 0:
                colour = BLACK_COLOUR
            else:
                colour = WHITE_COLOUR
            pygame.draw.rect(win, colour, (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    for piece in b.get_pieces(WHITE) + b.get_pieces(BLACK):
        colour = piece.get_colour()
        piece_type = piece.get_type()
        pos = piece.get_pos()
        row, col = pos[ROW], pos[COL]
        win.blit(sprites.get_image(*SPRITES_CORDS[colour][piece_type]['location'], *SPRITES_CORDS[colour][piece_type]['dimensions']), (col * SQUARE_SIZE, row * SQUARE_SIZE))


selected_piece = None
moves = []
while run and b.winner == None:
    pygame.time.delay(5)
    
    displayBoard(win, b, moves)

    # get all events
    ev = pygame.event.get()

    # proceed events
    for event in ev:

        if event.type == pygame.QUIT:
            run = False

        # handle MOUSEBUTTONUP
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            square_coords = (pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE)

            if selected_piece is not None and square_coords in moves:
                b.move_piece(*selected_piece.get_pos(), *square_coords)
                selected_piece = None
                moves = []
            else:
                selected_piece = b.get_piece(square_coords[ROW], square_coords[COL])
                if selected_piece is not None and selected_piece.get_colour() == b.whose_turn():
                    moves = selected_piece.available_moves(b)
                    print(moves)
                else:
                    moves = []
      
    pygame.display.update()


