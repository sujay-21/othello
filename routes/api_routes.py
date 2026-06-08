"""
REST API endpoints for the Othello application.
All endpoints return JSON.
"""
from flask import Blueprint, request, jsonify
from services import game_service, board_service
from ai.minimax import get_best_move, DEFAULT_DEPTH

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ─── Helpers ────────────────────────────────────────────────────────────────

def _error(msg, code=400):
    return jsonify({'error': msg}), code


# ─── POST /api/start ────────────────────────────────────────────────────────

@api_bp.route('/start', methods=['POST'])
def start():
    """
    Start a new game.
    Body: { "mode": "pvp" | "pvai" }
    Returns: { "game_id": <int>, ...state }
    """
    data = request.get_json(silent=True) or {}
    mode = data.get('mode', 'pvp')
    if mode not in ('pvp', 'pvai'):
        return _error("mode must be 'pvp' or 'pvai'")

    game_id = game_service.start_game(mode)
    state = game_service.get_state()
    return jsonify({'game_id': game_id, **state})


# ─── GET /api/board ─────────────────────────────────────────────────────────

@api_bp.route('/board', methods=['GET'])
def board():
    """Return the current board state."""
    state = game_service.get_state()
    if state is None:
        return _error('No active game. Start a game first.', 404)
    return jsonify(state)


# ─── POST /api/move ─────────────────────────────────────────────────────────

@api_bp.route('/move', methods=['POST'])
def move():
    """
    Make a human player move.
    Body: { "row": <int>, "col": <int> }
    Returns updated game state.
    """
    data = request.get_json(silent=True)
    if not data:
        return _error('Request body must be JSON with row and col.')

    row = data.get('row')
    col = data.get('col')

    if row is None or col is None:
        return _error('row and col are required.')
    if not isinstance(row, int) or not isinstance(col, int):
        return _error('row and col must be integers.')
    if not (0 <= row < 8 and 0 <= col < 8):
        return _error('row and col must be in range 0-7.')

    try:
        state = game_service.make_move(row, col)
        return jsonify(state)
    except ValueError as e:
        return _error(str(e))


# ─── POST /api/ai-move ──────────────────────────────────────────────────────

@api_bp.route('/ai-move', methods=['POST'])
def ai_move():
    """
    Compute and apply the AI's move (White in PvAI mode).
    Returns updated game state including the chosen move.
    """
    state = game_service.get_state()
    if state is None:
        return _error('No active game.', 404)
    if state['mode'] != 'pvai':
        return _error('AI move is only available in PvAI mode.')
    if state['game_over']:
        return _error('Game is already over.')
    if state['current_player'] != board_service.WHITE:
        return _error('It is not the AI\'s turn.')

    data = request.get_json(silent=True) or {}
    depth = int(data.get('depth', DEFAULT_DEPTH))
    depth = max(1, min(depth, 8))   # Clamp to safe range

    board_2d = board_service.list_to_board(state['board'])
    best = get_best_move(board_2d, depth)

    if best is None:
        # AI has no moves → advance turn manually
        state['current_player'] = board_service.BLACK
        return jsonify({**state, 'ai_move': None, 'message': 'AI passes.'})

    row, col = best
    try:
        new_state = game_service.make_move(row, col)
        return jsonify({**new_state, 'ai_move': {'row': row, 'col': col}})
    except ValueError as e:
        return _error(str(e))


# ─── POST /api/undo ─────────────────────────────────────────────────────────

@api_bp.route('/undo', methods=['POST'])
def undo():
    """Undo the last move (or last two moves in PvAI mode)."""
    try:
        state = game_service.undo_move()
        return jsonify(state)
    except ValueError as e:
        return _error(str(e))


# ─── GET /api/history ───────────────────────────────────────────────────────

@api_bp.route('/history', methods=['GET'])
def history():
    """Return all completed game records."""
    games = game_service.get_history()
    return jsonify({'games': games, 'count': len(games)})


# ─── GET /api/stats ─────────────────────────────────────────────────────────

@api_bp.route('/stats', methods=['GET'])
def stats():
    """Return aggregate game statistics."""
    return jsonify(game_service.get_statistics())
