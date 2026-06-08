"""
Game service: manages in-memory game state and coordinates
between board logic, AI, and the database.
"""
from services.board_service import (
    create_initial_board, apply_move, get_valid_moves,
    count_pieces, is_game_over, get_winner, copy_board,
    board_to_list, BLACK, WHITE
)
from models.game import Game

# In-memory game state (single active game per server instance)
_game_state = {}


def _reset_state():
    _game_state.clear()


def start_game(mode):
    """
    Initialise a new game.
    mode: 'pvp' or 'pvai'.
    Returns the newly created Game id.
    """
    _reset_state()
    board = create_initial_board()
    game_id = Game.create(mode)

    _game_state.update({
        'board':         board,
        'current_player': BLACK,
        'mode':          mode,
        'history':       [],
        'moves_played':  0,
        'game_over':     False,
        'winner':        None,
        'db_id':         game_id,
    })
    return game_id


def get_state():
    """Return a JSON-serialisable snapshot of the current game state."""
    if not _game_state:
        return None

    board  = _game_state['board']
    player = _game_state['current_player']
    black, white = count_pieces(board)
    valid_moves  = get_valid_moves(board, player)

    return {
        'game_id':        _game_state['db_id'],
        'board':          board_to_list(board),
        'current_player': player,
        'black_score':    black,
        'white_score':    white,
        'valid_moves':    valid_moves,
        'game_over':      _game_state['game_over'],
        'winner':         _game_state['winner'],
        'mode':           _game_state['mode'],
        'moves_played':   _game_state['moves_played'],
        'can_undo':       len(_game_state['history']) > 0,
    }


def make_move(row, col):
    """Apply a human player move at (row, col)."""
    if not _game_state or _game_state['game_over']:
        raise ValueError("No active game or game already over.")

    board  = _game_state['board']
    player = _game_state['current_player']

    _game_state['history'].append(copy_board(board))
    new_board = apply_move(board, row, col, player)
    _game_state['board'] = new_board
    _game_state['moves_played'] += 1

    _advance_turn()
    return get_state()


def undo_move():
    """Revert to the previous board state."""
    if not _game_state or not _game_state['history']:
        raise ValueError("Nothing to undo.")

    if _game_state['mode'] == 'pvai' and len(_game_state['history']) >= 2:
        _game_state['history'].pop()
        _game_state['board'] = _game_state['history'].pop()
        _game_state['current_player'] = BLACK
        _game_state['moves_played'] = max(0, _game_state['moves_played'] - 2)
    else:
        _game_state['board'] = _game_state['history'].pop()
        opponent = WHITE if _game_state['current_player'] == BLACK else BLACK
        _game_state['current_player'] = opponent
        _game_state['moves_played'] = max(0, _game_state['moves_played'] - 1)

    _game_state['game_over'] = False
    _game_state['winner']    = None
    return get_state()


def _advance_turn():
    board    = _game_state['board']
    current  = _game_state['current_player']
    opponent = WHITE if current == BLACK else BLACK

    if get_valid_moves(board, opponent):
        _game_state['current_player'] = opponent
    elif not get_valid_moves(board, current):
        _end_game()
    # else: current player has moves; opponent passes – keep current player


def _end_game():
    board  = _game_state['board']
    winner = get_winner(board)
    black, white = count_pieces(board)

    _game_state['game_over'] = True
    _game_state['winner']    = winner

    Game.update_result(
        _game_state['db_id'],
        winner, black, white, _game_state['moves_played']
    )


def get_history():
    return [g.to_dict() for g in Game.get_completed()]


def get_statistics():
    all_games  = Game.get_completed()
    total      = len(all_games)
    pvai_games = [g for g in all_games if g.mode == 'pvai']
    pvp_games  = [g for g in all_games if g.mode == 'pvp']

    return {
        'total_games': total,
        'pvp_games':   len(pvp_games),
        'pvai_games':  len(pvai_games),
        'black_wins':  sum(1 for g in all_games if g.winner == 'Black'),
        'white_wins':  sum(1 for g in all_games if g.winner == 'White'),
        'draws':       sum(1 for g in all_games if g.winner == 'Draw'),
        'ai_wins':     sum(1 for g in pvai_games if g.winner == 'White'),
        'human_wins':  sum(1 for g in pvai_games if g.winner == 'Black'),
        'avg_moves':   round(sum(g.moves_played for g in all_games) / total, 1) if total else 0,
    }
