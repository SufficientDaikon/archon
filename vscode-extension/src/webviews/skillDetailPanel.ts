/**
 * Skill Detail Webview Panel
 *
 * FR-013: Render SKILL.md documentation with proper markdown formatting + metadata
 */

import * as vscode from "vscode";
import type { Skill, SkillDetailData } from "../types";
import { getSkillInfo } from "../cli";

export class SkillDetailPanel {
  private static readonly viewType = "archon.skillDetail";
  private static panels = new Map<string, SkillDetailPanel>();

  private readonly _panel: vscode.WebviewPanel;
  private _disposables: vscode.Disposable[] = [];

  private constructor(
    panel: vscode.WebviewPanel,
    private readonly skill: Skill,
  ) {
    this._panel = panel;
    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
  }

  public static async show(skill: Skill): Promise<void> {
    // Reuse existing panel for same skill
    const existing = SkillDetailPanel.panels.get(skill.name);
    if (existing) {
      existing._panel.reveal(vscode.ViewColumn.One);
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      SkillDetailPanel.viewType,
      `Skill: ${skill.name}`,
      vscode.ViewColumn.One,
      { enableScripts: false },
    );

    const instance = new SkillDetailPanel(panel, skill);
    SkillDetailPanel.panels.set(skill.name, instance);

    // Try to load detailed data from CLI
    let documentation = "";
    let triggers: string[] = [];
    let dependencies: string[] = [];

    try {
      const detail = await getSkillInfo(skill.name);
      documentation = detail.data.documentation || "";
      triggers = detail.data.triggers || [];
      dependencies = detail.data.dependencies || [];
    } catch {
      documentation = `*Could not load documentation for ${skill.name}. The Archon CLI may not be available.*`;
    }

    panel.webview.html = instance._getHtml(
      documentation,
      triggers,
      dependencies,
    );
  }

  public dispose(): void {
    SkillDetailPanel.panels.delete(this.skill.name);
    this._panel.dispose();
    for (const d of this._disposables) {
      d.dispose();
    }
    this._disposables = [];
  }

