import os
import copy

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

VALUES = {PAWN: 1, KNIGHT: 3, BISHOP: 3, ROOK: 5, QUEEN: 9, KING: 1000}

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


def difference_in_pos(pos1, pos2):
    return (pos1[ROW] - pos2[ROW], pos1[COL] - pos2[COL])


def get_direction_vector(pos1, pos2):
    row_vector = pos2[ROW] - pos1[ROW]
    col_vector = pos2[COL] - pos1[COL]

    if row_vector == col_vector == 0:
        return (0, 0)

    return (int(row_vector / max(abs(row_vector), abs(col_vector))),
            int(col_vector / max(abs(row_vector), abs(col_vector))))


def same_sign(a, b):
    return (a < 0 and b < 0) or (a >= 0 and b >= 0)


def get_direction_vector_float(pos1, pos2):
    row_vector = pos2[ROW] - pos1[ROW]
    col_vector = pos2[COL] - pos1[COL]

    if row_vector == col_vector == 0:
        return (0, 0)

    return (row_vector / max(abs(row_vector), abs(col_vector)),
            col_vector / max(abs(row_vector), abs(col_vector)))


# Checks if pos3 is on line between pos1 and pos2
def in_line(pos1, pos2, pos3):
    if ((pos1[ROW] <= pos3[ROW] <= pos2[ROW] or pos2[ROW] <= pos3[ROW] <= pos1[ROW])
            and (pos1[COL] <= pos3[COL] <= pos2[COL] or pos2[COL] <= pos3[COL] <= pos1[COL])):
        direction_pos1_pos2 = difference_in_pos(pos1, pos2)
        direction_pos1_pos3 = difference_in_pos(pos1, pos3)

        # E.g pos1 = (5, 5), pos2 = (8, 8), pos3 = (7, 7)

        # In horizontal/vertical line
        if direction_pos1_pos3[ROW] == direction_pos1_pos2[ROW] == 0 or direction_pos1_pos3[
                COL] == direction_pos1_pos2[COL] == 0:
            return True

        # In diagonal line
        if direction_pos1_pos3[ROW] == direction_pos1_pos3[COL] and direction_pos1_pos2[
                ROW] == direction_pos1_pos2[COL]:
            return True

    return False


def list_intersection(l1, l2):
    temp = set(l2)
    return [value for value in l1 if value in temp]


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

    def protecting_king(self, board):
        # Checks if piece is currently protecting King from being in check by a Queen, Rook or Bishop

        # Checks Horizontal, Vertical, Diagonal to see if your teams King is in sight
        found_row_iter = found_col_iter = None
        for col_iter, row_iter in VERTICALS + HORIZONTALS + DIAGONALS:
            row = self.pos[ROW] + row_iter
            col = self.pos[COL] + col_iter
            while in_bounds((row, col)):
                target_piece = board.get_piece(row, col)
                if target_piece is not None:
                    if target_piece == board.king[self.get_colour()]:
                        found_col_iter = -1 * col_iter
                        found_row_iter = -1 * row_iter
                    break
                row += row_iter
                col += col_iter

            if found_row_iter is not None:
                break

        # If King not in sight, cannot be protecting King
        if found_row_iter is None:
            return (None, None)

        # If King is in line of sight, checks if there is a Bishop, Rook or Queen in opposite direction
        row = self.pos[ROW] + found_row_iter
        col = self.pos[COL] + found_col_iter
        opponent = WHITE if self.get_colour() == BLACK else BLACK
        direction = (found_col_iter, found_row_iter)
        while in_bounds((row, col)):
            target_piece = board.get_piece(row, col)
            if target_piece is not None:
                if target_piece.get_colour() == opponent and (
                    (target_piece.get_type() in [BISHOP, QUEEN] and direction in DIAGONALS) or
                    (target_piece.get_type() in [ROOK, QUEEN]
                     and direction in HORIZONTALS + VERTICALS)):
                    return (row, col)
                break
            row += found_row_iter
            col += found_col_iter

        # If in line of sight of King but not protecting from anything
        return (None, None)

    def filter_moves_to_protect_king(self, moves, board):
        # In case that is protecting King, filters out moves that would leave King exposed
        movement_vector = get_direction_vector(board.king[self.get_colour()].get_pos(),
                                               self.get_pos())
        negative_movement_vector = (-1 * movement_vector[ROW], -1 * movement_vector[COL])
        positions_in_line_with_king = self.moves_in_line(
            board, [movement_vector, negative_movement_vector])
        return list_intersection(moves, positions_in_line_with_king)


