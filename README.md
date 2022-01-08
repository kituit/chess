# Python Chess

Chess api written in Python, with gui created using pygame.

![GUI created with pygame](/src/img/sample_chess_interface2.png "Sample interface")

## Files

### 1. chess.py

Chess API. To use, create an instance of the provided Board class, which stores the current state of
the game. Each cell in board grid is either 

| Board Method                                     | Description                                                                                 |
|--------------------------------------------------|---------------------------------------------------------------------------------------------|
| get_piece(row, col)                              | Returns the piece object that is being stored in chess grid at position given by (row, col) |
| whose_turn()                                     | Returns whose turn it is (BLACK/WHITE)                                                      |
| move_piece(curr_row, curr_col, new_row, new_col) | Moves piece from (curr_row, curr_col) to (new_row, new_col)                                 |
| is_in_check(colour)                              | For a given player colour BLACK/WHITE, returns TRUE/FALSE if player is in check             |