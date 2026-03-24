/**
 * Synapse Detail Webview Panel
 *
 * FR-053: Clicking a synapse shows a detail webview with full information
 * FR-054: Follows the same pattern as skillDetailPanel.ts
 */

import * as vscode from "vscode";
import type { Synapse } from "../types";

export class SynapseDetailPanel {
  private static readonly viewType = "archon.synapseDetail";
  private static panels = new Map<string, SynapseDetailPanel>();

  private readonly _panel: vscode.WebviewPanel;
  private _disposables: vscode.Disposable[] = [];

  private constructor(
    panel: vscode.WebviewPanel,
    private readonly synapse: Synapse,
  ) {
    this._panel = panel;
    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
  }

  public static async show(synapse: Synapse): Promise<void> {
    // Reuse existing panel for same synapse
    const existing = SynapseDetailPanel.panels.get(synapse.name);
    if (existing) {
      existing._panel.reveal(vscode.ViewColumn.One);
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      SynapseDetailPanel.viewType,
      `Synapse: ${synapse.name}`,
      vscode.ViewColumn.One,
      { enableScripts: false },
    );

    const instance = new SynapseDetailPanel(panel, synapse);
    SynapseDetailPanel.panels.set(synapse.name, instance);

    panel.webview.html = instance._getHtml();
  }

  public dispose(): void {
    SynapseDetailPanel.panels.delete(this.synapse.name);
    this._panel.dispose();
    for (const d of this._disposables) {
      d.dispose();
    }
    this._disposables = [];
  }

  private _getHtml(): string {
    const syn = this.synapse;
    const typeBadge =
      syn.synapse_type === "core"
        ? '<span class="badge core">🧠 core</span>'
        : '<span class="badge optional">⚡ optional</span>';

    const phasesHtml = syn.firing_phases
      .map(
        (p) => `
        <div class="phase-card">
          <div class="phase-header">
            <span class="phase-name">${this._esc(p.name)}</span>
            <span class="phase-timing">${this._esc(p.timing)}</span>
          </div>
          <p class="phase-desc">${this._esc(p.description)}</p>
        </div>`,
      )
      .join("\n");

    const tagsHtml = syn.tags
      .map((t) => `<span class="tag">${this._esc(t)}</span>`)
      .join("");

    return /*html*/ `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Synapse: ${this._esc(syn.name)}</title>
    <style>
        body {
            font-family: var(--vscode-font-family, 'Segoe UI', sans-serif);
            background: var(--vscode-editor-background, #1a1a2e);
            color: var(--vscode-editor-foreground, #e0e0e0);
            margin: 0;
            padding: 24px;
            line-height: 1.6;
        }
        .synapse-header {
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--vscode-panel-border, #2a3a5e);
        }
        .synapse-header h1 {
            margin: 0 0 4px 0;
            font-size: 22px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .badge {
            font-size: 12px;
            padding: 2px 8px;
            border-radius: 10px;
            font-weight: 600;
        }
        .badge.core { background: rgba(147, 51, 234, 0.2); color: #a78bfa; }
        .badge.optional { background: rgba(234, 179, 8, 0.2); color: #fbbf24; }
        .synapse-header .version {
            font-size: 12px;
            padding: 2px 8px;
            background: rgba(108, 63, 232, 0.2);
            color: #a78bfa;
            border-radius: 10px;
            font-weight: 600;
        }
        .synapse-header .description {
            color: var(--vscode-descriptionForeground, #a0a0b0);
            font-size: 14px;
            margin-top: 6px;
        }
        .meta-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin-bottom: 24px;
        }
        .meta-card {
            background: var(--vscode-sideBar-background, #1e2a4a);
            border: 1px solid var(--vscode-panel-border, #2a3a5e);
            border-radius: 8px;
            padding: 12px;
        }
        .meta-card h3 {
            margin: 0 0 6px 0;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--vscode-descriptionForeground, #a0a0b0);
        }
        .tag {
            display: inline-block;
            padding: 2px 8px;
            margin: 2px;
            background: rgba(147, 51, 234, 0.15);
            color: #a78bfa;
            border-radius: 4px;
            font-size: 11px;
        }
        h2 {
            font-size: 16px;
            margin: 24px 0 12px 0;
            padding-bottom: 6px;
            border-bottom: 1px solid var(--vscode-panel-border, #2a3a5e);
        }
        .phase-card {
            background: var(--vscode-sideBar-background, #1e2a4a);
            border: 1px solid var(--vscode-panel-border, #2a3a5e);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
        }
        .phase-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 4px;
        }
        .phase-name {
            font-weight: 700;
            font-size: 14px;
        }
        .phase-timing {
            font-size: 11px;
            padding: 2px 6px;
            background: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
            border-radius: 4px;
        }
        .phase-desc {
            margin: 0;
            font-size: 13px;
            color: var(--vscode-descriptionForeground, #a0a0b0);
        }
    </style>
</head>
<body>
    <div class="synapse-header">
        <h1>
            🧠 ${this._esc(syn.name)}
            <span class="version">v${this._esc(syn.version)}</span>
            ${typeBadge}
        </h1>
        <p class="description">${this._esc(syn.description)}</p>
    </div>

    <div class="meta-grid">
        <div class="meta-card">
            <h3>Tags</h3>
            <div>${tagsHtml || "<em>None</em>"}</div>
        </div>
        <div class="meta-card">
            <h3>Synapse Type</h3>
            <div>${this._esc(syn.synapse_type)}</div>
        </div>
        <div class="meta-card">
            <h3>Phases</h3>
            <div>${syn.firing_phases.length} firing phase(s)</div>
        </div>
    </div>

    <h2>Firing Phases</h2>
    ${phasesHtml}
</body>
</html>`;
  }

  private _esc(text: string): string {
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
}
