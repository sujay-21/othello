/**
 * Othello – Main game JavaScript
 * Handles UI rendering, API communication, and game flow.
 */

// ── Constants ──────────────────────────────────────────────────
const EMPTY = 0, BLACK = 1, WHITE = 2;
const BOARD_SIZE = 8;

// ── State ──────────────────────────────────────────────────────
let state = null;     // Last received game state from server
let mode = 'pvp';     // Current game mode
let isAnimating = false;
let prevBoard = null; // For detecting which cells changed

// ── DOM References ─────────────────────────────────────────────
const boardEl        = document.getElementById('game-board');
const blackScoreEl   = document.getElementById('black-score');
const whiteScoreEl   = document.getElementById('white-score');
const blackTurnEl    = document.getElementById('black-turn-ind');
const whiteTurnEl    = document.getElementById('white-turn-ind');
const statusBarEl    = document.getElementById('status-bar');
const gameOverlay    = document.getElementById('game-over-overlay');
const winnerTextEl   = document.getElementById('winner-text');
const finalScoresEl  = document.getElementById('final-scores');
const aiThinkingEl   = document.getElementById('ai-thinking');
const undoBtn        = document.getElementById('btn-undo');
const passToast      = document.getElementById('pass-toast');

// ── API Helpers ────────────────────────────────────────────────
async function api(path, method = 'GET', body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body !== null) opts.body = JSON.stringify(body);
  const res = await fetch('/api' + path, opts);
  return res.json();
}

// ── Game Lifecycle ─────────────────────────────────────────────
async function startGame(gameMode) {
  mode = gameMode;
  prevBoard = null;
  isAnimating = false;

  // Hide overlay if visible
  gameOverlay.classList.remove('visible');

  const data = await api('/start', 'POST', { mode });
  if (data.error) { showStatus('⚠ ' + data.error); return; }

  state = data;
  renderBoard(data);
  updateScoreboard(data);
  updateStatus(data);

  document.getElementById('game-page').style.display = 'block';
  document.getElementById('home-page') && (document.getElementById('home-page').style.display = 'none');
}

// ── Board Rendering ────────────────────────────────────────────
function renderBoard(data) {
  const board     = data.board;
  const validSet  = new Set(data.valid_moves.map(([r, c]) => `${r},${c}`));

  // On first render, build all cells
  if (!prevBoard) {
    boardEl.innerHTML = '';
    for (let r = 0; r < BOARD_SIZE; r++) {
      for (let c = 0; c < BOARD_SIZE; c++) {
        const cell = createCell(r, c);
        boardEl.appendChild(cell);
      }
    }
  }

  // Update each cell
  const cells = boardEl.querySelectorAll('.cell');
  cells.forEach((cell, idx) => {
    const r = Math.floor(idx / BOARD_SIZE);
    const c = idx % BOARD_SIZE;
    const val = board[idx];
    const key = `${r},${c}`;
    const prev = prevBoard ? prevBoard[idx] : -1;

    // Clear classes
    cell.className = 'cell';
    if (validSet.has(key) && !data.game_over) cell.classList.add('valid');

    // Manage disc element
    let discEl = cell.querySelector('.disc');
    const dotEl = cell.querySelector('.valid-dot');

    if (val === EMPTY) {
      if (discEl) discEl.remove();
      if (!dotEl && validSet.has(key) && !data.game_over) {
        const dot = document.createElement('div');
        dot.className = 'valid-dot';
        cell.appendChild(dot);
      } else if (dotEl && (!validSet.has(key) || data.game_over)) {
        dotEl.remove();
      }
    } else {
      if (dotEl) dotEl.remove();

      if (!discEl) {
        // Place new disc
        discEl = document.createElement('div');
        discEl.className = `disc ${val === BLACK ? 'black' : 'white'} placing`;
        discEl.addEventListener('animationend', () => discEl.classList.remove('placing'), { once: true });
        cell.appendChild(discEl);
      } else if (prev !== val && prev !== -1) {
        // Flip animation
        const newColor = val === BLACK ? 'black' : 'white';
        const flipClass = val === BLACK ? 'flipping-to-black' : 'flipping-to-white';
        discEl.classList.remove('black', 'white');
        discEl.classList.add(newColor, flipClass);
        discEl.addEventListener('animationend', () => discEl.classList.remove(flipClass), { once: true });
      }
    }
  });

  prevBoard = [...board];
}

