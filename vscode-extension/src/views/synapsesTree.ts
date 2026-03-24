/**
 * Synapses Explorer Tree Data Provider
 *
 * FR-050: Synapse tree view in the Archon sidebar
 * FR-052: Synapse items display name, type badge, version, description
 *
 * Tree structure (flat — no categories for synapses):
 *   Synapse (e.g., "metacognition 🧠 core")
 */

import * as vscode from "vscode";
import { listSynapses } from "../cli";
import type { Synapse } from "../types";

// ─── Tree Item Types ────────────────────────────────────────────────────────

type SynapseTreeItem = SynapseItem;

class SynapseItem extends vscode.TreeItem {
  public readonly type = "synapse" as const;

  constructor(public readonly synapse: Synapse) {
    super(synapse.name, vscode.TreeItemCollapsibleState.None);

    const typeBadge = synapse.synapse_type === "core" ? "🧠 core" : "⚡ optional";
    this.description = `${typeBadge} — v${synapse.version}`;
    this.tooltip = new vscode.MarkdownString(
      `**${synapse.name}** v${synapse.version}\n\n` +
        `${synapse.description}\n\n` +
        `**Type:** ${synapse.synapse_type}\n` +
        `**Tags:** ${synapse.tags.join(", ")}\n` +
        `**Phases:** ${synapse.firing_phases.map((p) => p.name).join(" → ")}`,
    );

    this.iconPath = new vscode.ThemeIcon(
      synapse.synapse_type === "core" ? "brain" : "lightbulb",
      new vscode.ThemeColor("charts.purple"),
    );

    this.contextValue = `synapse-${synapse.synapse_type}`;

    // Click to show detail
    this.command = {
      command: "archon.showSynapseDetail",
      title: "Show Synapse Detail",
      arguments: [synapse],
    };
  }
}

// ─── Tree Data Provider ─────────────────────────────────────────────────────

export class SynapsesTreeProvider
  implements vscode.TreeDataProvider<SynapseTreeItem>
{
  private _onDidChangeTreeData = new vscode.EventEmitter<
    SynapseTreeItem | undefined | null
  >();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private synapses: Synapse[] = [];
  private loading = false;
  private loadError: string | null = null;

  /**
   * Refresh tree data by re-fetching from CLI.
   */
  refresh(): void {
    this.synapses = [];
    this.loadError = null;
    this._onDidChangeTreeData.fire(undefined);
  }

  getTreeItem(element: SynapseTreeItem): vscode.TreeItem {
    return element;
  }

  async getChildren(element?: SynapseTreeItem): Promise<SynapseTreeItem[]> {
    // Leaf nodes — synapses have no children
    if (element) {
      return [];
    }

    // Root — fetch synapses
    return this.getRootItems();
  }

  private async getRootItems(): Promise<SynapseTreeItem[]> {
    if (this.synapses.length === 0 && !this.loading && !this.loadError) {
      await this.fetchSynapses();
    }

    if (this.loadError) {
      const errorItem = new vscode.TreeItem(this.loadError);
      errorItem.iconPath = new vscode.ThemeIcon("warning");
      errorItem.contextValue = "error";
      return [errorItem as SynapseTreeItem];
    }

    if (this.loading) {
      const loadingItem = new vscode.TreeItem("Loading synapses...");
      loadingItem.iconPath = new vscode.ThemeIcon("loading~spin");
      return [loadingItem as SynapseTreeItem];
    }

    if (this.synapses.length === 0) {
      const emptyItem = new vscode.TreeItem("No synapses registered");
      emptyItem.iconPath = new vscode.ThemeIcon("info");
      return [emptyItem as SynapseTreeItem];
    }

    return this.synapses
      .sort((a, b) => a.name.localeCompare(b.name))
      .map((syn) => new SynapseItem(syn));
  }

  private async fetchSynapses(): Promise<void> {
    this.loading = true;
    try {
      const response = await listSynapses();
      this.synapses = response.data.items || [];
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("not found")) {
        this.loadError = "Archon CLI not found — click to install";
      } else {
        this.loadError = `Failed to load synapses: ${msg.substring(0, 80)}`;
      }
    } finally {
      this.loading = false;
    }
  }

  /**
   * Get a flat list of all synapses.
   */
  getAllSynapses(): Synapse[] {
    return this.synapses;
  }
}
