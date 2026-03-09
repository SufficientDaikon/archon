/**
 * Bundles Panel Tree Data Provider
 *
 * FR-009: Display all 8 bundles with expandable skill contents and installation status
 *
 * Tree structure:
 *   Bundle (e.g., "sdd-kit — Spec-Driven Development ✓ Installed")
 *     └─ Skill (e.g., "spec-writer ✓")
 */

import * as vscode from "vscode";
import { listBundles } from "../cli";
import type { Bundle } from "../types";

// ─── Tree Item Types ────────────────────────────────────────────────────────

type BundleTreeItem = BundleItem | BundleSkillItem;

class BundleItem extends vscode.TreeItem {
  public readonly type = "bundle" as const;

  constructor(public readonly bundle: Bundle) {
    super(bundle.name, vscode.TreeItemCollapsibleState.Collapsed);

    const installed = bundle.installed_skills.length;
    const total = bundle.skills.length;

    const statusLabel =
      bundle.status === "installed"
        ? "✅ Installed"
        : bundle.status === "partial"
          ? `⚡ Partial (${installed}/${total})`
          : "⬜ Not installed";

    this.description = `${statusLabel} — ${bundle.description}`;
    this.tooltip = new vscode.MarkdownString(
      `**${bundle.name}** v${bundle.version}\n\n` +
        `${bundle.description}\n\n` +
        `**Skills:** ${total} (${installed} installed)\n` +
        `**Status:** ${statusLabel}`,
    );

    const iconMap: Record<string, { icon: string; color: string }> = {
      installed: { icon: "package", color: "charts.green" },
      partial: { icon: "package", color: "charts.yellow" },
      "not-installed": { icon: "package", color: "descriptionForeground" },
    };
    const ic = iconMap[bundle.status] || iconMap["not-installed"];
    this.iconPath = new vscode.ThemeIcon(
      ic.icon,
      new vscode.ThemeColor(ic.color),
    );

    this.contextValue = `bundle-${bundle.status}`;
  }
}

class BundleSkillItem extends vscode.TreeItem {
  public readonly type = "bundle-skill" as const;

  constructor(
    public readonly skillName: string,
    public readonly installed: boolean,
    public readonly bundleName: string,
  ) {
    super(skillName, vscode.TreeItemCollapsibleState.None);

    this.description = installed ? "Installed" : "Not installed";
    this.iconPath = new vscode.ThemeIcon(
      installed ? "check" : "circle-outline",
      installed
        ? new vscode.ThemeColor("charts.green")
        : new vscode.ThemeColor("descriptionForeground"),
    );

    this.contextValue = installed
      ? "bundle-skill-installed"
      : "bundle-skill-not-installed";
  }
}

// ─── Tree Data Provider ─────────────────────────────────────────────────────

export class BundlesTreeProvider implements vscode.TreeDataProvider<BundleTreeItem> {
  private _onDidChangeTreeData = new vscode.EventEmitter<
    BundleTreeItem | undefined | null
  >();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private bundles: Bundle[] = [];
  private loading = false;
  private loadError: string | null = null;

  refresh(): void {
    this.bundles = [];
    this.loadError = null;
    this._onDidChangeTreeData.fire(undefined);
  }

  getTreeItem(element: BundleTreeItem): vscode.TreeItem {
    return element;
  }

  async getChildren(element?: BundleTreeItem): Promise<BundleTreeItem[]> {
    // Bundle skill items have no children
    if (element instanceof BundleSkillItem) {
      return [];
    }

    // Children of a bundle = its skills
    if (element instanceof BundleItem) {
      const bundle = element.bundle;
      return bundle.skills.map(
        (skillName) =>
          new BundleSkillItem(
            skillName,
            bundle.installed_skills.includes(skillName),
            bundle.name,
          ),
      );
    }

    // Root: fetch bundles
    if (this.bundles.length === 0 && !this.loading && !this.loadError) {
      await this.fetchBundles();
    }

    if (this.loadError) {
      const errorItem = new vscode.TreeItem(this.loadError) as BundleTreeItem;
      errorItem.iconPath = new vscode.ThemeIcon("warning");
      return [errorItem];
    }

    if (this.loading) {
      const loadingItem = new vscode.TreeItem(
        "Loading bundles...",
      ) as BundleTreeItem;
      loadingItem.iconPath = new vscode.ThemeIcon("loading~spin");
      return [loadingItem];
    }

    return this.bundles
      .sort((a, b) => a.name.localeCompare(b.name))
      .map((b) => new BundleItem(b));
  }

  private async fetchBundles(): Promise<void> {
    this.loading = true;
    try {
      const response = await listBundles();
      this.bundles = response.data.bundles || [];
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      this.loadError = msg.includes("not found")
        ? "OMNISKILL CLI not found"
        : `Failed to load bundles: ${msg.substring(0, 80)}`;
    } finally {
      this.loading = false;
    }
  }

  getAllBundles(): Bundle[] {
    return this.bundles;
  }
}
