# Contains game logic for chess

UP = -1
DOWN = 1
LEFT = -1
RIGHT = 1

ROW = 0
COL = 1

BOARD_SIZE = 8

BLACK = "Black"
WHITE = "White"
STALEMATE = "Stalemate"

PAWN = "P"
KNIGHT = "N"
BISHOP = "B"
ROOK = "R"
QUEEN = "Q"
KING = "K"

VALUES = {PAWN: 1, KNIGHT: 3, BISHOP: 3, ROOK: 5, QUEEN: 9, KING: 1000}

HORIZONTALS = [(0, LEFT), (0, RIGHT)]
VERTICALS = [(UP, 0), (DOWN, 0)]
DIAGONALS = [(UP, LEFT), (UP, RIGHT), (DOWN, LEFT), (DOWN, RIGHT)]
ALL_DIRECTIONS = HORIZONTALS + VERTICALS + DIAGONALS


def cache_moves(method):
    """
    Decorator to handle caching of available moves. When self.available_moves is called by a piece,
    decorator checks if has already calculated available moves for this turn. If it has, returns 
    stored values, else calculates and stores new values.
    """
    def wrapper(self, board, *args, **kwargs):
        has_modifiers = len(kwargs) > 0
        if self.available_moves_cache['turn'] == board.turn and not has_modifiers:
            return self.available_moves_cache['moves']
        else:
            moves = method(self, board, *args, **kwargs)
            if not has_modifiers:
                self.available_moves_cache['turn'] = board.turn
                self.available_moves_cache['moves'] = moves
            return moves

    return wrapper


def in_bounds(pos):
    """
    Checks if position given by (row, col) is within bounds of array of size GRID_SIZE x GRID_SIZE.

    Args:
        pos (Tuple): position in array (row, col).

    Returns:
        bool: returns True/False whether pos is in bounds.
    """
    return pos[ROW] in range(BOARD_SIZE) and pos[COL] in range(BOARD_SIZE)


def difference_in_pos(pos1, pos2):
    """
    Performs pos1 - pos2 pointwise, i.e (pos1[0] - pos2[0], pos1[1] - pos2[1]).

    Args:
        pos1 (Tuple): position in array (row, col).
        pos2 (Tuple): position in array (row, col).

    Returns:
        Tuple: returns (pos1[ROW] - pos2[ROW], pos1[COL] - pos2[COL]).
    """
    return (pos1[ROW] - pos2[ROW], pos1[COL] - pos2[COL])


def get_direction_vector(pos1, pos2):
    """
    Finds the direction of the line going from pos1 to pos2, e.g (UP, RIGHT) to indicate pos2 is
    diagonally above and to the right of pos1. If pos1 and pos2 are not on a vertical/horizontal/
    diagonal line, returns (None, None).

    Args:
        pos1 (Tuple): position in array (row, col).
        pos2 (Tuple): position in array (row, col).

    Returns:
        Tuple: Returns Tuple of form (UP/DOWN/0, LEFT/RIGHT/0) if pos1 and pos2 are on a vertical/
                horizontal/diagonal line, otherwise returns (None, None).
    """
    direction = difference_in_pos(pos2, pos1)
    increment = (None, None)

    # Line from pos1 to pos2 is a diagonal line \
    if direction[ROW] == direction[COL] != 0:
        increment = (UP, LEFT) if direction[ROW] < 0 else (DOWN, RIGHT)

    # Line from pos1 to pos2 is a diagonal line /
    if direction[ROW] == -1 * direction[COL] != 0:
        increment = (UP, RIGHT) if direction[ROW] < 0 else (DOWN, LEFT)

    # Line from pos1 to pos2 is a horizontal line
    if direction[ROW] == 0 and direction[COL] != 0:
        increment = (0, LEFT) if direction[COL] < 0 else (0, RIGHT)

    # Line from pos1 to pos2 is a vertical line
    if direction[ROW] != 0 and direction[COL] == 0:
        increment = (UP, 0) if direction[ROW] < 0 else (DOWN, 0)

    return increment


