import os
import sys
os.environ['SDL_AUDIODRIVER'] = 'dsp'
import pygame
import pygame.freetype
from chess import KING, QUEEN, BISHOP, ROOK, KNIGHT, PAWN, BLACK, STALEMATE, WHITE, Board, ROW, COL, in_bounds

MODE_DEFAULT = "--default"
MODE_FLASK = "--flask"
MODE_MQTT = "--mqtt"
MQTT_HIGH_LATENCY = "--highlatency"

if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == MODE_DEFAULT):
    MODE = MODE_DEFAULT
elif len(sys.argv) == 3 and sys.argv[1] == MODE_FLASK:
    MODE = MODE_FLASK
elif len(sys.argv) >= 3 and sys.argv[1] == MODE_MQTT:
    MODE = MODE_MQTT
else:
    raise ValueError("Invalid command line args")

if MODE == MODE_MQTT:
    from client_mqtt import ChessMqttClient
elif MODE == MODE_FLASK:
    from client_flask import ChessFlaskClient

# Colours (r, g, b)
BLACK_TEXT = (0, 0, 0)
BLACK_COLOUR = (189,183,107)
WHITE_COLOUR = (255, 255, 224)
MOVE_COLOUR = (0, 0, 150)
CHECK_COLOUR = (150, 0, 0)
PREVIOUS_MOVE_COLOUR = (149, 0, 255)

# GUI Size Constants
BOARD_SIZE = 1000 # Must be divisible by 8 to display correctly, as needs to be evenly divided into 8 x 8 grid
SQUARE_SIZE = BOARD_SIZE // 8
DISPLAY_DIMENSIONS = (BOARD_SIZE, BOARD_SIZE + SQUARE_SIZE)
FONT_SIZE = SQUARE_SIZE // 2

SPRITES_FILE = "src/img/sprites.png"
FPS = 7

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

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Quit(Exception):
    pass

class SpriteSheet(object):
    """ Class used to grab images out of a sprite sheet. """

    def __init__(self):
        # Load the sprite sheet.
        self.sprite_sheet = pygame.image.load(resource_path(SPRITES_FILE))

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

    def drawBoard(self, board, moves=[]):
        # Clear display
        self.win.fill((255, 255, 255))
        
        # Create Checkered Grid
        for col in range(8):
            for row in range(8):
                if (row, col) in moves:
                    colour = MOVE_COLOUR
                elif (row, col) in board.get_checking_pieces_pos(board.whose_turn()):
                    colour = CHECK_COLOUR
                elif (row, col) == board.get_previous_move_pos():
                    colour = PREVIOUS_MOVE_COLOUR
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
        
        # Update display
        pygame.display.update()
        
    def drawText(self, text_str):
        text_rect = self.font.get_rect(text_str)
        text_rect.center = (self.win.get_rect().midbottom[0], self.win.get_rect().midbottom[1] - text_rect.height)
        self.font.render_to(self.win, text_rect.topleft, text_str, BLACK_TEXT)

        # Update display
        pygame.display.update()

