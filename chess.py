# Hello World

UP = 1
DOWN = -1
LEFT = -1
RIGHT = 1

BLACK = "Black"
WHITE = "White"

PAWN = "P"
KNIGHT = "k"
BISHOP = "B"
KING = "K"

VALUES = {
    PAWN: 1,
    KNIGHT: 3,
    BISHOP: 3,
    KING: 1000
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
        self.has_moved = False

    def __str__(self):
        return PAWN

    def get_type(self):
        return self.type

    def available_moves(self, board):

        moves = []

        next_row = self.row + (-1 if self.colour == BLACK else 1)

        if next_row in range(8):

            # Moving pawn forward if nothing in front of it
            if board.get_piece(next_row, self.col) is None:
                moves.append((next_row, self.col))
            
            # Moving pawn 2 places forward if nothing in front of it and has not yet moved
            if board.get_piece(next_row + 1, self.col) is None and not self.has_moved:
                moves.append((next_row + 1, self.col))
                self.has_moved = True

            # Moving pawn diagonally forward left if there is an enemy piece there
            if (self.col - 1 in range(8) and board.get_piece(next_row, self.col - 1) is not None
                    and board.get_piece(next_row, self.col - 1).get_colour() != self.colour):
                moves.append((next_row, self.col - 1))

            # Moving pawn diagonally forward right if there is an enemy piece there
            if (self.col + 1 in range(8) and board.get_piece(next_row, self.col + 1) is not None
                    and board.get_piece(next_row, self.col + 1).get_colour() != self.colour):
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

    def available_moves(self, board):
        moves = []

        row = self.row
        col = self.col
        KNIGHT_MOVES = [(row + 1, col + 2), (row + 1, col - 2), (row + 2, col + 1),
                        (row + 2, col - 1), (row - 1, col + 2), (row - 1, col - 2),
                        (row - 2, col + 1), (row - 2, col - 1)]

        for trial_row, trial_col in KNIGHT_MOVES:
            if trial_row in range(8) and trial_col in range(8):
                piece = board.get_piece(trial_row, trial_col)

                if piece is None or piece.colour != self.colour:
                    moves.append((trial_row, trial_col))

        return moves

class Bishop(Piece):
    def __init__(self, row, col, colour):
        Piece.__init__(self, row, col, colour)
        self.type = BISHOP

    def __str__(self):
        return BISHOP
    
    def get_type(self):
        return self.type
    
    def available_moves(self, board):
        moves = []

        row = self.row
        col = self.col
        
        def bishop_move_checker(bishop, board, start_row, start_col, row_iter, col_iter):
            moves = []
            
            row = start_row + row_iter
            col = start_col + col_iter
            while row in range(8) and col in range(8):
                target_piece = board.get_piece(row, col)

                if target_piece is None:
                    moves.append((row, col))
                else:
                    if target_piece.get_colour() != bishop.colour:
                        moves.append((row, col))
                    break

                row += row_iter
                col += col_iter
            return moves
        
        moves += bishop_move_checker(self, board, row, col, UP, RIGHT)
        moves += bishop_move_checker(self, board, row, col, UP, LEFT)
        moves += bishop_move_checker(self, board, row, col, DOWN, RIGHT)
        moves += bishop_move_checker(self, board, row, col, DOWN, LEFT)
    
        return moves

class King(Piece):
    def __init__(self, row, col, colour):
        Piece.__init__(self, row, col, colour)
        self.type = KING

    def __str__(self):
        return KING

    def get_type(self):
        return self.type
    
    def available_moves(self, board):
        moves = []
        
        opposing_pieces = board.get_pieces(BLACK) if self.colour == WHITE else board.get_pieces(WHITE)
        
        # Removing King from list of opposing pieces (King is first piece in list)
        opposing_pieces = opposing_pieces[1:]
        opposing_moves = []
        for piece in opposing_pieces:
            opposing_moves += piece.available_moves(board)
        
        for row in [self.row - 1, self.row, self.row + 1]:
            for col in [self.col - 1, self.col, self.col + 1]:
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
        self.grid[1] = [Pawn(1, x, WHITE) for x in range(8)]
        self.grid[6] = [Pawn(6, x, BLACK) for x in range(8)]

        # Knights
        self.grid[0][1] = Knight(0, 1, WHITE)
        self.grid[0][6] = Knight(0, 6, WHITE)
        self.grid[7][1] = Knight(7, 1, BLACK)
        self.grid[7][6] = Knight(7, 6, BLACK)

        # Bishops
        self.grid[0][2] = Bishop(0, 2, WHITE)
        self.grid[0][5] = Bishop(0, 5, WHITE)
        self.grid[7][2] = Bishop(7, 2, BLACK)
        self.grid[7][5] = Bishop(7, 5, BLACK)

        # Kings
        self.white_king = King(0, 4, WHITE)
        self.grid[0][4] = self.white_king
        self.black_king = King(7, 4, BLACK)
        self.grid[7][4] = self.black_king

        self.white_pieces = []
        for row in self.grid[0:2]:
            for piece in row:
                if piece is not None:
                    self.white_pieces.append(piece)
        self.white_pieces.sort(key= lambda piece: VALUES[piece.get_type()], reverse= True)

        self.black_pieces = []
        for row in self.grid[6:8]:
            for piece in row:
                if piece is not None:
                    self.black_pieces.append(piece)
        self.black_pieces.sort(key= lambda piece: VALUES[piece.get_type()], reverse= True)

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

        if (new_row, new_col) not in piece.available_moves(self):
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
    
    def get_piece(self, row, col):
        return self.grid[row][col]


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
            print(f"Check: White - {b.white_king.is_in_check(b)}, Black - {b.black_king.is_in_check(b)}")
        except:
            print("Invalid move")