def in_line(pos1, pos2, pos3):
    """
    Determines if pos3 is a point along a vertical/horizontal/diagonal line between pos1 and pos2. 
    Note, does not check if there is anything else in between pos1 and pos2, only that pos3 is
    inbetween. 

    Args:
        pos1 (Tuple): position in array (row, col).
        pos2 (Tuple): position in array (row, col).
        pos3 (Tuple): position in array (row, col).

    Returns:
        Bool: True/False of whether pos3 is between pos1 and pos2.
    """
    if ((pos1[ROW] <= pos3[ROW] <= pos2[ROW] or pos2[ROW] <= pos3[ROW] <= pos1[ROW])
            and (pos1[COL] <= pos3[COL] <= pos2[COL] or pos2[COL] <= pos3[COL] <= pos1[COL])):
        direction_pos1_pos2 = difference_in_pos(pos1, pos2)
        direction_pos1_pos3 = difference_in_pos(pos1, pos3)

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
    """
    Returns a list containing the intersection of 2 lists l1 and l2, i.e list with all items that
    are in both lists. Order of l1 is retained in returned list. 

    Args:
        l1 (List): Arbitrary list.
        l2 (List): Arbitrary list.

    Returns:
        List: List containing intersection of l1 and l2.
    """
    temp = set(l2)
    return [value for value in l1 if value in temp]


def in_sight(board, start_pos, direction):
    """
    Finds the first Piece on the board that is found by following a direction from a starting point
    in grid. If no Piece is found, returns None. 


    Args:
        board (Board): Instance of Board class that contains all information of current state of game
        start_pos (Tuple): Starting position in grid.
        direction (Tuple): Tuple containing of form (row_iter, col_iter), which is the direction that
                            should be followed from starting position.

    Returns:
        Piece: Returns the first Piece that is found by following direction from starting position
                or None if there is no Piece found. 
    """
    row_iter = direction[ROW]
    col_iter = direction[COL]
    row = start_pos[ROW] + row_iter
    col = start_pos[COL] + col_iter

    piece = None
    while in_bounds((row, col)) and piece is None:
        piece = board.get_piece(row, col)
        row += row_iter
        col += col_iter

    return piece


