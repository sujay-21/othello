# ♟ Othello (Reversi) – Full-Stack Web Game

A complete, production-quality Othello game built with Flask, SQLAlchemy, and Vanilla JavaScript. Features a powerful AI opponent using Minimax with Alpha-Beta Pruning.

---

## 🚀 Quick Start

```bash
# 1. Clone or extract the project
cd othello

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python app.py

# 4. Open in browser
# http://127.0.0.1:5000
```

---

## 📁 Project Structure

```
othello/
├── app.py                  # Flask application factory & entry point
├── config.py               # Environment configuration
├── requirements.txt        # Python dependencies
│
├── models/
│   ├── __init__.py         # SQLAlchemy db instance
│   └── game.py             # Game database model
│
├── ai/
│   ├── minimax.py          # Minimax + Alpha-Beta Pruning
│   └── evaluation.py       # Board evaluation heuristics
│
├── routes/
│   ├── game_routes.py      # HTML page routes
│   └── api_routes.py       # REST API endpoints
│
├── services/
│   ├── board_service.py    # Pure Othello board logic
│   └── game_service.py     # Game state management + DB integration
│
├── static/
│   ├── css/style.css       # Full game styling (art-deco noir theme)
│   └── js/
│       ├── game.js         # Board rendering + game flow
│       └── history.js      # Match history page
│
├── templates/
│   ├── index.html          # Main SPA (home + game)
│   └── history.html        # Match history & statistics
│
└── database/
    └── othello.db          # SQLite database (auto-created)
```

---

## 🎮 Game Modes

| Mode | Description |
|------|-------------|
| **Player vs Player** | Two humans on the same device, alternating turns |
| **Player vs AI** | Human plays Black; AI (Minimax depth-4) plays White |

---

## 🤖 AI Details

The AI uses **Minimax with Alpha-Beta Pruning** (default depth = 4).

### Evaluation Function

The board heuristic weighs five factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Piece Difference | 10 | Raw disc count advantage |
| Corner Occupancy | 800 | Corners are permanent and highly valuable |
| Edge Occupancy | 50 | Edges provide stability |
| Mobility | 78 | Number of available moves |
| Corner Closeness | -20 | Penalty for dangerous squares near empty corners |

Move ordering (corners first) further accelerates pruning.

---

## 🌐 REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/start` | Start a new game `{ "mode": "pvp"/"pvai" }` |
| `GET`  | `/api/board` | Get current board state |
| `POST` | `/api/move` | Make a human move `{ "row": N, "col": N }` |
| `POST` | `/api/ai-move` | Trigger AI move (PvAI only) |
| `POST` | `/api/undo` | Undo last move |
| `GET`  | `/api/history` | All completed game records |
| `GET`  | `/api/stats` | Aggregate statistics |

---

## 🗄 Database Schema

```sql
CREATE TABLE games (
    id          INTEGER PRIMARY KEY,
    mode        VARCHAR(20),     -- 'pvp' or 'pvai'
    winner      VARCHAR(20),     -- 'Black', 'White', 'Draw'
    black_score INTEGER,
    white_score INTEGER,
    moves_played INTEGER,
    started_at  DATETIME,
    ended_at    DATETIME
);
```

---

## 🎨 Features

- ✅ Full Othello rules implementation
- ✅ Valid move highlighting with animated dots
- ✅ Smooth disc placement & flip animations
- ✅ Turn passing when no valid moves exist
- ✅ Undo move (2-step undo in PvAI mode)
- ✅ Restart game
- ✅ Match history stored in SQLite
- ✅ Statistics dashboard
- ✅ Game rules modal
- ✅ Responsive design (mobile-friendly)
- ✅ Art-deco noir UI theme

---

## 📦 Dependencies

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.23
Werkzeug==3.0.1
```

---

## 🔧 Configuration

Edit `config.py` or set environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `othello-secret-key-…` | Flask secret key |
| `DATABASE_URL` | `sqlite:///database/othello.db` | Database connection string |

---

## 📝 License

MIT — free to use and modify.