class Game():

    def __init__(self):
        self.gui = Gui()
        self.board = Board()
        self.clock = pygame.time.Clock()
        self.server_config = None
        self.mqtt = None
        self.flask = None

        if MODE == MODE_FLASK:
            self.flask = ChessFlaskClient(sys.argv[2], self.board)
        elif MODE == MODE_MQTT:
            qos = 0
            if len(sys.argv) == 4 and sys.argv[3] == MQTT_HIGH_LATENCY:
                qos = 2
            self.mqtt = ChessMqttClient(sys.argv[2], self.board, qos)
            self.mqtt.start()
        else:
            self.server_config = None


    def displayMove(self, moves):
        self.gui.drawBoard(self.board, moves=moves)

        if self.board.winner is None:
            text_str = f"Player {self.board.whose_turn()}"
        elif self.board.winner == STALEMATE:
            text_str = "Stalemate!!!"
        else:
            text_str = f"Player {self.board.winner} has won!"
        self.gui.drawText(text_str)
    
    def displayWaiting(self):
        self.gui.drawBoard(self.board)
        self.gui.drawText("Waiting for other player")
    
    def displayForfeit(self):
        self.gui.drawBoard(self.board)
        self.gui.drawText("Opponent has forfeited")
    
    def is_active(self):
        active = True
        if MODE == MODE_FLASK:
            active = self.flask.is_active()
        elif MODE == MODE_MQTT:
            active = self.mqtt.is_active()
        
        return active
    
    def is_waiting(self):
        waiting = False
        if MODE == MODE_FLASK:
            waiting = self.flask.is_waiting()
        if MODE == MODE_MQTT:
            waiting = self.mqtt.is_waiting()

        return waiting

    def playPrologue(self):
        self.displayWaiting()
        while True:
            if MODE == MODE_FLASK and self.flask.is_active_force_check():
                break
            elif MODE == MODE_MQTT and self.mqtt.is_active():
                break
            
            self.clock.tick(FPS)

            # Get all events
            ev = pygame.event.get()
            for event in ev:

                # Quit Game
                if event.type == pygame.QUIT:
                    raise Quit

    def playMain(self):
        selected_piece = None
        moves = []
        while self.board.winner is None and self.is_active():
            self.clock.tick(FPS)

            waiting = self.is_waiting()
    
            # Get all events
            ev = pygame.event.get()
            for event in ev:

                # Quit Game
                if event.type == pygame.QUIT:
                    raise Quit

                if not waiting:
                # Click on piece 
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        moves, selected_piece = self.doMove(pos, selected_piece, moves)
            
            # Display Game Board
            if waiting:
                self.displayWaiting()
            else:
                self.displayMove(moves)

    def doMove(self, pos, selected_piece, moves):
        square_coords = (pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE)
        if in_bounds(square_coords):
            
            # Deselect piece
            if selected_piece is not None and selected_piece == self.board.get_piece(*square_coords):
                selected_piece = None
                moves = []
            
            # If has already selected piece, choosing where to move piece
            elif selected_piece is not None and square_coords in moves:
                start_pos, end_pos = selected_piece.get_pos(), square_coords
                self.board.move_piece(*start_pos, *end_pos)
                if MODE == MODE_FLASK:
                    self.displayWaiting() # Added redraw before publish to avoid latency waiting for http response
                    self.flask.publish_move(start_pos, end_pos)
                elif MODE == MODE_MQTT:
                    self.mqtt.publish_move(start_pos, end_pos)

                selected_piece = None
                moves = []

            # Has not already selected piece, choosing piece to move
            else:
                selected_piece = self.board.get_piece(square_coords[ROW], square_coords[COL])
                if selected_piece is not None and selected_piece.get_colour() == self.board.whose_turn():
                    moves = selected_piece.available_moves(self.board)
                    print(moves)
                else:
                    moves = []
        
        return moves, selected_piece


    def playEpilogue(self):
        if (MODE == MODE_MQTT and self.mqtt.opponent_has_quit()) or (MODE == MODE_FLASK and self.flask.opponent_has_quit()):
            self.displayForfeit()

        run = True
        while run:
            self.clock.tick(FPS)

            # Get all events
            ev = pygame.event.get()
            for event in ev:

                # Quit Game
                if event.type == pygame.QUIT:
                    raise Quit

    def play(self):
        
        try:
            if MODE in [MODE_FLASK, MODE_MQTT]:
                self.playPrologue()
            self.playMain()
            self.playEpilogue()
        except (Quit, KeyboardInterrupt):
            print("Goodbye")        
        
        if MODE == MODE_FLASK:
            self.flask.publish_quit()
        elif MODE == MODE_MQTT:
            self.mqtt.publish_quit()


if __name__ == '__main__':
    g = Game()
    g.play()