class Piece:
    def __init__(self, pos, type, colour):
        self.pos = pos
        self.type = type
        self.colour = colour
        self.available_moves_cache = {'turn': -1, 'moves': []}

    def __str__(self):
        return self.type

    def set_pos(self, pos):
        """
        Set position of Piece.

        Args:
            pos (Tuple): Position of Piece in grid (row, col).

        Raises:
            ValueError: position is not within bounds of grid, (row, col) must be between 0 and 8.
        """
        if not in_bounds(pos):
            raise ValueError("Row/Col must be between 0 and 8")
        self.pos = pos

    def get_pos(self):
        """
        Gets the current position of Piece in grid.

        Returns:
            Tuple: Position (row, col) in grid.
        """
        return self.pos

    def get_colour(self):
        """
        Gets the colour of piece.

        Returns:
            string literal: Returns BLACK or WHITE.
        """
        return self.colour

    def get_type(self):
        """
        Gets the the type of piece.
        
        Returns:
            string literal: Returns PAWN/KNIGHT/BISHOP/ROOK/QUEEN/KING.
        """
        return self.type

    def moves_in_line(self, board, increments, include_protections=False, ignore_king_block=False):
        """
        Checks for possible unobstructed movement along a line dictated by a piece's initial 
        position (self.pos) and a list of possible increments. e.g increment (UP, RIGHT) would 
        check for possible movement along diagonal upward and right line from the piece's starting
        position. Records all moves along a line until it either reaches the edge of the game grid,
        or encounters another piece. By default, only records the position of a piece if it is the 
        opponents piece. Setting include_protections = True overrides this behaviour and also 
        records positions of friendly pieces. Returns the list of all possible moves on all such 
        lines. 

        Args:
            board (Board): Instance of Board class that contains all information about the 
                            current state of game.
            increments (List): List containing tuples of form (row_iter, col_iter), which represent 
                                the possible incremements that can be applied to starting position.
            include_protections (bool, optional): Determines whether to include the positions 
                                                    of pieces that this piece is protecting, i.e 
                                                    positions that are reachable if allied piece was
                                                    not there, defaults to False.

        Returns:
            List: Returns list of tuples contianing positions (row, col) of all possible moves along
                    lines. 
        """
        moves = []
        opponent = WHITE if self.colour == BLACK else BLACK
        for row_iter, col_iter in increments:
            row = self.pos[ROW] + row_iter
            col = self.pos[COL] + col_iter
            while in_bounds((row, col)):
                target_piece = board.get_piece(row, col)
                if target_piece is None:
                    moves.append((row, col))
                else:
                    if target_piece.get_colour() != self.colour or include_protections:
                        moves.append((row, col))
                    if not (target_piece == board.king[opponent] and ignore_king_block):
                        break
                row += row_iter
                col += col_iter

        return moves

    def protecting_king(self, board):
        """
        Checks if Piece is protecting King from being in check due to an enemy's Queen/Rook/Bishop. 
        Determines if your team's King is within line of sight (i.e unobstructed along a
        vertical, horizontal, diagonal line in grid), and if so checks if this piece is standing
        between King and an opponents piece who could place King in check along this line.

        Args:
            board (Board): Instance of Board class that contains all information about the 
                            current state of game.

        Returns:
            Tuple: Returns the position of the opponent's piece that this piece is protecting the
                    King from, defaults to (None, None) if there is no such piece. 
        """

        # Checks Horizontal, Vertical, Diagonal to see if your teams King is in sight
        found_row_iter = found_col_iter = None
        for row_iter, col_iter in VERTICALS + HORIZONTALS + DIAGONALS:
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

    def discovered_check(self, move, board):
        """
        Determines moving piece to position dictated by move will result in a discovered check. If 
        no discovered check results, returns None. Otherwise, returns the piece that causes the
        discovered check. 

        Args:
            move (Tuple): Position (row, col) that piece can move to. 
            board (Board): Instance of Board class that contains all information about the 
                            current state of game.

        Returns:
            Piece: Returns the piece that causes discovered check, if no such piece exists returns 
                    None.
        """

        opponent = BLACK if self.get_colour() == WHITE else WHITE
        enemy_king = board.king[opponent]

        # If move just results in piece staying in line with King, then cannot result in discovered check
        if in_line(enemy_king.get_pos(), self.get_pos(), move) or in_line(
                enemy_king.get_pos(), move, self.get_pos()):
            return None

        increment = get_direction_vector(enemy_king.get_pos(), self.get_pos())
        if increment == (None, None):
            return None

        # Checks if enemy king is in sight of piece (i.e, not just in line with King)
        if in_sight(board, self.get_pos(),
                    (-1 * increment[ROW], -1 * increment[COL])) != enemy_king:
            return None

        # Checks if you have a Rook, Bishp, Queen, in sight of this piece
        piece = in_sight(board, self.get_pos(), increment)
        if piece is not None:
            if piece.get_colour() == self.get_colour():
                if increment in HORIZONTALS + VERTICALS and piece.get_type() in [ROOK, QUEEN]:
                    return piece
                if increment in DIAGONALS and piece.get_type() in [BISHOP, QUEEN]:
                    return piece

        return None

    def filter_moves_to_protect_king(self, moves, board):
        """
        Given a set of possible moves, filter out moves that would leave your King exposed in the 
        case that piece is protecting King.

        Args:
            moves (List): List of possible positions (row, col) that Piece can move to.
            board (Board): Instance of Board class that contains all information about the 
                            current state of game.

        Returns:
            List: List of moves with filter applied.
        """
        # In case that is protecting King, filters out moves that would leave King exposed
        movement_vector = get_direction_vector(board.king[self.get_colour()].get_pos(),
                                               self.get_pos())
        negative_movement_vector = (-1 * movement_vector[ROW], -1 * movement_vector[COL])
        positions_in_line_with_king = self.moves_in_line(
            board, [movement_vector, negative_movement_vector])
        return list_intersection(moves, positions_in_line_with_king)

    def filter_moves_to_stop_check(self, moves, board):
        """
        Given a set of moves, filters out moves that don't stop check in case that King is in check.

        Args:
            moves (List): List of possible positions (row, col) that Piece can move to.
            board (Board): Instance of Board class that contains all information about the 
                            current state of game.

        Returns:
            List: List of moves with filter applied.
        """
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
                if in_line(opposing_piece.get_pos(), board.king[self.get_colour()].get_pos(), move):
                    filtered_moves.append(move)
        return filtered_moves