  private _getHtml(
    documentation: string,
    triggers: string[],
    dependencies: string[],
  ): string {
    const skill = this.skill;

    // Convert markdown-like content to basic HTML
    const docHtml = this._renderMarkdown(documentation);

    return /*html*/ `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Skill: ${this._esc(skill.name)}</title>
    <style>
        body {
            font-family: var(--vscode-font-family, 'Segoe UI', sans-serif);
            background: var(--vscode-editor-background, #1a1a2e);
            color: var(--vscode-editor-foreground, #e0e0e0);
            margin: 0;
            padding: 24px;
            line-height: 1.6;
        }

        .skill-header {
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--vscode-panel-border, #2a3a5e);
        }

        .skill-header h1 {
            margin: 0 0 4px 0;
            font-size: 22px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .skill-header .version {
            font-size: 12px;
            padding: 2px 8px;
            background: rgba(108, 63, 232, 0.2);
            color: #a78bfa;
            border-radius: 10px;
            font-weight: 600;
        }

        .skill-header .status {
            font-size: 12px;
            padding: 2px 8px;
            border-radius: 10px;
            font-weight: 600;
        }

        .installed { background: rgba(34,197,94,0.15); color: #22c55e; }
        .not-installed { background: rgba(160,160,176,0.15); color: #a0a0b0; }

        .skill-header .description {
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

        .meta-card .value {
            font-size: 13px;
        }

        .tag {
            display: inline-block;
            padding: 2px 8px;
            margin: 2px;
            background: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
            border-radius: 4px;
            font-size: 11px;
        }

        .doc-content {
            background: var(--vscode-sideBar-background, #1e2a4a);
            border: 1px solid var(--vscode-panel-border, #2a3a5e);
            border-radius: 8px;
            padding: 20px;
        }

        .doc-content h1, .doc-content h2, .doc-content h3 {
            margin-top: 20px;
            margin-bottom: 8px;
        }

        .doc-content h1 { font-size: 20px; }
        .doc-content h2 { font-size: 16px; }
        .doc-content h3 { font-size: 14px; }

        .doc-content p { margin: 8px 0; }

        .doc-content code {
            background: rgba(255,255,255,0.08);
            padding: 1px 6px;
            border-radius: 3px;
            font-size: 12px;
        }

        .doc-content pre {
            background: rgba(0,0,0,0.3);
            padding: 12px;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 12px;
        }

        .doc-content ul, .doc-content ol {
            padding-left: 24px;
        }

        .doc-content li {
            margin: 4px 0;
        }
    </style>
</head>
<body>
    <div class="skill-header">
        <h1>
            ⚡ ${this._esc(skill.name)}
            <span class="version">v${this._esc(skill.version)}</span>
            <span class="status ${skill.installed ? "installed" : "not-installed"}">
                ${skill.installed ? "✓ Installed" : "Not Installed"}
            </span>
        </h1>
        <div class="description">${this._esc(skill.description)}</div>
    </div>

    <div class="meta-grid">
        <div class="meta-card">
            <h3>Category</h3>
            <div class="value">${this._esc(skill.category)}</div>
        </div>
        <div class="meta-card">
            <h3>Priority</h3>
            <div class="value">${this._esc(skill.priority)}</div>
        </div>
        <div class="meta-card">
            <h3>Platforms</h3>
            <div class="value">${skill.platforms.map((p) => `<span class="tag">${this._esc(p)}</span>`).join(" ")}</div>
        </div>
        <div class="meta-card">
            <h3>Tags</h3>
            <div class="value">${skill.tags.map((t) => `<span class="tag">${this._esc(t)}</span>`).join(" ")}</div>
        </div>
        ${
          triggers.length > 0
            ? `
        <div class="meta-card">
            <h3>Triggers</h3>
            <div class="value">${triggers.map((t) => `<span class="tag">${this._esc(t)}</span>`).join(" ")}</div>
        </div>
        `
            : ""
        }
        ${
          dependencies.length > 0
            ? `
        <div class="meta-card">
            <h3>Dependencies</h3>
            <div class="value">${dependencies.map((d) => `<span class="tag">${this._esc(d)}</span>`).join(" ")}</div>
        </div>
        `
            : ""
        }
    </div>

    <div class="doc-content">
        ${docHtml || '<p style="color: var(--vscode-descriptionForeground);">No documentation available.</p>'}
    </div>
</body>
</html>`;
  }

  /** Simple Markdown → HTML conversion (no external deps) */
  private _renderMarkdown(md: string): string {
    if (!md) {
      return "";
    }

    let html = this._esc(md);

    // Code blocks (```...```)
    html = html.replace(
      /```(\w*)\n([\s\S]*?)```/g,
      (_m, _lang, code) => `<pre><code>${code}</code></pre>`,
    );

    // Inline code
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Headers
    html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
    html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
    html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");

    // Bold and italic
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

    // Unordered lists
    html = html.replace(/^- (.+)$/gm, "<li>$1</li>");
    html = html.replace(/(<li>[\s\S]*?<\/li>)/g, "<ul>$1</ul>");
    // Collapse consecutive <ul> tags
    html = html.replace(/<\/ul>\s*<ul>/g, "");

    // Paragraphs (double newlines)
    html = html.replace(/\n\n/g, "</p><p>");
    html = `<p>${html}</p>`;

    // Clean up empty tags
    html = html.replace(/<p>\s*<\/p>/g, "");
    html = html.replace(/<p>\s*(<h[123]>)/g, "$1");
    html = html.replace(/(<\/h[123]>)\s*<\/p>/g, "$1");
    html = html.replace(/<p>\s*(<ul>)/g, "$1");
    html = html.replace(/(<\/ul>)\s*<\/p>/g, "$1");
    html = html.replace(/<p>\s*(<pre>)/g, "$1");
    html = html.replace(/(<\/pre>)\s*<\/p>/g, "$1");

    return html;
  }

  private _esc(s: string): string {
    return s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
}
