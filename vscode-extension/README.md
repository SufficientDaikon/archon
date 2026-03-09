# OMNISKILL — AI Agent Framework for VS Code

> **Browse skills, run pipelines, invoke agents, and monitor health — all from VS Code.**

![VS Code](https://img.shields.io/badge/VS%20Code-1.85%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

### 🔮 Skills Explorer

Browse and install from **49+ categorized AI skills** with visual installation status. Search across all skills and categories instantly.

### 🤖 Agents Panel

View all **8 AI agents** with role descriptions, capabilities, and click-to-view documentation. Invoke agents directly with parameter input.

### 🚀 Pipeline Dashboard

Run and monitor **5 multi-step pipelines** with real-time progress visualization, context budget tracking, and artifact links.

### 📦 Bundle Management

Install related skills as **cohesive bundles** (web-dev-kit, django-kit, sdd-kit, etc.) with visual installation tracking.

### 🩺 Health Report

Run the OMNISKILL Doctor for a visual health assessment with platform compatibility cards, score gauge, and issue recommendations.

### 📊 Status Bar

Always-visible pipeline status and context budget meter with color-coded warnings.

## Quick Start

1. **Install the OMNISKILL CLI**:

   ```bash
   pip install omniskill
   ```

2. **Install this extension** from the VS Code Marketplace

3. **Open the OMNISKILL sidebar** (⚡ icon in the Activity Bar)

4. **Browse skills** and click to install, or **run a pipeline** from the Pipelines panel

## Commands

| Command                          | Description                            |
| -------------------------------- | -------------------------------------- |
| `OMNISKILL: Initialize`          | Initialize OMNISKILL in your workspace |
| `OMNISKILL: Install Skill`       | Install an individual skill            |
| `OMNISKILL: Install Bundle`      | Install a skill bundle                 |
| `OMNISKILL: Uninstall Component` | Remove a skill or bundle               |
| `OMNISKILL: Run Pipeline`        | Execute a multi-step pipeline          |
| `OMNISKILL: Show Dashboard`      | Open the Pipeline Dashboard            |
| `OMNISKILL: Run Doctor`          | Run health diagnostics                 |
| `OMNISKILL: Validate Workspace`  | Validate workspace configuration       |
| `OMNISKILL: Search Skills`       | Search across all skills               |
| `OMNISKILL: Admin Dashboard`     | View framework statistics              |
| `OMNISKILL: Update`              | Check for and apply updates            |
| `OMNISKILL: Open Settings`       | Open extension settings                |
| `OMNISKILL: Show Context Budget` | View context budget usage              |

## Settings

| Setting                          | Default       | Description                                                                              |
| -------------------------------- | ------------- | ---------------------------------------------------------------------------------------- |
| `omniskill.cliPath`              | `"omniskill"` | Path to the OMNISKILL CLI executable                                                     |
| `omniskill.defaultPlatform`      | `"auto"`      | Default platform adapter (auto, claude-code, copilot-cli, cursor, windsurf, antigravity) |
| `omniskill.showStatusBar`        | `true`        | Show status bar items                                                                    |
| `omniskill.autoRefreshDashboard` | `true`        | Auto-refresh dashboard during pipeline runs                                              |
| `omniskill.contextBudgetWarning` | `75`          | Context budget warning threshold (%)                                                     |

## Supported Platforms

Works identically in:

- **VS Code** (1.85+)
- **Cursor**
- **Windsurf**

## Architecture

This extension is a **GUI wrapper** around the OMNISKILL CLI. It delegates all operations to the CLI via `omniskill <command> --json` subprocess calls, ensuring the extension stays in sync with the framework and never reimplements logic.

```
Extension ──spawn──→ omniskill <cmd> --json ──→ Parse JSON envelope ──→ Update UI
```

## Development

```bash
# Clone and setup
cd vscode-extension
npm install

# Build
npm run compile

# Watch mode
npm run watch

# Package VSIX
npm run package
```

## Requirements

- **VS Code** 1.85 or later
- **OMNISKILL CLI** (`pip install omniskill`)
- **Python** 3.10+ (for CLI)

## License

MIT — see [LICENSE](../LICENSE)
