import os
from chess import Board, in_bounds, ROW, COL, STALEMATE

def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


def get_moves(input_str):
    """
    Takes in input from player and returns corresponding grid co-ordinates.

    Args:
        input_str (string): Input string for text based game.

    Raises:
        ValueError: Player did not enter two co-ordinates.
        ValueError: Co-ordinate must consist of 2 characters.
        ValueError: Co-ordinate must be of form <letter><number>.
        ValueError: Co-ordinates are outside of grid.

    Returns:
        Tuple, Tuple: Returns two Tuples of form (row, col).
    """

    inputs = input_str.split()

    if len(inputs) != 2:
        raise ValueError("Must enter two co-ordinates in grid")

    move1 = inputs[0]
    move2 = inputs[1]

    if len(move1) != 2 or len(move2) != 2:
        raise ValueError("Co-ordinate must be two characters")

    if not (move1[0].isalpha() and move1[1].isnumeric()) or not (move2[0].isalpha()
                                                                 and move2[1].isnumeric()):
        raise ValueError("Co-ordinate must be of form <letter><number>")

    def move_to_pos(move):
        row = int(move[1]) - 1
        col = ord(move[0].lower()) - 97
        pos = (row, col)
        if not in_bounds(pos):
            raise ValueError("Co-ordinates are outside of grid")
        return (row, col)

    return move_to_pos(move1), move_to_pos(move2)


if __name__ == '__main__':
    b = Board()

    while b.winner is None:
        clear_console()
        print(b)
        player = b.whose_turn()
        while True:
            try:
                input_str = input(
                    f"Player {player}{' - Check' if b.is_in_check(player) else ''} - Enter Move: ")
                curr_pos, new_pos = get_moves(input_str)
                b.move_piece(curr_pos[ROW], curr_pos[COL], new_pos[ROW], new_pos[COL])
                break
            except ValueError:
                print("Invalid Move")

    if b.winner == STALEMATE:
        print("Stalemate!!")
    else:
        print(f"Congrats {b.winner}, you win!!!")