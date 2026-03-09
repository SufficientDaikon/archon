/**
 * Agents Panel Tree Data Provider
 *
 * FR-007: Display all 8 agents with click-to-view documentation capability
 *
 * Tree structure: flat list of agents with role descriptions
 */

import * as vscode from "vscode";
import { listAgents } from "../cli";
import type { Agent } from "../types";

// ─── Tree Item ──────────────────────────────────────────────────────────────

class AgentItem extends vscode.TreeItem {
  constructor(public readonly agent: Agent) {
    super(agent.name, vscode.TreeItemCollapsibleState.None);

    this.description = agent.role;
    this.tooltip = new vscode.MarkdownString(
      `**${agent.name}**\n\n` +
        `**Role:** ${agent.role}\n\n` +
        `${agent.description}\n\n` +
        `**Phase:** ${agent.workflow_phase}\n` +
        `**Skills:** ${agent.skills.join(", ")}\n` +
        `**Capabilities:** ${agent.capabilities.join(", ")}` +
        (agent.handoff
          ? `\n\n**Handoff → ** ${agent.handoff.next_agent} (produces ${agent.handoff.artifact})`
          : ""),
    );

    // Phase-based icons
    const iconMap: Record<string, string> = {
      specification: "file-text",
      implementation: "code",
      review: "eye",
      debugging: "bug",
      research: "telescope",
      design: "paintcan",
      testing: "beaker",
      orchestration: "organization",
    };
    this.iconPath = new vscode.ThemeIcon(
      iconMap[agent.workflow_phase] || "robot",
      new vscode.ThemeColor("charts.blue"),
    );

    this.contextValue = "agent";

    // Click to view documentation
    this.command = {
      command: "omniskill.showAgentDetail",
      title: "Show Agent Documentation",
      arguments: [agent],
    };
  }
}

// ─── Tree Data Provider ─────────────────────────────────────────────────────

export class AgentsTreeProvider implements vscode.TreeDataProvider<AgentItem> {
  private _onDidChangeTreeData = new vscode.EventEmitter<
    AgentItem | undefined | null
  >();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private agents: Agent[] = [];
  private loading = false;
  private loadError: string | null = null;

  refresh(): void {
    this.agents = [];
    this.loadError = null;
    this._onDidChangeTreeData.fire(undefined);
  }

  getTreeItem(element: AgentItem): vscode.TreeItem {
    return element;
  }

  async getChildren(element?: AgentItem): Promise<AgentItem[]> {
    // Agents are flat — no children
    if (element) {
      return [];
    }

    // Root: fetch agents
    if (this.agents.length === 0 && !this.loading && !this.loadError) {
      await this.fetchAgents();
    }

    if (this.loadError) {
      const errorItem = new vscode.TreeItem(this.loadError) as AgentItem;
      errorItem.iconPath = new vscode.ThemeIcon("warning");
      return [errorItem];
    }

    if (this.loading) {
      const loadingItem = new vscode.TreeItem("Loading agents...") as AgentItem;
      loadingItem.iconPath = new vscode.ThemeIcon("loading~spin");
      return [loadingItem];
    }

    return this.agents
      .sort((a, b) => a.name.localeCompare(b.name))
      .map((a) => new AgentItem(a));
  }

  private async fetchAgents(): Promise<void> {
    this.loading = true;
    try {
      const response = await listAgents();
      this.agents = response.data.agents || [];
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      this.loadError = msg.includes("not found")
        ? "OMNISKILL CLI not found"
        : `Failed to load agents: ${msg.substring(0, 80)}`;
    } finally {
      this.loading = false;
    }
  }

  getAllAgents(): Agent[] {
    return this.agents;
  }
}
