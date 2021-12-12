import os

UP = -1
DOWN = 1
LEFT = -1
RIGHT = 1

ROW = 0
COL = 1

BLACK = "Black"
WHITE = "White"

PAWN = "P"
KNIGHT = "k"
BISHOP = "B"
ROOK = "R"
QUEEN = "Q"
KING = "K"

VALUES = {
    PAWN: 1,
    KNIGHT: 3,
    BISHOP: 3,
    ROOK: 5,
    QUEEN: 9,
    KING: 1000
}

HORIZONTALS = [(LEFT, 0), (RIGHT, 0)]
VERTICALS = [(0, UP), (0, DOWN)]
DIAGONALS = [(LEFT, UP), (RIGHT, UP), (LEFT, DOWN), (RIGHT, DOWN)]

def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

def in_bounds(pos):
    if pos[ROW] in range(8) and pos[COL] in range(8):
        return True
    return False

class Piece:
    def __init__(self, pos, type, colour):
        self.pos = pos
        self.type = type
        self.colour = colour

    def __str__(self):
        return self.type

    def set_pos(self, pos):
        if not in_bounds(pos):
            raise ValueError("Row/Col must be between 0 and 8")
        self.pos = pos

    def get_pos(self):
        return self.pos

    def get_colour(self):
        return self.colour

    def get_type(self):
        return self.type

    def moves_in_line(self, board, increments):
        moves = []
        for col_iter, row_iter in increments:
            row = self.pos[ROW] + row_iter
            col = self.pos[COL] + col_iter
            while in_bounds((row, col)):
                target_piece = board.get_piece(row, col)
                if target_piece is None:
                    moves.append((row, col))
                else:
                    if target_piece.get_colour() != self.colour:
                        moves.append((row, col))
                    break
                row += row_iter
                col += col_iter
        
        return moves



class Pawn(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, PAWN, colour)
        self.__direction = DOWN if colour == WHITE else UP
        self.__has_moved = False

    def available_moves(self, board):
        moves = []
        next_row = self.pos[ROW] + self.__direction
        col = self.pos[COL]
        if next_row in range(8):

            # Moving pawn forward if nothing in front of it
            if board.get_piece(next_row, col) is None:
                moves.append((next_row, col))
            
            # Moving pawn 2 places forward if nothing in front of it and has not yet moved
            if board.get_piece(next_row + self.__direction, col) is None and not self.__has_moved:
                moves.append((next_row + self.__direction, col))
                self.has_moved = True

            # Moving pawn diagonally forward left if there is an enemy piece there
            if (col + LEFT in range(8) and board.get_piece(next_row, col - 1) is not None
                    and board.get_piece(next_row, col - 1).get_colour() != self.colour):
                moves.append((next_row, col - 1))

            # Moving pawn diagonally forward right if there is an enemy piece there
            if (col + RIGHT in range(8) and board.get_piece(next_row, col + 1) is not None
                    and board.get_piece(next_row, col + 1).get_colour() != self.colour):
                moves.append((next_row, col + 1))

        return moves


class Knight(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, KNIGHT, colour)

    def available_moves(self, board):
        moves = []

        row = self.pos[ROW]
        col = self.pos[COL]
        KNIGHT_MOVES = [(row + 1, col + 2), (row + 1, col - 2), (row + 2, col + 1),
                        (row + 2, col - 1), (row - 1, col + 2), (row - 1, col - 2),
                        (row - 2, col + 1), (row - 2, col - 1)]

        for trial_pos in KNIGHT_MOVES:
            if in_bounds(trial_pos):
                piece = board.get_piece(trial_pos[ROW], trial_pos[COL])

                if piece is None or piece.get_colour() != self.colour:
                    moves.append(trial_pos)

        return moves

class Bishop(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, BISHOP, colour)
    
    def available_moves(self, board):
        return self.moves_in_line(board, DIAGONALS)