class Pawn(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, PAWN, colour)
        self.__direction = DOWN if colour == WHITE else UP
        self.__has_moved = False
    
    def set_has_moved(self):
        """
        Records that Pawn has moved
        """
        self.__has_moved = True

    @cache_moves
    def available_moves(self, board):
        """
        Finds all available moves of a Pawn Piece given current state of the board.

        Args:
            board (Board): Instance of Board class that contains all information about the 
                            current state of game.

        Returns:
            List: Returns list of possible moves.
        """
        moves = []
        next_row = self.pos[ROW] + self.__direction
        col = self.pos[COL]
        if next_row in range(8):

            # Moving pawn forward if nothing in front of it
            if board.get_piece(next_row, col) is None:
                moves.append((next_row, col))

            # Moving pawn 2 places forward if nothing in front of it and has not yet moved
            if board.get_piece(next_row, col) is None and board.get_piece(next_row + self.__direction, col) is None and not self.__has_moved:
                moves.append((next_row + self.__direction, col))

            # Moving pawn diagonally forward left if there is an enemy piece there
            if ((col + LEFT in range(8) and board.get_piece(next_row, col - 1) is not None
                    and board.get_piece(next_row, col - 1).get_colour() != self.colour)):
                moves.append((next_row, col - 1))

            # Moving pawn diagonally forward right if there is an enemy piece there
            if ((col + RIGHT in range(8) and board.get_piece(next_row, col + 1) is not None
                    and board.get_piece(next_row, col + 1).get_colour() != self.colour)):
                moves.append((next_row, col + 1))

        # In case that is protecting King, filters out moves that would leave King exposed
        protecting_king_from_piece = self.protecting_king(board)
        if protecting_king_from_piece != (None, None):
            moves = self.filter_moves_to_protect_king(moves, board)

        # In the case that is in check, any move has to be one that takes out of check
        if board.check[self.get_colour()]['in_check']:
            moves = self.filter_moves_to_stop_check(moves, board)

        return moves
    
    def attacking_moves(self, board):
        """
        Returns all possible moves that involve a Pawn capturing another piece

        Args:
            board (Board): Instance of Board class that contains all information about the 
                            current state of game.

        Returns:
            List: Returns list of possible moves.
        """
        moves = []
        next_row = self.pos[ROW] + self.__direction
        col = self.pos[COL]

        if in_bounds((next_row, col + LEFT)):
            moves.append((next_row, col + LEFT))
        if in_bounds((next_row, col + RIGHT)):
            moves.append((next_row, col + RIGHT))
        
        return moves



class Knight(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, KNIGHT, colour)

    @cache_moves
    def available_moves(self, board, include_protections=False):
        """
        Finds all available moves of a Knight Piece given current state of the board.

        Args:
            board (Board): Instance of Board class that contains all information about the 
                            current state of game.
            include_protections (bool, optional): Determines whether to include the positions 
                                                    of pieces that this piece is protecting, i.e 
                                                    positions that are reachable if allied piece was
                                                    not there, defaults to False.

        Returns:
            List: Returns list of possible moves.
        """
        moves = []

        if self.protecting_king(board) != (None, None):
            return []

        row = self.pos[ROW]
        col = self.pos[COL]
        KNIGHT_MOVES = [(row + 1, col + 2), (row + 1, col - 2), (row + 2, col + 1),
                        (row + 2, col - 1), (row - 1, col + 2), (row - 1, col - 2),
                        (row - 2, col + 1), (row - 2, col - 1)]

        for trial_pos in KNIGHT_MOVES:
            if in_bounds(trial_pos):
                piece = board.get_piece(trial_pos[ROW], trial_pos[COL])

                if piece is None or piece.get_colour() != self.colour or include_protections:
                    moves.append(trial_pos)

        # In the case that is in check, any move has to be one that takes out of check
        if board.check[self.get_colour()]['in_check']:
            moves = self.filter_moves_to_stop_check(moves, board)

        return moves
    
    def attacking_moves(self, board):
        return self.available_moves(board, include_protections=True)