# TODO: Fix issue with double check, where moving one of your pieces may lead to discovered check in which another one of your piece causes check
# Fix: use similar code to protecting King, in which we have to see if one of your pieces is protecting opposing King from another one of your pieces

# Is assuming piece isn't a king because otherwise would be an unneccesary filter as Kings already move to get themselves out of check

    def filter_moves_to_stop_check(self, moves, board):
        filtered_moves = []

        # In double check, pieces can't stop chess by capturing or blocking, has to be from movement from King
        if len(board.check[self.get_colour()]['pieces_causing_check']) > 1:
            return []

        opposing_piece = board.check[self.get_colour()]['pieces_causing_check'][0]
        for move in moves:
            # Capture piece that is causing check
            if move == opposing_piece.get_pos():
                filtered_moves.append(move)
            # Block piece, note cannot block a check caused by a Knight
            elif opposing_piece.get_type() != KNIGHT:
                if in_line(opposing_piece.get_pos(), board.king[self.get_colour()].get_pos(),
                           move):
                    filtered_moves.append(move)

        return filtered_moves


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

        # In case that is protecting King, filters out moves that would leave King exposed
        protecting_king_from_piece = self.protecting_king(board)
        if protecting_king_from_piece is not (None, None):
            moves = self.filter_moves_to_protect_king(moves, board)

        # In the case that is in check, any move has to be one that takes out of check
        if board.check[self.get_colour()]['in_check']:
            moves = self.filter_moves_to_stop_check(moves, board)

        return moves


class Knight(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, KNIGHT, colour)

    def available_moves(self, board):
        moves = []

        if self.protecting_king(board) is not (None, None):
            return []

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

        # In the case that is in check, any move has to be one that takes out of check
        if board.check[self.get_colour()]['in_check']:
            moves = self.filter_moves_to_stop_check(moves, board)

        return moves


class Bishop(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, BISHOP, colour)

    def available_moves(self, board):
        moves = self.moves_in_line(board, DIAGONALS)

        # In case that is protecting King, filters out moves that would leave King exposed
        protecting_king_from_piece = self.protecting_king(board)
        if protecting_king_from_piece is not (None, None):
            moves = self.filter_moves_to_protect_king(moves, board)

        # In the case that is in check, any move has to be one that takes out of check
        if board.check[self.get_colour()]['in_check']:
            moves = self.filter_moves_to_stop_check(moves, board)

        return moves


class Rook(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, ROOK, colour)

    def available_moves(self, board):
        moves = self.moves_in_line(board, HORIZONTALS + VERTICALS)

        # In case that is protecting King, filters out moves that would leave King exposed
        protecting_king_from_piece = self.protecting_king(board)
        if protecting_king_from_piece is not (None, None):
            moves = self.filter_moves_to_protect_king(moves, board)

        # In the case that is in check, any move has to be one that takes out of check
        if board.check[self.get_colour()]['in_check']:
            moves = self.filter_moves_to_stop_check(moves, board)

        return moves


class Queen(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, QUEEN, colour)

    def available_moves(self, board):
        moves = self.moves_in_line(board, HORIZONTALS + VERTICALS + DIAGONALS)

        # In case that is protecting King, filters out moves that would leave King exposed
        protecting_king_from_piece = self.protecting_king(board)
        if protecting_king_from_piece is not (None, None):
            moves = self.filter_moves_to_protect_king(moves, board)

        # In the case that is in check, any move has to be one that takes out of check
        if board.check[self.get_colour()]['in_check']:
            moves = self.filter_moves_to_stop_check(moves, board)

        return moves


class King(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, KING, colour)

    def available_moves(self, board):
        moves = []

        opposing_pieces = board.get_pieces(BLACK) if self.colour == WHITE else board.get_pieces(
            WHITE)

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
                    if (piece is None or
                            piece.get_colour() != self.colour) and (row, col) not in opposing_moves:
                        moves.append((row, col))

        # TODO Add castling feature

        return moves

    def is_in_check(self, board):
        opposing_pieces = board.get_pieces(BLACK) if self.colour == WHITE else board.get_pieces(
            WHITE)

        # Removing King from list of opposing pieces (King is first piece in list)
        opposing_pieces = opposing_pieces[1:]
        opposing_moves = []
        for piece in opposing_pieces:
            opposing_moves += piece.available_moves(board)

        return self.curr_pos() in opposing_moves


