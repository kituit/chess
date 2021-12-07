# Hello World

BLACK = "Black"
WHITE = "White"

PAWN = "P"
KNIGHT = "K"

VALUES = {
    PAWN : 1,
    KNIGHT : 3
}

class Piece:
    def __init__(self, pos_row, pos_col, colour):
        self.row = pos_row
        self.col = pos_col
        self.colour = colour

    def set_pos(self, pos_row, pos_col):
        if pos_row not in range(8) or pos_col not in range(8):
            raise ValueError("Row/Col must be between 0 and 8")

        self.row = pos_row
        self.col = pos_col

    def curr_pos(self):
        return (self.row, self.col)

    def get_colour(self):
        return self.colour


class Pawn(Piece):
    def __init__(self, row, col, colour):
        Piece.__init__(self, row, col, colour)
        self.type = PAWN

    def __str__(self):
        return PAWN

    def get_type(self):
        return self.type

    def available_moves(self, grid):

        moves = []

        next_row = self.row + (-1 if self.colour == BLACK else 1)

        if next_row in range(8):

            # Moving pawn forward if nothing in front of it
            if grid[next_row][self.col] is None:
                moves.append((next_row, self.col))

            # Moving pawn diagonally forward if there is an enemy piece there
            if (self.col - 1 in range(8) and grid[next_row][self.col - 1] is not None
                    and grid[next_row][self.col - 1].get_colour() != self.colour):
                moves.append((next_row, self.col - 1))

            # Moving pawn diagonally forward if there is an enemy piece there
            if (self.col + 1 in range(8) and grid[next_row][self.col + 1] is not None
                    and grid[next_row][self.col + 1].get_colour() != self.colour):
                moves.append((next_row, self.col + 1))

        return moves


class Knight(Piece):
    def __init__(self, row, col, colour):
        Piece.__init__(self, row, col, colour)
        self.type = KNIGHT

    def __str__(self):
        return KNIGHT

    def get_type(self):
        return self.type

    def available_moves(self, grid):
        moves = []

        row = self.row
        col = self.col
        KNIGHT_MOVES = [(row + 1, col + 2), (row + 1, col - 2), (row + 2, col + 1),
                        (row + 2, col - 1), (row - 1, col + 2), (row - 1, col - 2),
                        (row - 2, col + 1), (row - 2, col - 1)]

        for trial_row, trial_col in KNIGHT_MOVES:
            if trial_row in range(8) and trial_col in range(8):
                piece = grid[trial_row][trial_col]

                if piece is None or piece.colour != self.colour:
                    moves.append((trial_row, trial_col))

        return moves


class Board:
    def __init__(self):
        self.grid = [[None for x in range(8)] for y in range(8)]

        # Pawns
        self.grid[1] = [Pawn(1, x, WHITE) for x in range(8)]
        self.grid[6] = [Pawn(6, x, BLACK) for x in range(8)]

        # Knights
        self.grid[0][1] = Knight(0, 1, WHITE)
        self.grid[0][6] = Knight(0, 6, WHITE)
        self.grid[7][1] = Knight(7, 1, BLACK)
        self.grid[7][6] = Knight(7, 6, BLACK)

        self.white_pieces = []
        for row in self.grid[0:2]:
            for piece in row:
                if piece is not None:
                    self.white_pieces.append(piece)
        self.white_pieces.sort(key= lambda piece: VALUES[piece.get_type()])

        self.black_pieces = []
        for row in self.grid[6:7]:
            for piece in row:
                if piece is not None:
                    self.black_pieces.append(piece)
        self.black_pieces.sort(key= lambda piece: VALUES[piece.get_type()])

    def __str__(self):
        grid_str = ""
        for index, row in enumerate(self.grid):
            for element in row:
                if element is None:
                    grid_str += " "
                else:
                    grid_str += element.__str__()
            if index != len(self.grid) - 1:
                grid_str += '\n'

        return grid_str
    
    def get_pieces(self, colour):
        if colour == BLACK:
            return self.black_pieces
        else:
            return self.white_pieces
    
    def get_pieces_str(self, colour):
        pieces = self.white_pieces if colour == WHITE else self.black_pieces
        return [f"{piece.get_type()} {piece.curr_pos()}" for piece in pieces]        

    def move_piece(self, curr_row, curr_col, new_row, new_col):
        piece = self.grid[curr_row][curr_col]

        if (new_row, new_col) not in piece.available_moves(self.grid):
            raise ValueError("Move not valid")
        
        target_piece = self.grid[new_row][new_col]
        if target_piece is not None:
            if target_piece.get_colour() == BLACK:
                self.black_pieces.remove(target_piece)
            else:
                self.white_pieces.remove(target_piece)

        piece.set_pos(new_row, new_col)
        self.grid[curr_row][curr_col] = None
        self.grid[new_row][new_col] = piece

    def piece_at_pos(self, row, col):
        if self.grid[row][col] is None:
            return None
        else:
            return self.grid[row][col].get_type()


if __name__ == '__main__':
    b = Board()
    print(b)

    print("==========")

    while True:
        print("Piece:")
        curr_row = int(input("Row: "))
        curr_col = int(input("Col: "))
        print(f"{b.piece_at_pos(curr_row, curr_col)} - Move:")
        new_row = int(input("Row: "))
        new_col = int(input("Col: "))

        try:
            b.move_piece(curr_row, curr_col, new_row, new_col)
            print(b)
            print(f"White pieces: {b.get_pieces_str(WHITE)}, Black pieces: {b.get_pieces_str(BLACK)}")
        except:
            print("Invalid move")
