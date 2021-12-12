import os

UP = 1
DOWN = -1
LEFT = -1
RIGHT = 1

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

def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

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
        self.__type = PAWN
        self.__has_moved = False

    def __str__(self):
        return PAWN

    def get_type(self):
        return self.__type

    def available_moves(self, board):

        moves = []

        next_row = self.row + (-1 if self.colour == BLACK else 1)

        if next_row in range(8):

            # Moving pawn forward if nothing in front of it
            if board.get_piece(next_row, self.col) is None:
                moves.append((next_row, self.col))
            
            # Moving pawn 2 places forward if nothing in front of it and has not yet moved
            if board.get_piece(next_row + (-1 if self.colour == BLACK else 1), self.col) is None and not self.__has_moved:
                moves.append((next_row + (-1 if self.colour == BLACK else 1), self.col))
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
        self.__type = KNIGHT

    def __str__(self):
        return KNIGHT

    def get_type(self):
        return self.__type

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
        self.__type = BISHOP

    def __str__(self):
        return BISHOP
    
    def get_type(self):
        return self.__type
    
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

class Rook(Piece):
    def __init__(self, row, col, colour):
        Piece.__init__(self, row, col, colour)
        self.__type = ROOK

    def __str__(self):
        return ROOK
    
    def get_type(self):
        return self.__type
    
    def available_moves(self, board):
        moves = []

        row = self.row
        col = self.col
        
        def rook_move_checker(bishop, board, start_row, start_col, row_iter, col_iter):
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
        
        moves += rook_move_checker(self, board, row, col, UP, 0)
        moves += rook_move_checker(self, board, row, col, DOWN, 0)
        moves += rook_move_checker(self, board, row, col, 0, LEFT)
        moves += rook_move_checker(self, board, row, col, 0, RIGHT)
    
        return moves

class Queen(Piece):
    def __init__(self, row, col, colour):
        Piece.__init__(self, row, col, colour)
        self.__type = QUEEN

    def __str__(self):
        return QUEEN
    
    def get_type(self):
        return self.__type
    
    def available_moves(self, board):
        moves = []

        row = self.row
        col = self.col
        
        def queen_move_checker(bishop, board, start_row, start_col, row_iter, col_iter):
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
        
        moves += queen_move_checker(self, board, row, col, UP, RIGHT)
        moves += queen_move_checker(self, board, row, col, UP, 0)
        moves += queen_move_checker(self, board, row, col, UP, LEFT)
        moves += queen_move_checker(self, board, row, col, DOWN, RIGHT)
        moves += queen_move_checker(self, board, row, col, DOWN, 0)
        moves += queen_move_checker(self, board, row, col, DOWN, LEFT)
        moves += queen_move_checker(self, board, row, col, 0, LEFT)
        moves += queen_move_checker(self, board, row, col, 0, RIGHT)
    
        return moves

class King(Piece):
    def __init__(self, row, col, colour):
        Piece.__init__(self, row, col, colour)
        self.__type = KING

    def __str__(self):
        return KING

    def get_type(self):
        return self.__type
    
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

        # Rooks
        self.grid[0][0] = Rook(0, 0, WHITE)
        self.grid[0][7] = Rook(0, 7, WHITE)
        self.grid[7][0] = Rook(7, 0, BLACK)
        self.grid[7][7] = Rook(7, 7, BLACK)

        # Queens
        self.grid[0][3] = Queen(0, 3, WHITE)
        self.grid[7][3] = Queen(7, 3, BLACK)

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

        self.turn = 0
        self.check  = {
            WHITE: False,
            BLACK: False
        }
        self.winner = None

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
        if not all([_ in range(8) for _ in [curr_row, curr_col, new_row, new_col]]):
            raise ValueError("Coordinates not between 0 and 7")
        
        piece = self.grid[curr_row][curr_col]
        player = WHITE if self.turn % 2 == 0 else BLACK
        
        if piece.get_colour() != player:
            raise ValueError("Cannot move an opponents piece")

        if (new_row, new_col) not in piece.available_moves(self):
            raise ValueError("Move not valid")
        
        target_piece = self.grid[new_row][new_col]
        if target_piece is not None:
            if target_piece.get_colour() == BLACK:
                self.black_pieces.remove(target_piece)
            else:
                self.white_pieces.remove(target_piece)
        

        
        
        # If you are in check your next move has to take you out of check
        # If you are in check mate, you lose

        temp_new = self.grid[new_row][new_col]

        piece.set_pos(new_row, new_col)
        self.grid[curr_row][curr_col] = None
        self.grid[new_row][new_col] = piece



        # Check

        player_in_check_last_round = self.check[player]
        player_in_check_this_round = self.white_king.is_in_check(self)

        # If you started the turn already in check, then you have to take youself out of check
        if player_in_check_last_round and player_in_check_this_round:
            self.grid[curr_row][curr_col] = piece
            self.grid[new_row][new_col] = temp_new
            piece.set_pos(curr_row, curr_col)
            raise ValueError("Player must take themself out of check")
        
        # Cannot do a move that results in yourself being put in check
        if player_in_check_this_round:
            self.grid[curr_row][curr_col] = piece
            self.grid[new_row][new_col] = temp_new
            piece.set_pos(curr_row, curr_col)
            raise ValueError("Player cannot put themselves in check")
        

        self.check[WHITE] = player_in_check_this_round
        self.check[BLACK] = self.black_king.is_in_check(self)

        # Checking if either player is in checkmate
        if self.check[WHITE] and len(self.white_king.available_moves()) == 0:
            self.winner = BLACK
        if self.check[BLACK] and len(self.black_king.available_moves()) == 0:
            self.winner = WHITE

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

        try:
            input1 = input(f"Player {b.whose_turn()} - Enter current row/col: ").split()
            curr_row, curr_col = int(input1[0]), int(input1[1])
            input2 = input(f"{b.piece_at_pos(curr_row, curr_col)} - Move to row/col: ").split()
            new_row, new_col = int(input2[0]), int(input2[1])
            try:
                b.move_piece(curr_row, curr_col, new_row, new_col)
            except ValueError:
                print("Invalid move")
        except (ValueError, IndexError):
            print("Please enter 2 numbers for row/col coordinates")
    
    print(f"Congrats {b.winner}, you win!!!")