class Board:
    def __init__(self):

        # Create 8 x 8 Grid
        self.grid = [[None for x in range(8)] for y in range(8)]

        # Pawns
        self.grid[1] = [Pawn((1, x), WHITE) for x in range(8)]
        self.grid[6] = [Pawn((6, x), BLACK) for x in range(8)]

        # Remaining Pieces
        pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        self.grid[0] = [piece((0, index), WHITE) for index, piece in enumerate(pieces)]
        self.grid[7] = [piece((7, index), BLACK) for index, piece in enumerate(pieces)]

        self.king = {WHITE: self.grid[0][4], BLACK: self.grid[7][4]}

        self.pieces = {WHITE: [], BLACK: []}
        for row in self.grid[0:2]:
            for piece in row:
                self.pieces[WHITE].append(piece)
        self.pieces[WHITE].sort(key=lambda piece: VALUES[piece.get_type()], reverse=True)

        for row in self.grid[6:8]:
            for piece in row:
                self.pieces[BLACK].append(piece)
        self.pieces[BLACK].sort(key=lambda piece: VALUES[piece.get_type()], reverse=True)

        self.turn = 0
        self.check = {
            WHITE: {
                'in_check': False,
                'pieces_causing_check': []
            },
            BLACK: {
                'in_check': False,
                'pieces_causing_check': []
            }
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
        return self.pieces[colour]

    def get_pieces_str(self, colour):
        pieces = self.pieces[colour]
        return [f"{piece.get_type()} {piece.get_pos()}" for piece in pieces]

    def move_piece(self, curr_row, curr_col, new_row, new_col):
        if not (in_bounds((curr_row, curr_col)) and in_bounds((new_row, new_col))):
            raise ValueError("Coordinates not between 0 and 7")

        piece = self.grid[curr_row][curr_col]

        if piece is None:
            raise ValueError("No piece selected")

        player = self.whose_turn()
        opponent = BLACK if player == WHITE else WHITE

        if piece.get_colour() != player:
            raise ValueError("Cannot move an opponents piece")

        if (new_row, new_col) not in piece.available_moves(self):
            raise ValueError("Move not valid")

        target_piece = self.grid[new_row][new_col]

        if target_piece is not None and target_piece.get_colour() == player:
            raise ValueError("Cannot capture your own piece")

        temp_grid = copy.deepcopy(self.grid)

        # Capture opposing target_piece
        if target_piece is not None:
            self.pieces[opponent].remove(target_piece)
            if target_piece in self.check[player]['pieces_causing_check']:
                self.check[player]['pieces_causing_check'.remove(target_piece)]
                self.check[player]['in_check'] = len(self.check[player]['pieces_causing_check']) > 1

        # You cannot make a move that places yourself in check
        # # If you are in check your next move has to take you out of check
        # # If you are in check mate, you lose

        piece.set_pos((new_row, new_col))
        self.grid[curr_row][curr_col] = None
        self.grid[new_row][new_col] = piece

        # Place Oppossing King in Check
        new_available_moves = piece.available_moves(self)
        if piece.get_colour() == WHITE and self.king[BLACK].get_pos() in new_available_moves:
            self.check[BLACK]['in_check'] = True
            self.check[BLACK]['pieces_causing_check'].append(piece)
        elif piece.get_colour() == BLACK and self.king[WHITE].get_pos() in new_available_moves:
            self.check[WHITE]['in_check'] = True
            self.check[WHITE]['pieces_causing_check'].append(piece)

        # player_in_check_last_round = self.check[player]
        # player_in_check_this_round = self.king[WHITE].is_in_check(self)

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

    def is_in_check(self, colour):
        return self.check[colour]['in_check']


if __name__ == '__main__':
    b = Board()

    while b.winner is None:
        #clear_console()
        print("==========")
        print(b)
        print(f"White - {b.get_pieces_str(WHITE)}, Black - {b.get_pieces_str(BLACK)}")
        print(f"Check: White - {b.is_in_check(WHITE)}, Black - {b.is_in_check(BLACK)}")

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