class Rook(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, ROOK, colour)
    
    def available_moves(self, board):
        return self.moves_in_line(board, HORIZONTALS + VERTICALS)

class Queen(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, QUEEN, colour)
    
    def available_moves(self, board):
        return self.moves_in_line(board, HORIZONTALS + VERTICALS + DIAGONALS)

class King(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, KING, colour)
    
    def available_moves(self, board):
        moves = []
        
        opposing_pieces = board.get_pieces(BLACK) if self.colour == WHITE else board.get_pieces(WHITE)
        
        row = self.pos[ROW]
        col = self.pos[COL]

        # Removing King from list of opposing pieces (King is first piece in list)
        opposing_pieces = opposing_pieces[1:]
        opposing_moves = []
        for piece in opposing_pieces:
            opposing_moves += piece.available_moves(board)
        
        for row in [row - 1, row, row + 1]:
            for col in [col - 1, col, col + 1]:
                if row in range(8) and col in range(8) and not (row == col == 0):
                    piece = board.get_piece(row, col)
                    if (piece is None or piece.get_colour() != self.colour) and (row, col) not in opposing_moves:
                        moves.append((row, col))

        # TODO Add castling feature

        return moves
        
    def is_in_check(self, board):
        opposing_pieces = board.get_pieces(BLACK) if self.colour == WHITE else board.get_pieces(WHITE)
        
        # Removing King from list of opposing pieces (King is first piece in list)
        opposing_pieces = opposing_pieces[1:]
        opposing_moves = []
        for piece in opposing_pieces:
            opposing_moves += piece.available_moves(board)

        return self.curr_pos() in opposing_moves

