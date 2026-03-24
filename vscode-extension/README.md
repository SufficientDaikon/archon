# Archon — AI Agent Framework for VS Code

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

Run the Archon Doctor for a visual health assessment with platform compatibility cards, score gauge, and issue recommendations.

### 📊 Status Bar

Always-visible pipeline status and context budget meter with color-coded warnings.

## Quick Start

1. **Install the Archon CLI**:

   ```bash
   pip install archon
   ```

2. **Install this extension** from the VS Code Marketplace

3. **Open the Archon sidebar** (⚡ icon in the Activity Bar)

4. **Browse skills** and click to install, or **run a pipeline** from the Pipelines panel

## Commands

| Command                          | Description                            |
| -------------------------------- | -------------------------------------- |
| `Archon: Initialize`          | Initialize Archon in your workspace |
| `Archon: Install Skill`       | Install an individual skill            |
| `Archon: Install Bundle`      | Install a skill bundle                 |
| `Archon: Uninstall Component` | Remove a skill or bundle               |
| `Archon: Run Pipeline`        | Execute a multi-step pipeline          |
| `Archon: Show Dashboard`      | Open the Pipeline Dashboard            |
| `Archon: Run Doctor`          | Run health diagnostics                 |
| `Archon: Validate Workspace`  | Validate workspace configuration       |
| `Archon: Search Skills`       | Search across all skills               |
| `Archon: Admin Dashboard`     | View framework statistics              |
| `Archon: Update`              | Check for and apply updates            |
| `Archon: Open Settings`       | Open extension settings                |
| `Archon: Show Context Budget` | View context budget usage              |

## Settings

| Setting                          | Default       | Description                                                                              |
| -------------------------------- | ------------- | ---------------------------------------------------------------------------------------- |
| `archon.cliPath`              | `"archon"` | Path to the Archon CLI executable                                                     |
| `archon.defaultPlatform`      | `"auto"`      | Default platform adapter (auto, claude-code, copilot-cli, cursor, windsurf, antigravity) |
| `archon.showStatusBar`        | `true`        | Show status bar items                                                                    |
| `archon.autoRefreshDashboard` | `true`        | Auto-refresh dashboard during pipeline runs                                              |
| `archon.contextBudgetWarning` | `75`          | Context budget warning threshold (%)                                                     |

## Supported Platforms

Works identically in:

- **VS Code** (1.85+)
- **Cursor**
- **Windsurf**

## Architecture

This extension is a **GUI wrapper** around the Archon CLI. It delegates all operations to the CLI via `archon <command> --json` subprocess calls, ensuring the extension stays in sync with the framework and never reimplements logic.

```
Extension ──spawn──→ archon <cmd> --json ──→ Parse JSON envelope ──→ Update UI
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
- **Archon CLI** (`pip install archon`)
- **Python** 3.10+ (for CLI)

## License

MIT — see [LICENSE](../LICENSE)