class Bishop(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, BISHOP, colour)

    @cache_moves
    def available_moves(self, board, include_protections=False, ignore_king_block=False):
        """
        Finds all available moves of a Bishop Piece given current state of the board.

        Args:
            board (Board): Instance of Board class that contains all information about the 
                            current state of game.
            include_protections (bool, optional): Determines whether to include the positions 
                                                    of pieces that this piece is protecting, i.e 
                                                    positions that are reachable if allied piece was
                                                    not there, defaults to False.

        Returns:
            List: Returns list of possible moves.
        """
        moves = self.moves_in_line(board, DIAGONALS, include_protections=include_protections, ignore_king_block=ignore_king_block)

        # In case that is protecting King, filters out moves that would leave King exposed
        protecting_king_from_piece = self.protecting_king(board)
        if protecting_king_from_piece != (None, None):
            moves = self.filter_moves_to_protect_king(moves, board)

        # In the case that is in check, any move has to be one that takes out of check
        if board.check[self.get_colour()]['in_check']:
            moves = self.filter_moves_to_stop_check(moves, board)

        return moves
    
    def attacking_moves(self, board):
        return self.moves_in_line(board, DIAGONALS, include_protections=True, ignore_king_block=True)


class Rook(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, ROOK, colour)

    @cache_moves
    def available_moves(self, board, include_protections=False, ignore_king_block=False):
        """
        Finds all available moves of a Rook Piece given current state of the board.

        Args:
            board (Board): Instance of Board class that contains all information about the 
                            current state of game.
            include_protections (bool, optional): Determines whether to include the positions 
                                                    of pieces that this piece is protecting, i.e 
                                                    positions that are reachable if allied piece was
                                                    not there, defaults to False.

        Returns:
            List: Returns list of possible moves.
        """
        moves = self.moves_in_line(board,
                                   HORIZONTALS + VERTICALS,
                                   include_protections=include_protections,
                                   ignore_king_block=ignore_king_block)

        # In case that is protecting King, filters out moves that would leave King exposed
        protecting_king_from_piece = self.protecting_king(board)
        if protecting_king_from_piece != (None, None):
            moves = self.filter_moves_to_protect_king(moves, board)

        # In the case that is in check, any move has to be one that takes out of check
        if board.check[self.get_colour()]['in_check']:
            moves = self.filter_moves_to_stop_check(moves, board)

        return moves

    def attacking_moves(self, board):
        return self.moves_in_line(board, HORIZONTALS + VERTICALS, include_protections=True, ignore_king_block=True)


class Queen(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, QUEEN, colour)

    @cache_moves
    def available_moves(self, board, include_protections=False, ignore_king_block=False):
        """
        Finds all available moves of a Queen Piece given current state of the board.

        Args:
            board (Board): Instance of Board class that contains all information about the 
                            current state of game.
            include_protections (bool, optional): Determines whether to include the positions 
                                                    of pieces that this piece is protecting, i.e 
                                                    positions that are reachable if allied piece was
                                                    not there, defaults to False.

        Returns:
            List: Returns list of possible moves.
        """
        moves = self.moves_in_line(board,
                                   HORIZONTALS + VERTICALS + DIAGONALS,
                                   include_protections=include_protections,
                                   ignore_king_block=ignore_king_block)

        # In case that is protecting King, filters out moves that would leave King exposed
        protecting_king_from_piece = self.protecting_king(board)
        if protecting_king_from_piece != (None, None):
            moves = self.filter_moves_to_protect_king(moves, board)

        # In the case that is in check, any move has to be one that takes out of check
        if board.check[self.get_colour()]['in_check']:
            moves = self.filter_moves_to_stop_check(moves, board)

        return moves

    def attacking_moves(self, board):
        return self.moves_in_line(board, ALL_DIRECTIONS, include_protections=True, ignore_king_block=True)


