/**
 * Health Report Webview Panel
 *
 * FR-014: Visualize doctor command results with platform health cards and overall score
 *
 * Shows:
 *   - Circular gauge with overall health score
 *   - Platform cards with green/yellow/red status
 *   - Specific issues with suggested fixes
 */

import * as vscode from "vscode";
import type { DoctorData } from "../types";
import { runDoctor } from "../cli";

export class HealthPanel {
  public static currentPanel: HealthPanel | undefined;
  private static readonly viewType = "omniskill.health";

  private readonly _panel: vscode.WebviewPanel;
  private _disposables: vscode.Disposable[] = [];

  private constructor(panel: vscode.WebviewPanel) {
    this._panel = panel;
    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
  }

  public static async show(): Promise<void> {
    if (HealthPanel.currentPanel) {
      HealthPanel.currentPanel._panel.reveal(vscode.ViewColumn.One);
      HealthPanel.currentPanel._loadData();
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      HealthPanel.viewType,
      "OMNISKILL — Health Report",
      vscode.ViewColumn.One,
      { enableScripts: true },
    );

    HealthPanel.currentPanel = new HealthPanel(panel);
    await HealthPanel.currentPanel._loadData();
  }

  private async _loadData(): Promise<void> {
    // Show loading state
    this._panel.webview.html = this._getLoadingHtml();

    try {
      const response = await runDoctor();
      this._panel.webview.html = this._getHtml(response.data);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      this._panel.webview.html = this._getErrorHtml(msg);
    }
  }

  public dispose(): void {
    HealthPanel.currentPanel = undefined;
    this._panel.dispose();
    for (const d of this._disposables) {
      d.dispose();
    }
    this._disposables = [];
  }

  private _getLoadingHtml(): string {
    return /*html*/ `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: var(--vscode-font-family, 'Segoe UI', sans-serif);
            background: var(--vscode-editor-background, #1a1a2e);
            color: var(--vscode-editor-foreground, #e0e0e0);
            display: flex; align-items: center; justify-content: center;
            min-height: 100vh; margin: 0;
        }
        .loading { text-align: center; }
        .spinner { font-size: 32px; animation: spin 1s linear infinite; display: inline-block; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="loading">
        <div class="spinner">⟳</div>
        <p>Running OMNISKILL Doctor...</p>
    </div>
</body>
</html>`;
  }

  private _getErrorHtml(error: string): string {
    return /*html*/ `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: var(--vscode-font-family, 'Segoe UI', sans-serif);
            background: var(--vscode-editor-background, #1a1a2e);
            color: var(--vscode-editor-foreground, #e0e0e0);
            display: flex; align-items: center; justify-content: center;
            min-height: 100vh; margin: 0;
        }
        .error { text-align: center; max-width: 500px; }
        .error-icon { font-size: 48px; margin-bottom: 16px; }
        .error-msg { color: #ef4444; background: rgba(239,68,68,0.1); padding: 12px; border-radius: 8px; font-size: 13px; }
    </style>
</head>
<body>
    <div class="error">
        <div class="error-icon">⚠️</div>
        <h2>Health Check Failed</h2>
        <div class="error-msg">${this._esc(error)}</div>
        <p style="color:#a0a0b0;font-size:13px;margin-top:16px;">
            Ensure the OMNISKILL CLI is installed and accessible.
        </p>
    </div>
</body>
</html>`;
  }