function createCell(r, c) {
  const cell = document.createElement('div');
  cell.className = 'cell';
  cell.dataset.row = r;
  cell.dataset.col = c;
  cell.addEventListener('click', () => handleCellClick(r, c));
  return cell;
}

// ── Click Handler ──────────────────────────────────────────────
async function handleCellClick(row, col) {
  if (!state || state.game_over || isAnimating) return;
  if (mode === 'pvai' && state.current_player === WHITE) return;

  // Check move is in valid list
  const isValid = state.valid_moves.some(([r, c]) => r === row && c === col);
  if (!isValid) return;

  isAnimating = true;
  const data = await api('/move', 'POST', { row, col });
  if (data.error) { showStatus('⚠ ' + data.error); isAnimating = false; return; }

  state = data;
  renderBoard(data);
  updateScoreboard(data);
  updateStatus(data);

  if (data.game_over) {
    isAnimating = false;
    showGameOver(data);
    return;
  }

  // PvAI: if AI's turn, trigger AI move
  if (mode === 'pvai' && data.current_player === WHITE) {
    await doAiMove();
  } else {
    isAnimating = false;
  }
}

// ── AI Move ────────────────────────────────────────────────────
async function doAiMove() {
  showAiThinking(true);
  // Small delay for UX
  await sleep(400);

  const data = await api('/ai-move', 'POST');
  showAiThinking(false);

  if (data.error) { showStatus('⚠ ' + data.error); isAnimating = false; return; }

  state = data;
  renderBoard(data);
  updateScoreboard(data);
  updateStatus(data);

  if (data.game_over) {
    showGameOver(data);
  }

  isAnimating = false;
}

// ── Undo ───────────────────────────────────────────────────────
async function undoMove() {
  if (!state || isAnimating) return;
  const data = await api('/undo', 'POST');
  if (data.error) { showStatus('⚠ ' + data.error); return; }

  prevBoard = null;  // Force full re-render
  state = data;
  renderBoard(data);
  updateScoreboard(data);
  updateStatus(data);
  gameOverlay.classList.remove('visible');
}

// ── UI Updates ─────────────────────────────────────────────────
function updateScoreboard(data) {
  blackScoreEl.textContent = data.black_score;
  whiteScoreEl.textContent = data.white_score;

  const blackPanel = document.querySelector('.player-panel.black-panel');
  const whitePanel = document.querySelector('.player-panel.white-panel');

  if (blackPanel && whitePanel) {
    if (data.current_player === BLACK && !data.game_over) {
      blackPanel.classList.add('active');
      whitePanel.classList.remove('active');
    } else if (data.current_player === WHITE && !data.game_over) {
      whitePanel.classList.add('active');
      blackPanel.classList.remove('active');
    } else {
      blackPanel.classList.remove('active');
      whitePanel.classList.remove('active');
    }
  }

  if (undoBtn) undoBtn.disabled = !data.can_undo;
}

function updateStatus(data) {
  if (data.game_over) {
    showStatus(`Game over — ${data.winner} wins!`);
    return;
  }

  const playerName = data.current_player === BLACK
    ? (mode === 'pvai' ? 'Your Turn (Black)' : 'Black\'s Turn')
    : (mode === 'pvai' ? 'AI Thinking…' : 'White\'s Turn');

  showStatus(playerName);
}

function showStatus(msg) {
  if (statusBarEl) statusBarEl.textContent = msg;
}

function showAiThinking(on) {
  if (aiThinkingEl) aiThinkingEl.classList.toggle('visible', on);
  if (statusBarEl)  statusBarEl.style.display = on ? 'none' : 'flex';
}

function showGameOver(data) {
  if (!gameOverlay) return;
  winnerTextEl.textContent =
    data.winner === 'Draw' ? '⬤ It\'s a Draw! ⬤' : `${data.winner} Wins!`;
  finalScoresEl.textContent =
    `Black ${data.black_score} – ${data.white_score} White`;
  gameOverlay.classList.add('visible');
}

function showPassToast(msg) {
  passToast.textContent = msg;
  passToast.classList.add('show');
  setTimeout(() => passToast.classList.remove('show'), 2200);
}

// ── Utilities ──────────────────────────────────────────────────
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── Public API (called from HTML) ──────────────────────────────
window.startGame = startGame;
window.undoMove  = undoMove;

window.restartGame = async function () {
  gameOverlay.classList.remove('visible');
  await startGame(mode);
};

window.goHome = function () {
  document.getElementById('game-page').style.display = 'none';
  document.getElementById('home-page').style.display = 'flex';
};
