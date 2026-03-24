/**
 * Status Bar Items
 *
 * FR-019: Pipeline status indicator (idle/running with step progress)
 * FR-020: Context budget meter with color coding (green/yellow/red)
 * FR-021: Clickable to open relevant dashboards
 */

import * as vscode from "vscode";

export class StatusBarManager {
  private _pipelineItem: vscode.StatusBarItem;
  private _budgetItem: vscode.StatusBarItem;
  private _disposed = false;

  constructor() {
    // Left item: Pipeline status
    this._pipelineItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Left,
      100,
    );
    this._pipelineItem.command = "archon.showDashboard";
    this._pipelineItem.tooltip = "Archon: Click to open Pipeline Dashboard";
    this.setPipelineIdle();

    // Right item: Context budget
    this._budgetItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      50,
    );
    this._budgetItem.command = "archon.showContextBudget";
    this._budgetItem.tooltip = "Archon: Context budget usage";
    this.setBudget(0, 0);

    // Show/hide based on settings
    this._updateVisibility();
  }

  /**
   * Set pipeline status to idle.
   */
  setPipelineIdle(): void {
    this._pipelineItem.text = "$(zap) Archon: Idle";
    this._pipelineItem.backgroundColor = undefined;
    this._pipelineItem.tooltip =
      "Archon: No active pipeline — Click to open Dashboard";
  }

  /**
   * Set pipeline status to running with step progress.
   */
  setPipelineRunning(
    pipelineName: string,
    currentStep: number,
    totalSteps: number,
  ): void {
    this._pipelineItem.text = `$(sync~spin) Archon: Running ${pipelineName} [${currentStep}/${totalSteps}]`;
    this._pipelineItem.backgroundColor = new vscode.ThemeColor(
      "statusBarItem.warningBackground",
    );
    this._pipelineItem.tooltip = `Archon: Pipeline "${pipelineName}" in progress — Step ${currentStep} of ${totalSteps}`;
  }

  /**
   * Set pipeline status to complete.
   */
  setPipelineComplete(pipelineName: string): void {
    this._pipelineItem.text = `$(check) Archon: ${pipelineName} Complete`;
    this._pipelineItem.backgroundColor = undefined;
    this._pipelineItem.tooltip = `Archon: Pipeline "${pipelineName}" completed successfully`;

    // Reset to idle after 10 seconds
    setTimeout(() => {
      if (!this._disposed) {
        this.setPipelineIdle();
      }
    }, 10_000);
  }

  /**
   * Set pipeline status to failed.
   */
  setPipelineFailed(pipelineName: string, step: string): void {
    this._pipelineItem.text = `$(error) Archon: ${pipelineName} Failed at ${step}`;
    this._pipelineItem.backgroundColor = new vscode.ThemeColor(
      "statusBarItem.errorBackground",
    );
    this._pipelineItem.tooltip = `Archon: Pipeline "${pipelineName}" failed at step "${step}" — Click for details`;
  }

  /**
   * Update context budget display.
   */
  setBudget(usedTokens: number, totalTokens: number): void {
    if (totalTokens <= 0) {
      this._budgetItem.text = "$(brain) — / —";
      this._budgetItem.backgroundColor = undefined;
      this._budgetItem.tooltip = "Archon: No context budget data";
      return;
    }

    const percentage = Math.round((usedTokens / totalTokens) * 100);
    const usedStr = this._formatTokens(usedTokens);
    const totalStr = this._formatTokens(totalTokens);

    this._budgetItem.text = `$(brain) ${usedStr}/${totalStr} tokens`;
    this._budgetItem.tooltip = `Archon: Context budget ${percentage}% used (${usedStr} of ${totalStr})`;

    // Color coding per spec
    const config = vscode.workspace.getConfiguration("archon");
    const warningThreshold = config.get<number>("contextBudgetWarning", 75);

    if (percentage >= 90) {
      this._budgetItem.backgroundColor = new vscode.ThemeColor(
        "statusBarItem.errorBackground",
      );
    } else if (percentage >= warningThreshold) {
      this._budgetItem.backgroundColor = new vscode.ThemeColor(
        "statusBarItem.warningBackground",
      );
    } else {
      this._budgetItem.backgroundColor = undefined;
    }
  }

  /**
   * Show status bar items.
   */
  show(): void {
    this._pipelineItem.show();
    this._budgetItem.show();
  }

  /**
   * Hide status bar items.
   */
  hide(): void {
    this._pipelineItem.hide();
    this._budgetItem.hide();
  }

  /**
   * Update visibility based on settings (FR-022: showStatusBar).
   */
  updateFromSettings(): void {
    this._updateVisibility();
  }

  /**
   * Dispose all status bar items.
   */
  dispose(): void {
    this._disposed = true;
    this._pipelineItem.dispose();
    this._budgetItem.dispose();
  }

  private _updateVisibility(): void {
    const config = vscode.workspace.getConfiguration("archon");
    const show = config.get<boolean>("showStatusBar", true);

    if (show) {
      this.show();
    } else {
      this.hide();
    }
  }

  private _formatTokens(n: number): string {
    if (n >= 1_000_000) {
      return (n / 1_000_000).toFixed(1) + "M";
    }
    if (n >= 1_000) {
      return Math.round(n / 1_000) + "K";
    }
    return n.toString();
  }
}
