/**
 * Archon VS Code Extension — Entry Point
 *
 * Activation: onStartupFinished
 * NFR-001: Activation time under 500ms
 *
 * Wires together:
 *   - CLI availability check (FR-004)
 *   - 4 sidebar tree views (FR-005 to FR-009)
 *   - 3 webview panels (FR-010 to FR-014)
 *   - Status bar items (FR-019 to FR-021)
 *   - 13+ commands (FR-017, FR-018)
 *   - Settings listener (FR-022 to FR-024)
 */

import * as vscode from "vscode";
import { checkCliAvailable, showInstallPrompt, resetCliCache } from "./cli";
import { SkillsTreeProvider } from "./views/skillsTree";
import { AgentsTreeProvider } from "./views/agentsTree";
import { PipelinesTreeProvider } from "./views/pipelinesTree";
import { BundlesTreeProvider } from "./views/bundlesTree";
import { SynapsesTreeProvider } from "./views/synapsesTree";
import { StatusBarManager } from "./statusBar";
import { registerCommands } from "./commands";

/**
 * Extension activation.
 */
export async function activate(
  context: vscode.ExtensionContext,
): Promise<void> {
  // ─── Output Channel ─────────────────────────────────────────────────
  const output = vscode.window.createOutputChannel("Archon");
  context.subscriptions.push(output);
  output.appendLine(`Archon extension activating...`);

  // ─── Tree View Providers ────────────────────────────────────────────
  const skillsTree = new SkillsTreeProvider();
  const agentsTree = new AgentsTreeProvider();
  const pipelinesTree = new PipelinesTreeProvider();
  const bundlesTree = new BundlesTreeProvider();
  const synapsesTree = new SynapsesTreeProvider();

  context.subscriptions.push(
    vscode.window.registerTreeDataProvider("archon-skills", skillsTree),
    vscode.window.registerTreeDataProvider("archon-agents", agentsTree),
    vscode.window.registerTreeDataProvider(
      "archon-pipelines",
      pipelinesTree,
    ),
    vscode.window.registerTreeDataProvider("archon-bundles", bundlesTree),
    vscode.window.registerTreeDataProvider("archon-synapses", synapsesTree),
  );

  // ─── Status Bar ─────────────────────────────────────────────────────
  const statusBar = new StatusBarManager();
  context.subscriptions.push({ dispose: () => statusBar.dispose() });

  // ─── Register All Commands ──────────────────────────────────────────
  registerCommands(
    context,
    skillsTree,
    agentsTree,
    pipelinesTree,
    bundlesTree,
    synapsesTree,
    statusBar,
  );

  // ─── Settings Change Listener (FR-023: immediate effect) ────────────
  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration("archon.showStatusBar")) {
        statusBar.updateFromSettings();
      }
      if (e.affectsConfiguration("archon.cliPath")) {
        resetCliCache();
        // Refresh all trees with new CLI path
        skillsTree.refresh();
        agentsTree.refresh();
        pipelinesTree.refresh();
        bundlesTree.refresh();
        synapsesTree.refresh();
        output.appendLine("CLI path changed — refreshing all views.");
      }
      if (e.affectsConfiguration("archon.contextBudgetWarning")) {
        // Budget display will update on next setBudget call
        output.appendLine("Context budget warning threshold updated.");
      }
    }),
  );

  // ─── CLI Availability Check (FR-004) ────────────────────────────────
  // Non-blocking check — don't slow down activation
  checkCliAvailable()
    .then((available) => {
      if (available) {
        output.appendLine("Archon CLI detected — extension ready.");
      } else {
        output.appendLine(
          "Archon CLI not found — will prompt on first use.",
        );
        // Show a subtle notification (not modal)
        vscode.window
          .showWarningMessage(
            "Archon CLI not found. Some features require the CLI.",
            "Install",
            "Set Path",
          )
          .then((choice) => {
            if (choice === "Install") {
              const terminal =
                vscode.window.createTerminal("Archon Install");
              terminal.sendText("pip install archon");
              terminal.show();
            } else if (choice === "Set Path") {
              vscode.commands.executeCommand(
                "workbench.action.openSettings",
                "archon.cliPath",
              );
            }
          });
      }
    })
    .catch(() => {
      output.appendLine("CLI check failed — will retry on first use.");
    });

  output.appendLine("Archon extension activated successfully.");
}

/**
 * Extension deactivation.
 */
export function deactivate(): void {
  // Cleanup is handled by disposables registered in context.subscriptions
}