class Board:
    def __init__(self):
        self.grid = [[None for x in range(8)] for y in range(8)]

        # Pawns
        self.grid[1] = [Pawn((1, x), WHITE) for x in range(8)]
        self.grid[6] = [Pawn((6, x), BLACK) for x in range(8)]

        pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        self.grid[0] = [piece((0, index), WHITE) for index, piece in enumerate(pieces)]
        self.grid[7] = [piece((7, index), BLACK) for index, piece in enumerate(pieces)]
        
        self.white_king = self.grid[0][4]
        self.black_king = self.grid[7][4]

        self.white_pieces = []
        for row in self.grid[0:2]:
            for piece in row:
                self.white_pieces.append(piece)
        self.white_pieces.sort(key= lambda piece: VALUES[piece.get_type()], reverse= True)

        self.black_pieces = []
        for row in self.grid[6:8]:
            for piece in row:
                self.black_pieces.append(piece)
        self.black_pieces.sort(key= lambda piece: VALUES[piece.get_type()], reverse= True)

        self.turn = 0
        self.check  = {
            WHITE: {'in_check': False, 'pieces_causing_check': []},
            BLACK: {'in_check': False, 'pieces_causing_check': []}
        }
        self.winner = None

    def __str__(self):
        grid_str = ""
        for index, row in enumerate(self.grid):
            for element in row:
                if element is None:
                    grid_str += "."
                else:
                    grid_str += element.__str__()
            if index != len(self.grid) - 1:
                grid_str += '\n'

        return grid_str
    
    def get_pieces(self, colour):
        return self.white_pieces if colour == WHITE else self.black_pieces
    
    def get_pieces_str(self, colour):
        pieces = self.white_pieces if colour == WHITE else self.black_pieces
        return [f"{piece.get_type()} {piece.get_pos()}" for piece in pieces]        

    def move_piece(self, curr_row, curr_col, new_row, new_col):
        if not (in_bounds((curr_row, curr_col)) and in_bounds((new_row, new_col))):
            raise ValueError("Coordinates not between 0 and 7")
        
        piece = self.grid[curr_row][curr_col]

        if piece is None:
            raise ValueError("No piece selected")

        player = self.whose_turn()
        
        if piece.get_colour() != player:
            raise ValueError("Cannot move an opponents piece")

        if (new_row, new_col) not in piece.available_moves(self):
            raise ValueError("Move not valid")
        
        target_piece = self.grid[new_row][new_col]
        
        # Capture opposing target_piece
        if target_piece is not None:
            if target_piece.get_colour() == BLACK:
                self.black_pieces.remove(target_piece)
                if piece in self.check[WHITE]['pieces_causing_check']:
                    self.check[WHITE]['pieces_causing_check'].remove(piece)
                    self.check[WHITE]['in_check'] = len(self.check[WHITE]['pieces_causing_check']) > 1
            else:
                self.white_pieces.remove(target_piece)
                if piece in self.check[BLACK]['pieces_causing_check']:
                    self.check[BLACK]['pieces_causing_check'].remove(piece)
                    self.check[BLACK]['in_check'] = len(self.check[BLACK]['pieces_causing_check']) > 1
        
        # # If you are in check your next move has to take you out of check
        # # If you are in check mate, you lose

        # temp_new = self.grid[new_row][new_col]

        piece.set_pos((new_row, new_col))
        self.grid[curr_row][curr_col] = None
        self.grid[new_row][new_col] = piece


        # Place Oppossing King in Check
        new_available_moves = piece.available_moves(self)
        if piece.get_colour() == WHITE and self.black_king.get_pos() in new_available_moves:
            self.check[BLACK]['in_check'] = True
            self.check[BLACK]['pieces_causing_check'].append(piece)
        elif piece.get_colour() == BLACK and self.white_king.get_pos() in new_available_moves:
            self.check[WHITE]['in_check'] = True
            self.check[WHITE]['pieces_causing_check'].append(piece)
        
        # player_in_check_last_round = self.check[player]
        # player_in_check_this_round = self.white_king.is_in_check(self)

        # # If you started the turn already in check, then you have to take youself out of check
        # if player_in_check_last_round and player_in_check_this_round:
        #     self.grid[curr_row][curr_col] = piece
        #     self.grid[new_row][new_col] = temp_new
        #     piece.set_pos(curr_row, curr_col)
        #     raise ValueError("Player must take themself out of check")
        
        # # Cannot do a move that results in yourself being put in check
        # if player_in_check_this_round:
        #     self.grid[curr_row][curr_col] = piece
        #     self.grid[new_row][new_col] = temp_new
        #     piece.set_pos(curr_row, curr_col)
        #     raise ValueError("Player cannot put themselves in check")
        

        # self.check[WHITE] = player_in_check_this_round
        # self.check[BLACK] = self.black_king.is_in_check(self)

        # # Checking if either player is in checkmate
        # if self.check[WHITE] and len(self.white_king.available_moves()) == 0:
        #     self.winner = BLACK
        # if self.check[BLACK] and len(self.black_king.available_moves()) == 0:
        #     self.winner = WHITE

        self.turn += 1

    def piece_at_pos(self, row, col):
        if self.grid[row][col] is None:
            return None
        else:
            return self.grid[row][col].get_type()
    
    def get_piece(self, row, col):
        return self.grid[row][col]

    def whose_turn(self):
        if self.turn % 2 == 0:
            return WHITE
        else:
            return BLACK


if __name__ == '__main__':
    b = Board()

    while b.winner is None:
        #clear_console()
        print("==========")
        print(b)
        print(f"White - {b.get_pieces_str(WHITE)}, Black - {b.get_pieces_str(BLACK)}")

        # try:
        input1 = input(f"Player {b.whose_turn()} - Enter current row/col: ").split()
        curr_row, curr_col = int(input1[0]), int(input1[1])
        input2 = input(f"{b.piece_at_pos(curr_row, curr_col)} - Move to row/col: ").split()
        new_row, new_col = int(input2[0]), int(input2[1])
            # try:
        b.move_piece(curr_row, curr_col, new_row, new_col)
            # except ValueError:
        print("Invalid move")
        # except (ValueError, IndexError):
        print("Please enter 2 numbers for row/col coordinates")
    
    print(f"Congrats {b.winner}, you win!!!")