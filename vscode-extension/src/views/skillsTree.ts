/**
 * Skills Explorer Tree Data Provider
 *
 * FR-005: Categorized tree of all 49+ skills with installation status badges
 * FR-006: Search/filter functionality across all skills and categories
 *
 * Tree structure:
 *   Category (e.g., "Django (4 skills)")
 *     └─ Skill (e.g., "django-models ✓")
 */

import * as vscode from "vscode";
import { listSkills } from "../cli";
import type { Skill, SkillCategory } from "../types";

// ─── Tree Item Types ────────────────────────────────────────────────────────

type SkillTreeItem = CategoryItem | SkillItem;

class CategoryItem extends vscode.TreeItem {
  public readonly type = "category" as const;

  constructor(
    public readonly category: SkillCategory,
    private readonly installedCount: number,
  ) {
    super(category.name, vscode.TreeItemCollapsibleState.Collapsed);

    const total = category.skills.length;
    this.description = `${installedCount}/${total} installed`;
    this.tooltip = `${category.name}: ${total} skills, ${installedCount} installed`;
    this.iconPath = new vscode.ThemeIcon(
      installedCount === total
        ? "folder"
        : installedCount > 0
          ? "folder-opened"
          : "folder",
    );
    this.contextValue = "skill-category";
  }
}

class SkillItem extends vscode.TreeItem {
  public readonly type = "skill" as const;

  constructor(public readonly skill: Skill) {
    super(skill.name, vscode.TreeItemCollapsibleState.None);

    this.description = skill.description;
    this.tooltip = new vscode.MarkdownString(
      `**${skill.name}** v${skill.version}\n\n` +
        `${skill.description}\n\n` +
        `**Category:** ${skill.category}\n` +
        `**Tags:** ${skill.tags.join(", ")}\n` +
        `**Status:** ${skill.installed ? "✅ Installed" : "⬜ Not installed"}`,
    );

    this.iconPath = new vscode.ThemeIcon(
      skill.installed ? "check" : "circle-outline",
      skill.installed
        ? new vscode.ThemeColor("charts.green")
        : new vscode.ThemeColor("descriptionForeground"),
    );

    this.contextValue = skill.installed
      ? "skill-installed"
      : "skill-not-installed";

    // Click to show detail
    this.command = {
      command: "omniskill.showSkillDetail",
      title: "Show Skill Detail",
      arguments: [skill],
    };
  }
}

// ─── Tree Data Provider ─────────────────────────────────────────────────────

export class SkillsTreeProvider implements vscode.TreeDataProvider<SkillTreeItem> {
  private _onDidChangeTreeData = new vscode.EventEmitter<
    SkillTreeItem | undefined | null
  >();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private categories: SkillCategory[] = [];
  private allSkills: Skill[] = [];
  private filterQuery = "";
  private loading = false;
  private loadError: string | null = null;

  /**
   * Refresh tree data by re-fetching from CLI.
   */
  refresh(): void {
    this.categories = [];
    this.allSkills = [];
    this.loadError = null;
    this._onDidChangeTreeData.fire(undefined);
  }

  /**
   * Set filter query for search (FR-006).
   */
  setFilter(query: string): void {
    this.filterQuery = query.toLowerCase().trim();
    this._onDidChangeTreeData.fire(undefined);
  }

  /**
   * Clear search filter.
   */
  clearFilter(): void {
    this.filterQuery = "";
    this._onDidChangeTreeData.fire(undefined);
  }

  getTreeItem(element: SkillTreeItem): vscode.TreeItem {
    return element;
  }

  async getChildren(element?: SkillTreeItem): Promise<SkillTreeItem[]> {
    // Leaf nodes — skills have no children
    if (element instanceof SkillItem) {
      return [];
    }

    // Children of a category
    if (element instanceof CategoryItem) {
      return this.getSkillsForCategory(element.category);
    }

    // Root — fetch categories
    return this.getRootCategories();
  }

  private async getRootCategories(): Promise<SkillTreeItem[]> {
    // Fetch skills if not cached
    if (this.allSkills.length === 0 && !this.loading && !this.loadError) {
      await this.fetchSkills();
    }

    if (this.loadError) {
      const errorItem = new vscode.TreeItem(this.loadError);
      errorItem.iconPath = new vscode.ThemeIcon("warning");
      errorItem.contextValue = "error";
      return [errorItem as SkillTreeItem];
    }

    if (this.loading) {
      const loadingItem = new vscode.TreeItem("Loading skills...");
      loadingItem.iconPath = new vscode.ThemeIcon("loading~spin");
      return [loadingItem as SkillTreeItem];
    }

    // Apply filter
    const filteredCategories = this.getFilteredCategories();

    if (filteredCategories.length === 0 && this.filterQuery) {
      const noResults = new vscode.TreeItem(
        `No skills matching "${this.filterQuery}"`,
      );
      noResults.iconPath = new vscode.ThemeIcon("search-stop");
      return [noResults as SkillTreeItem];
    }

    return filteredCategories.map((cat) => {
      const installed = cat.skills.filter((s) => s.installed).length;
      return new CategoryItem(cat, installed);
    });
  }

  private getSkillsForCategory(category: SkillCategory): SkillTreeItem[] {
    let skills = category.skills;

    // Apply filter within category
    if (this.filterQuery) {
      skills = skills.filter(
        (s) =>
          s.name.toLowerCase().includes(this.filterQuery) ||
          s.description.toLowerCase().includes(this.filterQuery) ||
          s.tags.some((t) => t.toLowerCase().includes(this.filterQuery)),
      );
    }

    return skills
      .sort((a, b) => a.name.localeCompare(b.name))
      .map((s) => new SkillItem(s));
  }

  private getFilteredCategories(): SkillCategory[] {
    if (!this.filterQuery) {
      return this.categories;
    }

    return this.categories
      .map((cat) => ({
        ...cat,
        skills: cat.skills.filter(
          (s) =>
            s.name.toLowerCase().includes(this.filterQuery) ||
            s.description.toLowerCase().includes(this.filterQuery) ||
            s.tags.some((t) => t.toLowerCase().includes(this.filterQuery)) ||
            cat.name.toLowerCase().includes(this.filterQuery),
        ),
      }))
      .filter((cat) => cat.skills.length > 0);
  }

  private async fetchSkills(): Promise<void> {
    this.loading = true;
    try {
      const response = await listSkills();
      const data = response.data;

      this.allSkills = data.skills || [];

      // Use categories from response or build from skills
      if (data.categories && data.categories.length > 0) {
        this.categories = data.categories;
      } else {
        this.categories = this.buildCategories(this.allSkills);
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("not found")) {
        this.loadError = "OMNISKILL CLI not found — click to install";
      } else {
        this.loadError = `Failed to load skills: ${msg.substring(0, 80)}`;
      }
    } finally {
      this.loading = false;
    }
  }

  private buildCategories(skills: Skill[]): SkillCategory[] {
    const categoryMap = new Map<string, Skill[]>();

    for (const skill of skills) {
      const cat = skill.category || "Uncategorized";
      if (!categoryMap.has(cat)) {
        categoryMap.set(cat, []);
      }
      categoryMap.get(cat)!.push(skill);
    }

    return Array.from(categoryMap.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([name, catSkills]) => ({
        name,
        skills: catSkills,
        count: catSkills.length,
      }));
  }

  /**
   * Get a flat list of all skills (for quick pick, etc.)
   */
  getAllSkills(): Skill[] {
    return this.allSkills;
  }
}