class King(Piece):
    def __init__(self, pos, colour):
        Piece.__init__(self, pos, KING, colour)

    @cache_moves
    def available_moves(self, board):
        """
        Finds all available moves of a King Piece given current state of the board.

        Args:
            board (Board): Instance of Board class that contains all information about the 
                            current state of game.
            include_protections (bool, optional): Determines whether to include the positions 
                                                    of pieces that this piece is protecting, i.e 
                                                    positions that are reachable if allied piece was
                                                    not there, defaults to False.

        Returns:
            List: Returns list of possible moves.
        """


        row = self.pos[ROW]
        col = self.pos[COL]
        opponent = BLACK if self.colour == WHITE else WHITE

        moves = [(row + row_iter, col + col_iter) for row_iter, col_iter in ALL_DIRECTIONS]
        
        # Filter out moves that are out of bounds
        moves = list(filter(lambda pos: in_bounds(pos), moves))
        
        # Filter out moves that attack your own pieces
        _ = lambda pos: board.get_piece(*pos) is None or board.get_piece(*pos).colour == opponent
        moves = list(filter(_, moves))

        # Removing King from list of opposing pieces (King is first piece in list)
        opposing_pieces = board.get_pieces(opponent)
        opposing_pieces = opposing_pieces[1:]

        for piece in opposing_pieces:
            if len(moves) == 0:
                return moves
            
            opposing_moves = piece.attacking_moves(board)
            moves = list(filter(lambda pos: pos not in opposing_moves, moves))

        return moves


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

        # Each player's King piece
        self.king = {WHITE: self.grid[0][4], BLACK: self.grid[7][4]}

        # List of Each player's pieces, sorted by value
        self.pieces = {WHITE: [], BLACK: []}
        for row in self.grid[0:2]:
            for piece in row:
                self.pieces[WHITE].append(piece)
        self.pieces[WHITE].sort(key=lambda piece: VALUES[piece.get_type()], reverse=True)

        for row in self.grid[6:8]:
            for piece in row:
                self.pieces[BLACK].append(piece)
        self.pieces[BLACK].sort(key=lambda piece: VALUES[piece.get_type()], reverse=True)

        # Current turn of Game
        self.turn = 0

        # Information about whether each player is in check
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

        # Winner of game, defaults to None
        self.winner = None

    def __str__(self):
        grid_str = "  abcdefgh\n  --------\n"
        for index, row in enumerate(self.grid):
            grid_str += f"{index + 1}|"
            for element in row:
                if element is None:
                    grid_str += "."
                else:
                    grid_str += element.__str__()
            if index != len(self.grid) - 1:
                grid_str += '\n'

        return grid_str

    def get_pieces(self, colour):
        """
        Returns all remaining BLACK/WHITE pieces remaining in play.

        Args:
            colour (string literal): BLACK or WHITE.

        Returns:
            List: List of BLACK/WHITE pieces.
        """
        return self.pieces[colour]

    def get_pieces_str(self, colour):
        pieces = self.pieces[colour]
        return [f"{piece.get_type()} {piece.get_pos()}" for piece in pieces]

    def move_piece(self, curr_row, curr_col, new_row, new_col):
        """
        Moves piece at (curr_row, curr_col) to (new_row, new_col).

        Args:
            curr_row (int): row co-ordinate in grid.
            curr_col (int): col co-ordinate in grid.
            new_row (int): row co-ordinate in grid.
            new_col (int): col co-ordinate in grid.

        Raises:
            ValueError: Either (curr_row, curr_col) or (new_row, new_col) points to position 
                        out of grid.
            ValueError: No piece exists at position (curr_row, curr_col).
            ValueError: Piece at (curr_row, curr_col) is the opponents.
            ValueError: Piece cannot move to (new_row, new_col).
            ValueError: Position (new_row, new_col) is the opponent's King, which you 
                        cannot capture.
        """

        if not (in_bounds((curr_row, curr_col)) and in_bounds((new_row, new_col))):
            raise ValueError("Coordinates not between 0 and 7")

        piece = self.grid[curr_row][curr_col]

        if piece is None:
            raise ValueError("No piece selected")

        player = self.whose_turn()
        opponent = BLACK if player == WHITE else WHITE

        if piece.get_colour() != player:
            raise ValueError("Cannot move an opponents piece")

        available_moves = piece.available_moves(self)
        if (new_row, new_col) not in available_moves:
            raise ValueError("Move not valid")

        target_piece = self.grid[new_row][new_col]

        if target_piece == self.king[opponent]:
            raise ValueError("Cannot capture opponent's King")

        # Capture opposing target_piece
        if target_piece is not None:
            self.pieces[opponent].remove(target_piece)

        # Check if moving piece will cause a discovered check
        discovered_check_piece = piece.discovered_check((new_row, new_col), self)
        if discovered_check_piece is not None:
            self.check[opponent]['pieces_causing_check'].append(discovered_check_piece)
            self.check[opponent]['in_check'] = True

        # Move piece, update turn count
        piece.set_pos((new_row, new_col))
        self.grid[curr_row][curr_col] = None
        self.grid[new_row][new_col] = piece
        self.turn += 1

        if piece.get_type() == PAWN:
            piece.set_has_moved()

        # Take your King out of check by either moving king, capturing piece or blocking
        if piece.get_type() == KING and self.check[player]['in_check']:
            self.check[player]['pieces_causing_check'].clear()
            self.check[player]['in_check'] = False
        elif target_piece in self.check[player]['pieces_causing_check']:
            self.check[player]['pieces_causing_check'].remove(target_piece)
            self.check[player]['in_check'] = len(self.check[player]['pieces_causing_check']) > 1
        elif self.check[player]['in_check']:
            for checking_piece in self.check[player]['pieces_causing_check']:
                if in_line(self.king[player].get_pos(), checking_piece.get_pos(), piece.get_pos()):
                    self.check[player]['pieces_causing_check'].remove(checking_piece)
            self.check[player]['in_check'] = len(self.check[player]['pieces_causing_check']) > 1

        # Place Oppossing King in Check, note a King can't place an opposing King in Check
        if piece.get_type() != KING:
            new_available_moves = piece.available_moves(self)
            if self.king[opponent].get_pos() in new_available_moves:
                self.check[opponent]['in_check'] = True
                self.check[opponent]['pieces_causing_check'].append(piece)

        # If opponent now has no possible moves they are either in checkmate (if they are in check)
        # or the game has ended in stalemate
        if self.no_available_moves(opponent):
            self.winner = player if self.is_in_check(opponent) else STALEMATE

    def get_piece(self, row, col):
        """
        Returns the piece in grid at position (row, col).

        Args:
            row (int): Row co-ordinate in grid.
            col (int): Col co-ordinate in grid.

        Returns:
            Piece: Returns Piece at grid[row][col].
        """
        return self.grid[row][col]

    def whose_turn(self):
        """
        Determines whose turn it is (BLACK/WHITE).

        Returns:
            string literal: Returns BLACK/WHITE.
        """
        if self.turn % 2 == 0:
            return WHITE
        else:
            return BLACK

    def is_in_check(self, colour):
        """
        Determines if player is in check or not.

        Args:
            colour (string literal): Player BLACK/WHITE.

        Returns:
            Bool: True if player is in check, else returns False. 
        """
        return self.check[colour]['in_check']

    def no_available_moves(self, colour):
        """
        Determines if player has no available moves.

        Args:
            colour (string literal): Player BLACK/WHITE.

        Returns:
            Bool: Returns True if player has no possible moves, else returns False.
        """
        pieces = self.pieces[colour][::-1]
        for piece in pieces:
            moves = piece.available_moves(self)
            if len(moves) > 0:
                return False

        return True
    
    def get_checking_pieces_pos(self, colour):
        """
        Returns the positions of all pieces causing check for colour's King

        Args:
            colour (string literal): Player BLACK/WHITE.

        Returns:
            List: Returns list of pos (row, col) all pieces causing check. 
        """
        return [piece.get_pos() for piece in self.check[colour]['pieces_causing_check']]