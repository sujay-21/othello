/**
 * Othello – Match History page JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  loadStats();
  loadHistory();
});

async function loadStats() {
  try {
    const data = await fetch('/api/stats').then(r => r.json());

    setText('stat-total',   data.total_games  ?? 0);
    setText('stat-pvp',     data.pvp_games    ?? 0);
    setText('stat-pvai',    data.pvai_games   ?? 0);
    setText('stat-black',   data.black_wins   ?? 0);
    setText('stat-white',   data.white_wins   ?? 0);
    setText('stat-draws',   data.draws        ?? 0);
    setText('stat-ai',      data.ai_wins      ?? 0);
    setText('stat-human',   data.human_wins   ?? 0);
    setText('stat-avg',     data.avg_moves    ?? 0);
  } catch (e) {
    console.error('Failed to load stats:', e);
  }
}

async function loadHistory() {
  const tbody = document.getElementById('history-tbody');
  const emptyState = document.getElementById('empty-state');

  try {
    const data = await fetch('/api/history').then(r => r.json());
    const games = data.games || [];

    if (games.length === 0) {
      emptyState && (emptyState.style.display = 'block');
      return;
    }

    emptyState && (emptyState.style.display = 'none');

    tbody.innerHTML = games.map((g, i) => `
      <tr>
        <td>${games.length - i}</td>
        <td><span class="badge badge-${g.mode}">${g.mode === 'pvp' ? 'PvP' : 'PvAI'}</span></td>
        <td><span class="badge badge-${winnerClass(g.winner)}">${g.winner ?? '—'}</span></td>
        <td>${g.black_score} – ${g.white_score}</td>
        <td>${g.moves_played}</td>
        <td>${formatDate(g.ended_at)}</td>
        <td>${formatDuration(g.duration_seconds)}</td>
      </tr>
    `).join('');

  } catch (e) {
    console.error('Failed to load history:', e);
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--text-muted)">Failed to load history.</td></tr>`;
  }
}

// ── Helpers ────────────────────────────────────────────────────
function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function winnerClass(winner) {
  if (!winner) return 'draw';
  return winner.toLowerCase() === 'draw' ? 'draw' : winner.toLowerCase();
}

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
    + ' ' + d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}

function formatDuration(secs) {
  if (!secs) return '—';
  if (secs < 60) return `${secs}s`;
  return `${Math.floor(secs / 60)}m ${secs % 60}s`;
}
