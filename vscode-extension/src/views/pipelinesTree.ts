/**
 * Pipelines Panel Tree Data Provider
 *
 * FR-008: Show all 5 pipelines with expandable steps and status indicators
 *
 * Tree structure:
 *   Pipeline (e.g., "sdd-pipeline — Spec-Driven Development")
 *     └─ Step (e.g., "1. specify → spec-writer-agent")
 */

import * as vscode from "vscode";
import { listPipelines } from "../cli";
import type { Pipeline, PipelineStep } from "../types";

// ─── Tree Item Types ────────────────────────────────────────────────────────

type PipelineTreeItem = PipelineItem | StepItem;

class PipelineItem extends vscode.TreeItem {
  public readonly type = "pipeline" as const;

  constructor(public readonly pipeline: Pipeline) {
    super(pipeline.name, vscode.TreeItemCollapsibleState.Collapsed);

    this.description = pipeline.description;
    this.tooltip = new vscode.MarkdownString(
      `**${pipeline.name}** v${pipeline.version}\n\n` +
        `${pipeline.description}\n\n` +
        `**Steps:** ${pipeline.steps.length}\n` +
        `**Tags:** ${pipeline.tags.join(", ")}\n` +
        `**Trigger:** "${pipeline.trigger}"\n` +
        `**Resumable:** ${pipeline.resumable ? "Yes" : "No"}`,
    );

    this.iconPath = new vscode.ThemeIcon(
      "play-circle",
      new vscode.ThemeColor("charts.purple"),
    );
    this.contextValue = "pipeline";
  }
}

class StepItem extends vscode.TreeItem {
  public readonly type = "step" as const;

  constructor(
    public readonly step: PipelineStep,
    public readonly index: number,
    public readonly pipelineName: string,
  ) {
    super(`${index + 1}. ${step.name}`, vscode.TreeItemCollapsibleState.None);

    this.description = `→ ${step.agent}`;
    this.tooltip = new vscode.MarkdownString(
      `**Step ${index + 1}: ${step.name}**\n\n` +
        `**Agent:** ${step.agent}\n` +
        `**Input:** ${step.input}\n` +
        `**Output:** ${step.output}\n` +
        `**On Failure:** ${step.on_failure}` +
        (step.loop_target ? `\n**Loop Target:** ${step.loop_target}` : "") +
        (step.max_iterations
          ? `\n**Max Iterations:** ${step.max_iterations}`
          : ""),
    );

    // Status-based icons
    const statusIcons: Record<string, { icon: string; color: string }> = {
      pending: { icon: "circle-outline", color: "descriptionForeground" },
      running: { icon: "sync~spin", color: "charts.yellow" },
      complete: { icon: "check", color: "charts.green" },
      failed: { icon: "error", color: "charts.red" },
      skipped: { icon: "debug-step-over", color: "descriptionForeground" },
    };
    const st = statusIcons[step.status] || statusIcons.pending;
    this.iconPath = new vscode.ThemeIcon(
      st.icon,
      new vscode.ThemeColor(st.color),
    );

    this.contextValue = "pipeline-step";
  }
}

// ─── Tree Data Provider ─────────────────────────────────────────────────────

export class PipelinesTreeProvider implements vscode.TreeDataProvider<PipelineTreeItem> {
  private _onDidChangeTreeData = new vscode.EventEmitter<
    PipelineTreeItem | undefined | null
  >();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private pipelines: Pipeline[] = [];
  private loading = false;
  private loadError: string | null = null;

  refresh(): void {
    this.pipelines = [];
    this.loadError = null;
    this._onDidChangeTreeData.fire(undefined);
  }

  getTreeItem(element: PipelineTreeItem): vscode.TreeItem {
    return element;
  }

  async getChildren(element?: PipelineTreeItem): Promise<PipelineTreeItem[]> {
    // Step items have no children
    if (element instanceof StepItem) {
      return [];
    }

    // Children of a pipeline = its steps
    if (element instanceof PipelineItem) {
      return element.pipeline.steps.map(
        (step, i) => new StepItem(step, i, element.pipeline.name),
      );
    }

    // Root: fetch pipelines
    if (this.pipelines.length === 0 && !this.loading && !this.loadError) {
      await this.fetchPipelines();
    }

    if (this.loadError) {
      const errorItem = new vscode.TreeItem(this.loadError) as PipelineTreeItem;
      errorItem.iconPath = new vscode.ThemeIcon("warning");
      return [errorItem];
    }

    if (this.loading) {
      const loadingItem = new vscode.TreeItem(
        "Loading pipelines...",
      ) as PipelineTreeItem;
      loadingItem.iconPath = new vscode.ThemeIcon("loading~spin");
      return [loadingItem];
    }

    return this.pipelines
      .sort((a, b) => a.name.localeCompare(b.name))
      .map((p) => new PipelineItem(p));
  }

  private async fetchPipelines(): Promise<void> {
    this.loading = true;
    try {
      const response = await listPipelines();
      this.pipelines = response.data.pipelines || [];
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      this.loadError = msg.includes("not found")
        ? "Archon CLI not found"
        : `Failed to load pipelines: ${msg.substring(0, 80)}`;
    } finally {
      this.loading = false;
    }
  }

  getAllPipelines(): Pipeline[] {
    return this.pipelines;
  }
}
