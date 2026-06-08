"""
Board evaluation functions for the Othello AI.

The heuristic considers:
  1. Piece difference  – raw disc count advantage
  2. Corner occupancy  – corners are highly valuable (stable, cannot be flipped)
  3. Edge occupancy    – edges are moderately stable
  4. Mobility          – number of available moves (flexibility)
  5. Corner closeness  – penalty for occupying squares adjacent to un-taken corners
"""

from services.board_service import (
    BLACK, WHITE, BOARD_SIZE, get_valid_moves, count_pieces
)

# Positional weight table (higher = better square to occupy)
POSITION_WEIGHTS = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,   5,   1,   1,   5,  -2,  10],
    [  5,  -2,   1,   0,   0,   1,  -2,   5],
    [  5,  -2,   1,   0,   0,   1,  -2,   5],
    [ 10,  -2,   5,   1,   1,   5,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100],
]

CORNERS = [(0, 0), (0, 7), (7, 0), (7, 7)]

# Cells immediately adjacent to each corner (dangerous if corner is empty)
CORNER_ADJACENTS = {
    (0, 0): [(0, 1), (1, 0), (1, 1)],
    (0, 7): [(0, 6), (1, 7), (1, 6)],
    (7, 0): [(6, 0), (7, 1), (6, 1)],
    (7, 7): [(6, 7), (7, 6), (6, 6)],
}


def evaluate_board(board, player):
    """
    Return a single heuristic score for `player` on `board`.
    Positive values favour `player`; negative values favour the opponent.
    """
    opponent = WHITE if player == BLACK else BLACK

    piece_score = _piece_difference(board, player)
    corner_s = _corner_score(board, player)
    edge_s = _edge_score(board, player)
    mobility_s = _mobility_score(board, player)
    position_s = _position_score(board, player)
    corner_close_s = _corner_closeness_penalty(board, player)

    # Weights tuned empirically
    score = (
        10  * piece_score
        + 800 * corner_s
        + 50  * edge_s
        + 78  * mobility_s
        + 10  * position_s
        - 20  * corner_close_s
    )
    return score


def _piece_difference(board, player):
    """Normalised piece-count difference in [-1, 1] range."""
    opponent = WHITE if player == BLACK else BLACK
    p_count = sum(board[r][c] == player   for r in range(BOARD_SIZE) for c in range(BOARD_SIZE))
    o_count = sum(board[r][c] == opponent for r in range(BOARD_SIZE) for c in range(BOARD_SIZE))
    total = p_count + o_count
    if total == 0:
        return 0
    return (p_count - o_count) / total


def corner_score(board, player):
    """Public wrapper used by external callers."""
    return _corner_score(board, player)


def _corner_score(board, player):
    """Normalised corner occupancy difference."""
    opponent = WHITE if player == BLACK else BLACK
    p_corners = sum(1 for r, c in CORNERS if board[r][c] == player)
    o_corners = sum(1 for r, c in CORNERS if board[r][c] == opponent)
    total = p_corners + o_corners
    if total == 0:
        return 0
    return (p_corners - o_corners) / total


def edge_score(board, player):
    """Public wrapper used by external callers."""
    return _edge_score(board, player)


def _edge_score(board, player):
    """Normalised edge (non-corner) occupancy difference."""
    opponent = WHITE if player == BLACK else BLACK
    edges = (
        [(0, c) for c in range(1, 7)] +
        [(7, c) for c in range(1, 7)] +
        [(r, 0) for r in range(1, 7)] +
        [(r, 7) for r in range(1, 7)]
    )
    p_edge = sum(1 for r, c in edges if board[r][c] == player)
    o_edge = sum(1 for r, c in edges if board[r][c] == opponent)
    total = p_edge + o_edge
    if total == 0:
        return 0
    return (p_edge - o_edge) / total


def mobility_score(board, player):
    """Public wrapper used by external callers."""
    return _mobility_score(board, player)


def _mobility_score(board, player):
    """Normalised mobility (available move count) difference."""
    opponent = WHITE if player == BLACK else BLACK
    p_moves = len(get_valid_moves(board, player))
    o_moves = len(get_valid_moves(board, opponent))
    total = p_moves + o_moves
    if total == 0:
        return 0
    return (p_moves - o_moves) / total


def _position_score(board, player):
    """Sum of positional weights for player minus opponent."""
    opponent = WHITE if player == BLACK else BLACK
    score = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == player:
                score += POSITION_WEIGHTS[r][c]
            elif board[r][c] == opponent:
                score -= POSITION_WEIGHTS[r][c]
    return score


def _corner_closeness_penalty(board, player):
    """
    Penalty for occupying cells adjacent to an uncaptured corner.
    These cells give the opponent a path to the corner.
    """
    opponent = WHITE if player == BLACK else BLACK
    p_penalty = 0
    o_penalty = 0
    for corner, adj_cells in CORNER_ADJACENTS.items():
        cr, cc = corner
        if board[cr][cc] == 0:   # Corner is still empty
            for r, c in adj_cells:
                if board[r][c] == player:
                    p_penalty += 1
                elif board[r][c] == opponent:
                    o_penalty += 1
    return p_penalty - o_penalty
