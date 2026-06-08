"""
Game model using sqlite3 (no external ORM).
"""
from datetime import datetime
from models import get_connection


class Game:
    """Represents a stored Othello game record."""

    def __init__(self, row=None):
        if row:
            self.id           = row['id']
            self.mode         = row['mode']
            self.winner       = row['winner']
            self.black_score  = row['black_score']
            self.white_score  = row['white_score']
            self.moves_played = row['moves_played']
            self.started_at   = row['started_at']
            self.ended_at     = row['ended_at']

    @classmethod
    def create(cls, mode):
        """Insert a new game record and return its id."""
        now = datetime.utcnow().isoformat()
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO games (mode, started_at) VALUES (?, ?)",
                (mode, now)
            )
            conn.commit()
            return cur.lastrowid

    @classmethod
    def get(cls, game_id):
        """Fetch a game by primary key."""
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
        return cls(row) if row else None

    @classmethod
    def update_result(cls, game_id, winner, black_score, white_score, moves_played):
        """Persist game result when a game ends."""
        now = datetime.utcnow().isoformat()
        with get_connection() as conn:
            conn.execute(
                """UPDATE games
                   SET winner=?, black_score=?, white_score=?, moves_played=?, ended_at=?
                   WHERE id=?""",
                (winner, black_score, white_score, moves_played, now, game_id)
            )
            conn.commit()

    @classmethod
    def get_completed(cls):
        """Return all finished games, newest first."""
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM games WHERE ended_at IS NOT NULL ORDER BY ended_at DESC"
            ).fetchall()
        return [cls(r) for r in rows]

    def to_dict(self):
        started = self.started_at
        ended   = self.ended_at
        duration = None
        if started and ended:
            try:
                s = datetime.fromisoformat(started)
                e = datetime.fromisoformat(ended)
                duration = int((e - s).total_seconds())
            except Exception:
                pass
        return {
            'id':               self.id,
            'mode':             self.mode,
            'winner':           self.winner,
            'black_score':      self.black_score,
            'white_score':      self.white_score,
            'moves_played':     self.moves_played,
            'started_at':       started,
            'ended_at':         ended,
            'duration_seconds': duration,
        }

    def __repr__(self):
        return f'<Game id={self.id} mode={self.mode} winner={self.winner}>'
