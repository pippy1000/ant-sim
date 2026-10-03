from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .game import ColonyGame

GAME = ColonyGame()

HTML_PAGE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Ant Colony Sim</title>
    <style>
      :root {
        --bg: #091318;
        --bg-2: #0d1e2b;
        --panel: rgba(20, 35, 43, 0.96);
        --panel-strong: rgba(13, 25, 31, 0.96);
        --panel-soft: rgba(24, 46, 58, 0.9);
        --border: rgba(167, 213, 255, 0.15);
        --accent: #7ce8ad;
        --accent-2: #7ec5ff;
        --gold: #f4cf78;
        --danger: #ff8d7d;
        --text: #edf8f3;
        --muted: #a8c3c0;
        --shadow: rgba(0, 0, 0, 0.28);
      }

      * { box-sizing: border-box; }

      body {
        margin: 0;
        font-family: "Segoe UI", Arial, sans-serif;
        background:
          radial-gradient(circle at top, rgba(124, 232, 173, 0.08), transparent 30%),
          linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%);
        color: var(--text);
      }

      .shell {
        max-width: 1200px;
        margin: 0 auto;
        padding: 28px 20px 40px;
      }

      .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 22px;
      }

      .title-wrap {
        display: flex;
        align-items: baseline;
        gap: 14px;
      }

      h1 {
        margin: 0;
        font-size: clamp(2.2rem, 5vw, 3.2rem);
        letter-spacing: -0.05em;
      }

      .subtitle {
        color: var(--muted);
        font-size: 0.9rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
      }

      .status-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 150px;
        padding: 10px 16px;
        border-radius: 999px;
        border: 1px solid rgba(124, 232, 173, 0.45);
        background: rgba(124, 232, 173, 0.12);
        color: var(--accent);
        font-weight: 700;
      }

      .layout {
        display: grid;
        grid-template-columns: 340px minmax(0, 1fr);
        gap: 20px;
      }

      .card {
        background: linear-gradient(180deg, var(--panel) 0%, var(--panel-soft) 100%);
        border: 1px solid var(--border);
        border-radius: 18px;
        box-shadow: 0 18px 36px var(--shadow);
      }

      .sidebar {
        display: flex;
        flex-direction: column;
        gap: 18px;
      }

      .hero {
        padding: 22px;
        background:
          linear-gradient(135deg, rgba(124, 232, 173, 0.12), rgba(126, 197, 255, 0.08)),
          linear-gradient(180deg, var(--panel) 0%, var(--panel-strong) 100%);
      }

      .hero .eyebrow {
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.72rem;
        margin-bottom: 8px;
      }

      .hero h2 {
        margin: 0 0 14px;
        font-size: 1.8rem;
      }

      .hero-stats {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
        margin-top: 18px;
      }

      .mini-stat {
        padding: 12px 13px;
        border-radius: 12px;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
      }

      .mini-label {
        display: block;
        color: var(--muted);
        font-size: 0.7rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 6px;
      }

      .mini-value {
        font-size: 1.5rem;
        font-weight: 800;
      }

      .main-panel {
        display: flex;
        flex-direction: column;
        gap: 18px;
      }

      .resource-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px;
      }

      .resource-card {
        padding: 18px 18px 16px;
      }

      .resource-card h3 {
        margin: 0 0 14px;
        color: var(--muted);
        font-size: 0.75rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
      }

      .resource-value {
        font-size: clamp(1.8rem, 4vw, 2.6rem);
        font-weight: 800;
        line-height: 1;
      }

      .resource-meta {
        margin-top: 12px;
        color: var(--muted);
        font-size: 0.9rem;
      }

      .action-card {
        padding: 18px;
      }

      .section-label {
        font-size: 0.7rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 16px;
      }

      .actions {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
      }

      button {
        appearance: none;
        border: none;
        border-radius: 12px;
        padding: 12px 16px;
        font-weight: 700;
        font-size: 0.96rem;
        cursor: pointer;
        color: #08151d;
        background: linear-gradient(180deg, var(--accent-2), #71aee9);
        box-shadow: 0 8px 16px rgba(83, 154, 220, 0.22);
        transition: transform 0.12s ease, box-shadow 0.12s ease;
      }

      button:hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 20px rgba(83, 154, 220, 0.25);
      }

      button.secondary {
        background: linear-gradient(180deg, var(--gold), #d3a850);
      }

      button.warning {
        background: linear-gradient(180deg, #ffb08a, #ef7d66);
      }

      button.ghost {
        background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
        color: var(--text);
        border: 1px solid var(--border);
        box-shadow: none;
      }

      .event-card {
        padding: 18px 20px;
      }

      .event-card h3 {
        margin: 0 0 12px;
        font-size: 0.75rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--muted);
      }

      #event-text {
        margin: 0;
        line-height: 1.5;
        color: var(--text);
        min-height: 56px;
        padding: 16px 18px;
        border-radius: 12px;
        background: rgba(0,0,0,0.12);
        border: 1px solid rgba(255,255,255,0.04);
      }

      @media (max-width: 860px) {
        .layout {
          grid-template-columns: 1fr;
        }

        .topbar {
          flex-direction: column;
          align-items: flex-start;
        }
      }
    </style>
  </head>
  <body>
    <div class="shell">
      <div class="topbar">
        <div class="title-wrap">
          <h1>Ant Colony Sim</h1>
          <span class="subtitle">idle command</span>
        </div>
        <div class="status-pill" id="auto-state">Auto-gather: ON</div>
      </div>

      <div class="layout">
        <aside class="sidebar">
          <div class="card hero">
            <div class="eyebrow">Colony overview</div>
            <h2>Queen's Nest</h2>
            <div class="hero-stats">
              <div class="mini-stat">
                <span class="mini-label">Turn</span>
                <span class="mini-value" id="turn">0</span>
              </div>
              <div class="mini-stat">
                <span class="mini-label">Nest</span>
                <span class="mini-value" id="nest-level">1</span>
              </div>
              <div class="mini-stat">
                <span class="mini-label">Workers</span>
                <span class="mini-value" id="workers">0</span>
              </div>
              <div class="mini-stat">
                <span class="mini-label">Soldiers</span>
                <span class="mini-value" id="soldiers">0</span>
              </div>
            </div>
          </div>
        </aside>

        <main class="main-panel">
          <div class="resource-grid">
            <div class="card resource-card">
              <h3>Food</h3>
              <div class="resource-value" id="food">0</div>
              <div class="resource-meta">+<span id="food-per-tick">0</span> / tick</div>
            </div>
            <div class="card resource-card">
              <h3>Workers</h3>
              <div class="resource-value" id="workers-value">0</div>
              <div class="resource-meta">Idle gain +<span id="idle-income">0</span></div>
            </div>
            <div class="card resource-card">
              <h3>Queen</h3>
              <div class="resource-value" id="queen-health">0</div>
              <div class="resource-meta">Health</div>
            </div>
            <div class="card resource-card">
              <h3>Threat</h3>
              <div class="resource-value" id="enemy-pressure">0</div>
              <div class="resource-meta">Enemy pressure</div>
            </div>
          </div>

          <div class="card action-card">
            <div class="section-label">Colony actions</div>
            <div class="actions">
              <button data-action="tick">Gather</button>
              <button class="secondary" data-action="hire_worker">Hire Worker</button>
              <button class="secondary" data-action="train_soldier">Train Soldier</button>
              <button class="secondary" data-action="upgrade_nest">Upgrade Nest</button>
              <button class="warning" data-action="battle">Battle</button>
              <button class="ghost" data-action="toggle_idle">Toggle Idle</button>
            </div>
          </div>

          <div class="card event-card">
            <h3>Colony log</h3>
            <p id="event-text">The queen wakes the colony.</p>
          </div>
        </main>
      </div>
    </div>

    <script>
      async function callAction(action) {
        const response = await fetch('/api/action', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action })
        });
        const data = await response.json();
        renderState(data);
      }

      function renderState(data) {
        document.getElementById('food').textContent = data.food;
        document.getElementById('workers').textContent = data.workers;
        document.getElementById('workers-value').textContent = data.workers;
        document.getElementById('soldiers').textContent = data.soldiers;
        document.getElementById('nest-level').textContent = data.nest_level;
        document.getElementById('queen-health').textContent = data.queen_health;
        document.getElementById('enemy-pressure').textContent = data.enemy_pressure;
        document.getElementById('food-per-tick').textContent = data.food_per_tick;
        document.getElementById('idle-income').textContent = data.idle_income;
        document.getElementById('auto-state').textContent = `Auto-gather: ${data.auto_gather ? 'ON' : 'OFF'}`;
        document.getElementById('turn').textContent = data.turn;
        document.getElementById('event-text').textContent = data.last_event;
      }

      async function refreshStatus() {
        const response = await fetch('/api/status');
        const data = await response.json();
        renderState(data);
      }

      document.querySelectorAll('[data-action]').forEach((button) => {
        button.addEventListener('click', () => callAction(button.dataset.action));
      });

      refreshStatus();
      setInterval(refreshStatus, 1500);
    </script>
  </body>
