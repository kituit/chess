# Hello World

BLACK = "Black"
WHITE = "White"

PAWN = "P"

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

class Pawn(Piece):

    def __init__(self, row, col, colour):
        Piece.__init__(self, row, col, colour)
        self.type = PAWN

    def __str__(self):
        return PAWN


class Board:

    def __init__(self):
        self.grid = [[None for x in range(8)] for y in range(8)]
        self.grid[1] = [Pawn(1, x, WHITE) for x in range(8)]
        self.grid[-2] = [Pawn(1, x, BLACK) for x in range(8)]

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

    def move_piece(self, curr_row, curr_col, new_row, new_col):
        piece = self.grid[curr_row][curr_col]
        piece.set_pos(new_row, new_col)
        self.grid[curr_row][curr_col] = None
        self.grid[new_row][new_col] = piece  
                

if __name__ == '__main__':
    b = Board()
    print(b)

    print("==========")

    b.move_piece(1, 0, 2, 0)
    print(b)
