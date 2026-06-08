"""
Flask routes for serving HTML pages.
"""
from flask import Blueprint, render_template

game_bp = Blueprint('game', __name__)


@game_bp.route('/')
def index():
    """Main menu / landing page."""
    return render_template('index.html')


@game_bp.route('/game')
def game():
    """Othello game board page."""
    return render_template('game.html')


@game_bp.route('/history')
def history():
    """Match history and statistics page."""
    return render_template('history.html')
