"""
Board service: pure logic for Othello board operations.
All functions are stateless and operate on plain Python lists.
"""

# Constants
EMPTY = 0
BLACK = 1
WHITE = 2
BOARD_SIZE = 8

# All 8 directions: (row_delta, col_delta)
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),           (0, 1),
              (1, -1),  (1, 0),  (1, 1)]


def create_initial_board():
    """
    Create and return an 8x8 board with the standard Othello starting position.
    Center: White at (3,3),(4,4); Black at (3,4),(4,3).
    """
    board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    board[3][3] = WHITE
    board[4][4] = WHITE
    board[3][4] = BLACK
    board[4][3] = BLACK
    return board


def copy_board(board):
    """Return a deep copy of the board."""
    return [row[:] for row in board]


def is_on_board(row, col):
    """Check whether (row, col) is within board boundaries."""
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def get_flips(board, row, col, player):
    """
    Return a list of (r, c) positions that would be flipped
    if `player` places a disc at (row, col).
    Returns an empty list if the move is invalid.
    """
    if board[row][col] != EMPTY:
        return []

    opponent = WHITE if player == BLACK else BLACK
    all_flips = []

    for dr, dc in DIRECTIONS:
        r, c = row + dr, col + dc
        line = []

        # Walk in this direction while we see opponent discs
        while is_on_board(r, c) and board[r][c] == opponent:
            line.append((r, c))
            r += dr
            c += dc

        # Valid only if we end on our own disc (after ≥1 opponent disc)
        if line and is_on_board(r, c) and board[r][c] == player:
            all_flips.extend(line)

    return all_flips


def is_valid_move(board, row, col, player):
    """Return True if placing `player` disc at (row, col) is a legal move."""
    return bool(get_flips(board, row, col, player))


def get_valid_moves(board, player):
    """Return a list of (row, col) tuples representing all valid moves for `player`."""
    return [
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if is_valid_move(board, r, c, player)
    ]


def apply_move(board, row, col, player):
    """
    Apply a move for `player` at (row, col), flipping captured discs.
    Returns the new board state. Raises ValueError on invalid move.
    """
    flips = get_flips(board, row, col, player)
    if not flips:
        raise ValueError(f"Invalid move at ({row}, {col}) for player {player}")

    new_board = copy_board(board)
    new_board[row][col] = player
    for r, c in flips:
        new_board[r][c] = player
    return new_board


def count_pieces(board):
    """Return (black_count, white_count) for the current board."""
    black = sum(board[r][c] == BLACK for r in range(BOARD_SIZE) for c in range(BOARD_SIZE))
    white = sum(board[r][c] == WHITE for r in range(BOARD_SIZE) for c in range(BOARD_SIZE))
    return black, white


def is_game_over(board):
    """Return True if neither player has any valid move."""
    return not get_valid_moves(board, BLACK) and not get_valid_moves(board, WHITE)


def get_winner(board):
    """
    Determine the winner of a finished game.
    Returns 'Black', 'White', or 'Draw'.
    """
    black, white = count_pieces(board)
    if black > white:
        return 'Black'
    elif white > black:
        return 'White'
    return 'Draw'


def board_to_list(board):
    """Flatten the 2D board into a single list for JSON serialisation."""
    return [cell for row in board for cell in row]


def list_to_board(flat):
    """Reconstruct a 2D board from a flat list."""
    return [flat[i * BOARD_SIZE:(i + 1) * BOARD_SIZE] for i in range(BOARD_SIZE)]
