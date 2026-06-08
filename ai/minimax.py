"""
Minimax algorithm with Alpha-Beta Pruning for the Othello AI.

Entry point: get_best_move(board, depth=4) → (row, col)
"""
import math
from services.board_service import (
    BLACK, WHITE, get_valid_moves, apply_move, is_game_over, copy_board
)
from ai.evaluation import evaluate_board

DEFAULT_DEPTH = 4
INF = math.inf


def get_best_move(board, depth=DEFAULT_DEPTH):
    """
    Return the best (row, col) move for the AI (White player).
    Uses minimax with alpha-beta pruning.
    Returns None if no moves are available.
    """
    valid_moves = get_valid_moves(board, WHITE)
    if not valid_moves:
        return None

    best_score = -INF
    best_move = None
    alpha = -INF
    beta = INF

    # Order moves: prefer corners and positionally strong squares first
    ordered_moves = _order_moves(board, valid_moves, WHITE)

    for move in ordered_moves:
        row, col = move
        new_board = apply_move(board, row, col, WHITE)
        score = _minimax(new_board, depth - 1, alpha, beta, False)  # Black's turn next
        if score > best_score:
            best_score = score
            best_move = move
        alpha = max(alpha, score)

    return best_move


def _minimax(board, depth, alpha, beta, is_maximising):
    """
    Recursive minimax with alpha-beta pruning.

    is_maximising=True  → AI (White) is choosing
    is_maximising=False → Human (Black) is choosing
    """
    player = WHITE if is_maximising else BLACK

    # Terminal conditions
    if depth == 0 or is_game_over(board):
        return evaluate_board(board, WHITE)

    valid_moves = get_valid_moves(board, player)

    # Current player has no moves → pass turn
    if not valid_moves:
        return _minimax(board, depth - 1, alpha, beta, not is_maximising)

    ordered_moves = _order_moves(board, valid_moves, player)

    if is_maximising:
        max_eval = -INF
        for move in ordered_moves:
            new_board = apply_move(board, move[0], move[1], player)
            eval_score = _minimax(new_board, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Beta cut-off
        return max_eval
    else:
        min_eval = INF
        for move in ordered_moves:
            new_board = apply_move(board, move[0], move[1], player)
            eval_score = _minimax(new_board, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha cut-off
        return min_eval


def generate_moves(board, player):
    """Return ordered list of valid moves for `player`."""
    return _order_moves(board, get_valid_moves(board, player), player)


# ---------------------------------------------------------------------------
# Move ordering helpers
# ---------------------------------------------------------------------------

_CORNER_SET = {(0, 0), (0, 7), (7, 0), (7, 7)}

_POSITION_PRIORITY = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,   5,   1,   1,   5,  -2,  10],
    [  5,  -2,   1,   0,   0,   1,  -2,   5],
    [  5,  -2,   1,   0,   0,   1,  -2,   5],
    [ 10,  -2,   5,   1,   1,   5,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100],
]


def _order_moves(board, moves, player):
    """
    Sort moves so that stronger squares are explored first,
    improving alpha-beta pruning efficiency.
    """
    return sorted(moves, key=lambda m: _POSITION_PRIORITY[m[0]][m[1]], reverse=True)