</html>
"""


class ColonyRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            self._send_html(HTML_PAGE)
            return

        if self.path == "/api/status":
            self._send_json(GAME.to_dict())
            return

        self.send_error(404, "Not found")

    def do_POST(self) -> None:
        if self.path != "/api/action":
            self.send_error(404, "Not found")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            payload: dict[str, Any] = json.loads(raw.decode("utf-8") or "{}")
        except (ValueError, TypeError, json.JSONDecodeError):
            self._send_json({"error": "Invalid JSON payload"}, status=400)
            return

        action = str(payload.get("action") or payload.get("command") or "").strip().lower()
        if not action:
            self._send_json({"error": "Action required"}, status=400)
            return

        action_map = {
            "tick": "tick",
            "gather": "tick",
            "advance": "tick",
            "hire_worker": "hire_worker",
            "hire": "hire_worker",
            "worker": "hire_worker",
            "train_soldier": "recruit_soldier",
            "train": "recruit_soldier",
            "soldier": "recruit_soldier",
            "upgrade_nest": "upgrade_nest",
            "upgrade": "upgrade_nest",
            "nest": "upgrade_nest",
            "battle": "battle",
            "raid": "battle",
            "toggle_idle": "toggle_idle",
            "idle": "toggle_idle",
            "auto": "toggle_idle",
            "status": "status",
        }

        command = action_map.get(action, action)

        if command == "tick":
            GAME.tick()
        elif command == "hire_worker":
            GAME.hire_worker()
        elif command == "recruit_soldier":
            GAME.recruit_soldier()
        elif command == "upgrade_nest":
            GAME.upgrade_nest()
        elif command == "battle":
            GAME.battle()
        elif command == "toggle_idle":
            GAME.toggle_idle()
        elif command == "status":
            pass
        else:
            self._send_json({"error": f"Unknown action: {action}"}, status=400)
            return

        self._send_json(GAME.to_dict())


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8000), ColonyRequestHandler)
    print("Ant Colony Sim web app running at http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