  private _getHtml(data: DoctorData): string {
    const score = data.overall_score;
    const scoreColor =
      score >= 80 ? "#22c55e" : score >= 50 ? "#eab308" : "#ef4444";
    const scoreLabel =
      score >= 80 ? "Healthy" : score >= 50 ? "Degraded" : "Unhealthy";

    // Build platform cards
    const platformCards = data.platforms
      .map((p) => {
        const statusColor =
          p.status === "healthy"
            ? "#22c55e"
            : p.status === "degraded"
              ? "#eab308"
              : p.status === "error"
                ? "#ef4444"
                : "#6b7280";
        const statusIcon =
          p.status === "healthy"
            ? "✓"
            : p.status === "degraded"
              ? "⚠"
              : p.status === "error"
                ? "✗"
                : "—";

        const checksHtml = p.checks
          .map((c) => {
            const chkColor =
              c.status === "pass"
                ? "#22c55e"
                : c.status === "warn"
                  ? "#eab308"
                  : "#ef4444";
            const chkIcon =
              c.status === "pass" ? "✓" : c.status === "warn" ? "⚠" : "✗";
            return `<div class="check-item">
                    <span style="color:${chkColor}">${chkIcon}</span>
                    <span>${this._esc(c.name)}: ${this._esc(c.message)}</span>
                    ${c.suggestion ? `<div class="suggestion">${this._esc(c.suggestion)}</div>` : ""}
                </div>`;
          })
          .join("");

        return `<div class="platform-card">
                <div class="platform-header">
                    <span class="platform-name">${this._esc(p.name)}</span>
                    <span class="platform-status" style="color:${statusColor}">${statusIcon} ${this._esc(p.status)}</span>
                </div>
                <div class="platform-msg">${this._esc(p.message)}</div>
                ${checksHtml ? `<div class="checks">${checksHtml}</div>` : ""}
            </div>`;
      })
      .join("");

    // Build issues list
    const issuesHtml =
      data.issues.length > 0
        ? data.issues
            .map((i) => {
              const color = i.status === "fail" ? "#ef4444" : "#eab308";
              const icon = i.status === "fail" ? "✗" : "⚠";
              return `<div class="issue">
                    <span style="color:${color};font-weight:bold;">${icon}</span>
                    <div>
                        <strong>${this._esc(i.name)}</strong>: ${this._esc(i.message)}
                        ${i.suggestion ? `<div class="suggestion">${this._esc(i.suggestion)}</div>` : ""}
                    </div>
                </div>`;
            })
            .join("")
        : '<p style="color:#22c55e;">No issues found — everything looks great!</p>';

    return /*html*/ `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OMNISKILL Health Report</title>
    <style>
        body {
            font-family: var(--vscode-font-family, 'Segoe UI', sans-serif);
            background: var(--vscode-editor-background, #1a1a2e);
            color: var(--vscode-editor-foreground, #e0e0e0);
            margin: 0;
            padding: 24px;
            line-height: 1.5;
        }

        .header {
            display: flex;
            align-items: center;
            gap: 24px;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--vscode-panel-border, #2a3a5e);
        }

        /* Score Gauge */
        .gauge-container {
            position: relative;
            width: 120px;
            height: 120px;
            flex-shrink: 0;
        }

        .gauge-svg {
            transform: rotate(-90deg);
        }

        .gauge-bg {
            fill: none;
            stroke: rgba(255,255,255,0.08);
            stroke-width: 10;
        }

        .gauge-fill {
            fill: none;
            stroke: ${scoreColor};
            stroke-width: 10;
            stroke-linecap: round;
            stroke-dasharray: ${(score / 100) * 314} 314;
            transition: stroke-dasharray 1s ease;
        }

        .gauge-label {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }

        .gauge-score {
            font-size: 28px;
            font-weight: 700;
            color: ${scoreColor};
        }

        .gauge-text {
            font-size: 11px;
            color: var(--vscode-descriptionForeground, #a0a0b0);
        }

        .header-info h1 {
            margin: 0 0 4px 0;
            font-size: 20px;
        }

        .header-info .meta {
            font-size: 12px;
            color: var(--vscode-descriptionForeground, #a0a0b0);
        }

        .header-info .meta span { margin-right: 16px; }

        .stats-row {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }

        .stat {
            background: var(--vscode-sideBar-background, #1e2a4a);
            border: 1px solid var(--vscode-panel-border, #2a3a5e);
            border-radius: 8px;
            padding: 12px 16px;
            flex: 1;
            min-width: 100px;
            text-align: center;
        }

        .stat-value { font-size: 22px; font-weight: 700; }
        .stat-label { font-size: 11px; color: var(--vscode-descriptionForeground, #a0a0b0); text-transform: uppercase; }

        .section-title {
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--vscode-descriptionForeground, #a0a0b0);
            margin: 24px 0 12px 0;
        }

        .platform-card {
            background: var(--vscode-sideBar-background, #1e2a4a);
            border: 1px solid var(--vscode-panel-border, #2a3a5e);
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 8px;
        }

        .platform-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
        }

        .platform-name { font-weight: 600; font-size: 14px; }
        .platform-status { font-size: 12px; font-weight: 600; text-transform: uppercase; }
        .platform-msg { font-size: 12px; color: var(--vscode-descriptionForeground, #a0a0b0); }

        .checks { margin-top: 8px; }

        .check-item {
            display: flex;
            gap: 8px;
            align-items: flex-start;
            font-size: 12px;
            padding: 3px 0;
        }

        .issue {
            display: flex;
            gap: 10px;
            align-items: flex-start;
            padding: 8px 12px;
            margin-bottom: 4px;
            background: var(--vscode-sideBar-background, #1e2a4a);
            border: 1px solid var(--vscode-panel-border, #2a3a5e);
            border-radius: 6px;
            font-size: 13px;
        }

        .suggestion {
            font-size: 11px;
            color: #60a5fa;
            margin-top: 2px;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="gauge-container">
            <svg class="gauge-svg" viewBox="0 0 120 120" width="120" height="120">
                <circle class="gauge-bg" cx="60" cy="60" r="50" />
                <circle class="gauge-fill" cx="60" cy="60" r="50" />
            </svg>
            <div class="gauge-label">
                <div class="gauge-score">${score}</div>
                <div class="gauge-text">${scoreLabel}</div>
            </div>
        </div>
        <div class="header-info">
            <h1>⚡ OMNISKILL Health Report</h1>
            <div class="meta">
                <span>CLI v${this._esc(data.cli_version)}</span>
                <span>Python ${this._esc(data.python_version)}</span>
            </div>
        </div>
    </div>

    <div class="stats-row">
        <div class="stat">
            <div class="stat-value">${data.skills_count}</div>
            <div class="stat-label">Skills</div>
        </div>
        <div class="stat">
            <div class="stat-value">${data.installed_count}</div>
            <div class="stat-label">Installed</div>
        </div>
        <div class="stat">
            <div class="stat-value">${data.agents_count}</div>
            <div class="stat-label">Agents</div>
        </div>
        <div class="stat">
            <div class="stat-value">${data.pipelines_count}</div>
            <div class="stat-label">Pipelines</div>
        </div>
        <div class="stat">
            <div class="stat-value">${data.platforms.length}</div>
            <div class="stat-label">Platforms</div>
        </div>
    </div>

    <div class="section-title">Platform Health</div>
    ${platformCards}

    <div class="section-title">Issues & Recommendations</div>
    ${issuesHtml}
</body>
</html>`;
  }

  private _esc(s: string): string {
    return s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
}
