"""
Othello (Reversi) Web Application
Entry point: python app.py
"""
import os
from flask import Flask
from models import init_db


def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'othello-secret-key')

    # Initialise the SQLite database
    init_db()

    # Register blueprints
    from routes.game_routes import game_bp
    from routes.api_routes import api_bp
    app.register_blueprint(game_bp)
    app.register_blueprint(api_bp)

    return app

app = create_app()
if __name__ == '__main__':
    print("╔══════════════════════════════════════════╗")
    print("║        OTHELLO – Server Starting          ║")
    print("║  Open http://127.0.0.1:5000 in browser   ║")
    print("╚══════════════════════════════════════════╝")
    app.run(host='127.0.0.1', port=5000, debug=True)
