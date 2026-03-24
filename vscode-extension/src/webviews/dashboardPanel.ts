/**
 * Pipeline Dashboard Webview Panel
 *
 * FR-010: Real-time pipeline progress with step visualization
 * FR-011: Context budget meter with color-coded warnings
 * FR-012: Clickable links to generated artifacts
 */

import * as vscode from "vscode";
import type { PipelineRunData } from "../types";

export class DashboardPanel {
  public static currentPanel: DashboardPanel | undefined;
  private static readonly viewType = "archon.dashboard";

  private readonly _panel: vscode.WebviewPanel;
  private _disposables: vscode.Disposable[] = [];
  private _currentRun: PipelineRunData | null = null;

  private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
    this._panel = panel;
    this._panel.webview.html = this._getHtml();

    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

    this._panel.webview.onDidReceiveMessage(
      (msg) => {
        switch (msg.command) {
          case "openArtifact":
            if (msg.path) {
              vscode.commands.executeCommand(
                "vscode.open",
                vscode.Uri.file(msg.path),
              );
            }
            break;
          case "refresh":
            vscode.commands.executeCommand("archon.refreshDashboard");
            break;
        }
      },
      null,
      this._disposables,
    );
  }

  public static show(extensionUri: vscode.Uri): DashboardPanel {
    if (DashboardPanel.currentPanel) {
      DashboardPanel.currentPanel._panel.reveal(vscode.ViewColumn.One);
      return DashboardPanel.currentPanel;
    }

    const panel = vscode.window.createWebviewPanel(
      DashboardPanel.viewType,
      "Archon — Pipeline Dashboard",
      vscode.ViewColumn.One,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
      },
    );

    DashboardPanel.currentPanel = new DashboardPanel(panel, extensionUri);
    return DashboardPanel.currentPanel;
  }

  public updateRun(run: PipelineRunData): void {
    this._currentRun = run;
    this._panel.webview.postMessage({ type: "update", data: run });
  }

  public showIdle(): void {
    this._currentRun = null;
    this._panel.webview.postMessage({ type: "idle" });
  }

  public dispose(): void {
    DashboardPanel.currentPanel = undefined;
    this._panel.dispose();
    for (const d of this._disposables) {
      d.dispose();
    }
    this._disposables = [];
  }

  private _getHtml(): string {
    return /*html*/ `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archon Pipeline Dashboard</title>
    <style>
        :root {
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --bg-card: #1e2a4a;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0b0;
            --accent-purple: #6c3fe8;
            --accent-blue: #3b82f6;
            --accent-green: #22c55e;
            --accent-yellow: #eab308;
            --accent-red: #ef4444;
            --border-color: #2a3a5e;
        }

        body {
            font-family: var(--vscode-font-family, 'Segoe UI', sans-serif);
            background: var(--vscode-editor-background, var(--bg-primary));
            color: var(--vscode-editor-foreground, var(--text-primary));
            margin: 0;
            padding: 20px;
            line-height: 1.5;
        }

        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--vscode-panel-border, var(--border-color));
        }

        .header h1 {
            margin: 0;
            font-size: 20px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .header .logo {
            display: inline-block;
            width: 24px;
            height: 24px;
            background: linear-gradient(135deg, #6c3fe8, #3b82f6);
            border-radius: 6px;
            text-align: center;
            line-height: 24px;
            font-size: 14px;
        }

        .header .status-badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .status-idle { background: var(--bg-card); color: var(--text-secondary); }
        .status-running { background: #1e3a5f; color: var(--accent-blue); }
        .status-complete { background: #1a3a2a; color: var(--accent-green); }
        .status-failed { background: #3a1a1a; color: var(--accent-red); }

        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 20px;
        }

        .card {
            background: var(--vscode-sideBar-background, var(--bg-card));
            border: 1px solid var(--vscode-panel-border, var(--border-color));
            border-radius: 8px;
            padding: 16px;
        }

        .card h2 {
            margin: 0 0 12px 0;
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
        }

        /* Pipeline Steps */
        .steps-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .step {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 12px;
            margin-bottom: 4px;
            border-radius: 6px;
            transition: background 0.15s;
        }

        .step:hover {
            background: var(--vscode-list-hoverBackground, rgba(255,255,255,0.05));
        }

        .step-number {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 12px;
            flex-shrink: 0;
        }

        .step-pending .step-number { background: #2a2a3e; color: var(--text-secondary); }
        .step-running .step-number { background: #1e3a5f; color: var(--accent-blue); animation: pulse 1.5s infinite; }
        .step-complete .step-number { background: #1a3a2a; color: var(--accent-green); }
        .step-failed .step-number { background: #3a1a1a; color: var(--accent-red); }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .step-info { flex: 1; }
        .step-name { font-weight: 600; font-size: 13px; }
        .step-agent { font-size: 11px; color: var(--text-secondary); }
        .step-status-icon { font-size: 16px; }

        /* Context Budget */
        .budget-meter {
            margin-top: 8px;
        }

        .budget-bar-track {
            width: 100%;
            height: 12px;
            background: var(--bg-primary);
            border-radius: 6px;
            overflow: hidden;
        }

        .budget-bar-fill {
            height: 100%;
            border-radius: 6px;
            transition: width 0.5s ease, background 0.3s;
        }

        .budget-green { background: linear-gradient(90deg, #22c55e, #16a34a); }
        .budget-yellow { background: linear-gradient(90deg, #eab308, #ca8a04); }
        .budget-red { background: linear-gradient(90deg, #ef4444, #dc2626); }

        .budget-labels {
            display: flex;
            justify-content: space-between;
            margin-top: 6px;
            font-size: 11px;
            color: var(--text-secondary);
        }

        .budget-value {
            font-size: 28px;
            font-weight: 700;
            text-align: center;
            margin: 8px 0;
        }

        /* Artifacts */
        .artifact {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 10px;
            margin-bottom: 4px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.15s;
        }

        .artifact:hover {
            background: var(--vscode-list-hoverBackground, rgba(255,255,255,0.08));
        }

        .artifact-icon { opacity: 0.7; }
        .artifact-name { flex: 1; }
        .artifact-step { color: var(--text-secondary); font-size: 11px; }

        /* Idle State */
        .idle-state {
            text-align: center;
            padding: 60px 20px;
        }

        .idle-state .idle-icon {
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.3;
        }

        .idle-state h2 {
            font-size: 18px;
            margin-bottom: 8px;
            color: var(--text-primary);
            text-transform: none;
            letter-spacing: normal;
        }

        .idle-state p {
            color: var(--text-secondary);
            margin: 4px 0;
        }

        /* Timer */
        .timer {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 12px;
            text-align: center;
        }

        .btn {
            background: var(--accent-purple);
            color: white;
            border: none;
            padding: 6px 14px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
        }

        .btn:hover { opacity: 0.9; }
    </style>
</head>
<body>
    <div class="header">
        <h1>
            <span class="logo">⚡</span>
            Pipeline Dashboard
        </h1>
        <span id="status-badge" class="status-badge status-idle">Idle</span>
    </div>

    <div id="idle-state" class="idle-state">
        <div class="idle-icon">⚡</div>
        <h2>No Active Pipeline</h2>
        <p>Run a pipeline from the sidebar or command palette to see progress here.</p>
        <p style="margin-top:16px;">
            <button class="btn" onclick="vscode.postMessage({command:'refresh'})">Refresh</button>
        </p>
    </div>

    <div id="active-state" class="dashboard-grid" style="display:none;">
        <div>
            <div class="card">
                <h2 id="pipeline-name">Pipeline Steps</h2>
                <ul class="steps-list" id="steps-list"></ul>
            </div>

            <div class="card" style="margin-top:16px;">
                <h2>Artifacts</h2>
                <div id="artifacts-list">
                    <p style="color:var(--text-secondary);font-size:12px;">No artifacts yet.</p>
                </div>
            </div>
        </div>

        <div>
            <div class="card">
                <h2>Context Budget</h2>
                <div id="budget-value" class="budget-value">0%</div>
                <div class="budget-meter">
                    <div class="budget-bar-track">
                        <div id="budget-fill" class="budget-bar-fill budget-green" style="width:0%"></div>
                    </div>
                    <div class="budget-labels">
                        <span id="budget-used">0K</span>
                        <span id="budget-total">0K</span>
                    </div>
                </div>
            </div>

            <div class="card" style="margin-top:16px;">
                <h2>Run Info</h2>
                <div style="font-size:12px;">
                    <div style="margin-bottom:6px;"><strong>Pipeline:</strong> <span id="run-pipeline">—</span></div>
                    <div style="margin-bottom:6px;"><strong>Status:</strong> <span id="run-status">—</span></div>
                    <div style="margin-bottom:6px;"><strong>Progress:</strong> <span id="run-progress">—</span></div>
                    <div class="timer"><strong>Elapsed:</strong> <span id="run-elapsed">—</span></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        function formatTokens(n) {
            if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
            if (n >= 1000) return (n / 1000).toFixed(0) + 'K';
            return n.toString();
        }

        function formatTime(seconds) {
            if (seconds < 60) return seconds + 's';
            const m = Math.floor(seconds / 60);
            const s = seconds % 60;
            return m + 'm ' + s + 's';
        }

        function getStepIcon(status) {
            switch (status) {
                case 'complete': return '✓';
                case 'running': return '⟳';
                case 'failed': return '✗';
                case 'skipped': return '⏭';
                default: return '○';
            }
        }

        function update(run) {
            document.getElementById('idle-state').style.display = 'none';
            document.getElementById('active-state').style.display = 'grid';

            // Status badge
            const badge = document.getElementById('status-badge');
            badge.textContent = run.status.charAt(0).toUpperCase() + run.status.slice(1);
            badge.className = 'status-badge status-' + run.status;

            // Pipeline name
            document.getElementById('pipeline-name').textContent = run.pipeline + ' — Steps';

            // Steps
            const stepsList = document.getElementById('steps-list');
            stepsList.innerHTML = run.steps.map(function(step, i) {
                return '<li class="step step-' + step.status + '">' +
                    '<div class="step-number">' + (i + 1) + '</div>' +
                    '<div class="step-info">' +
                        '<div class="step-name">' + step.name + '</div>' +
                        '<div class="step-agent">' + step.agent + '</div>' +
                    '</div>' +
                    '<span class="step-status-icon">' + getStepIcon(step.status) + '</span>' +
                '</li>';
            }).join('');

            // Context budget
            var pct = run.context_budget.percentage;
            document.getElementById('budget-value').textContent = pct + '%';
            var fill = document.getElementById('budget-fill');
            fill.style.width = pct + '%';
            fill.className = 'budget-bar-fill ' +
                (pct >= 90 ? 'budget-red' : pct >= 75 ? 'budget-yellow' : 'budget-green');
            document.getElementById('budget-used').textContent = formatTokens(run.context_budget.used);
            document.getElementById('budget-total').textContent = formatTokens(run.context_budget.total);

            // Run info
            document.getElementById('run-pipeline').textContent = run.pipeline;
            document.getElementById('run-status').textContent = run.status;
            document.getElementById('run-progress').textContent = run.current_step + '/' + run.total_steps + ' steps';
            document.getElementById('run-elapsed').textContent = formatTime(run.elapsed_seconds);

            // Artifacts
            var artifactsEl = document.getElementById('artifacts-list');
            if (run.artifacts && run.artifacts.length > 0) {
                artifactsEl.innerHTML = run.artifacts.map(function(a) {
                    return '<div class="artifact" onclick="vscode.postMessage({command:\'openArtifact\',path:\'' +
                        a.path.replace(/\\\\/g, '\\\\\\\\').replace(/'/g, "\\\\'") + '\'})">' +
                        '<span class="artifact-icon">📄</span>' +
                        '<span class="artifact-name">' + a.name + '</span>' +
                        '<span class="artifact-step">' + a.step + '</span>' +
                    '</div>';
                }).join('');
            } else {
                artifactsEl.innerHTML = '<p style="color:var(--text-secondary);font-size:12px;">No artifacts yet.</p>';
            }
        }

        function showIdle() {
            document.getElementById('idle-state').style.display = 'block';
            document.getElementById('active-state').style.display = 'none';
            document.getElementById('status-badge').textContent = 'Idle';
            document.getElementById('status-badge').className = 'status-badge status-idle';
        }

        window.addEventListener('message', function(event) {
            var msg = event.data;
            if (msg.type === 'update') {
                update(msg.data);
            } else if (msg.type === 'idle') {
                showIdle();
            }
        });
    </script>
</body>
</html>`;
  }
}
