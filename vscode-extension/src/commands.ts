/**
 * OMNISKILL Command Registrations
 *
 * FR-017: 13+ commands registered in command palette
 * FR-018: Initialize, Install Skill, Install Bundle, Uninstall, Run Pipeline,
 *         Show Dashboard, Run Doctor, Validate, Search, Admin Dashboard,
 *         Update, Settings, Context Budget
 */

import * as vscode from "vscode";
import * as cli from "./cli";
import { SkillsTreeProvider } from "./views/skillsTree";
import { AgentsTreeProvider } from "./views/agentsTree";
import { PipelinesTreeProvider } from "./views/pipelinesTree";
import { BundlesTreeProvider } from "./views/bundlesTree";
import { DashboardPanel } from "./webviews/dashboardPanel";
import { SkillDetailPanel } from "./webviews/skillDetailPanel";
import { HealthPanel } from "./webviews/healthPanel";
import { StatusBarManager } from "./statusBar";
import type { Skill, Agent, Pipeline, PipelineRunData } from "./types";

/**
 * Register all OMNISKILL commands.
 */
export function registerCommands(
  context: vscode.ExtensionContext,
  skillsTree: SkillsTreeProvider,
  agentsTree: AgentsTreeProvider,
  pipelinesTree: PipelinesTreeProvider,
  bundlesTree: BundlesTreeProvider,
  statusBar: StatusBarManager,
): void {
  const register = (
    id: string,
    handler: (...args: unknown[]) => Promise<void> | void,
  ) => {
    context.subscriptions.push(vscode.commands.registerCommand(id, handler));
  };

  // ─── Initialize ─────────────────────────────────────────────────────
  register("omniskill.initialize", async () => {
    const cliOk = await cli.checkCliAvailable();
    if (!cliOk) {
      await cli.showInstallPrompt();
      return;
    }

    try {
      await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: "OMNISKILL: Initializing...",
        },
        async () => {
          const result = await cli.initOmniskill();
          const data = result.data;
          vscode.window.showInformationMessage(
            `OMNISKILL initialized! Detected platforms: ${data.platforms_detected.join(", ")}. ` +
              `Config: ${data.config_path}`,
          );
        },
      );
    } catch (err) {
      vscode.window.showErrorMessage(
        `Initialize failed: ${err instanceof Error ? err.message : err}`,
      );
    }
  });

  // ─── Install Skill ──────────────────────────────────────────────────
  register("omniskill.installSkill", async (...args: unknown[]) => {
    let skillName: string | undefined;

    // If called from tree context menu, first arg is a tree item
    if (
      args[0] &&
      typeof args[0] === "object" &&
      "skill" in (args[0] as Record<string, unknown>)
    ) {
      skillName = ((args[0] as Record<string, unknown>).skill as Skill).name;
    }

    if (!skillName) {
      skillName = await vscode.window.showInputBox({
        prompt: "Enter skill name to install",
        placeHolder: "e.g., spec-writer, django-models",
      });
    }

    if (!skillName) {
      return;
    }

    try {
      await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: `Installing skill: ${skillName}...`,
        },
        async () => {
          await cli.installSkill(skillName!);
          vscode.window.showInformationMessage(
            `Skill "${skillName}" installed successfully.`,
          );
          skillsTree.refresh();
          bundlesTree.refresh();
        },
      );
    } catch (err) {
      vscode.window.showErrorMessage(
        `Install failed: ${err instanceof Error ? err.message : err}`,
      );
    }
  });

  // ─── Install Bundle ─────────────────────────────────────────────────
  register("omniskill.installBundle", async (...args: unknown[]) => {
    let bundleName: string | undefined;

    if (
      args[0] &&
      typeof args[0] === "object" &&
      "bundle" in (args[0] as Record<string, unknown>)
    ) {
      bundleName = (
        (args[0] as Record<string, unknown>).bundle as { name: string }
      ).name;
    }

    if (!bundleName) {
      bundleName = await vscode.window.showInputBox({
        prompt: "Enter bundle name to install",
        placeHolder: "e.g., sdd-kit, web-dev-kit, django-kit",
      });
    }

    if (!bundleName) {
      return;
    }

    try {
      await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: `Installing bundle: ${bundleName}...`,
        },
        async () => {
          await cli.installBundle(bundleName!);
          vscode.window.showInformationMessage(
            `Bundle "${bundleName}" installed successfully.`,
          );
          skillsTree.refresh();
          bundlesTree.refresh();
        },
      );
    } catch (err) {
      vscode.window.showErrorMessage(
        `Bundle install failed: ${err instanceof Error ? err.message : err}`,
      );
    }
  });

  // ─── Uninstall Component ────────────────────────────────────────────
  register("omniskill.uninstallComponent", async (...args: unknown[]) => {
    let componentName: string | undefined;

    if (
      args[0] &&
      typeof args[0] === "object" &&
      "skill" in (args[0] as Record<string, unknown>)
    ) {
      componentName = ((args[0] as Record<string, unknown>).skill as Skill)
        .name;
    }

    if (!componentName) {
      componentName = await vscode.window.showInputBox({
        prompt: "Enter component name to uninstall",
        placeHolder: "Skill or bundle name",
      });
    }

    if (!componentName) {
      return;
    }

    const confirm = await vscode.window.showWarningMessage(
      `Uninstall "${componentName}"?`,
      { modal: true },
      "Uninstall",
    );

    if (confirm !== "Uninstall") {
      return;
    }

    try {
      await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: `Uninstalling: ${componentName}...`,
        },
        async () => {
          await cli.uninstallComponent(componentName!);
          vscode.window.showInformationMessage(
            `"${componentName}" uninstalled successfully.`,
          );
          skillsTree.refresh();
          bundlesTree.refresh();
        },
      );
    } catch (err) {
      vscode.window.showErrorMessage(
        `Uninstall failed: ${err instanceof Error ? err.message : err}`,
      );
    }
  });

  // ─── Run Pipeline ───────────────────────────────────────────────────
  register("omniskill.runPipeline", async (...args: unknown[]) => {
    let pipelineName: string | undefined;

    if (
      args[0] &&
      typeof args[0] === "object" &&
      "pipeline" in (args[0] as Record<string, unknown>)
    ) {
      pipelineName = ((args[0] as Record<string, unknown>).pipeline as Pipeline)
        .name;
    }

    if (!pipelineName) {
      const pipelines = pipelinesTree.getAllPipelines();
      if (pipelines.length > 0) {
        const pick = await vscode.window.showQuickPick(
          pipelines.map((p) => ({
            label: p.name,
            description: p.description,
            detail: `${p.steps.length} steps — ${p.tags.join(", ")}`,
          })),
          { placeHolder: "Select a pipeline to run" },
        );
        pipelineName = pick?.label;
      } else {
        pipelineName = await vscode.window.showInputBox({
          prompt: "Enter pipeline name to run",
          placeHolder: "e.g., sdd-pipeline, ux-pipeline",
        });
      }
    }

    if (!pipelineName) {
      return;
    }

    // Open dashboard
    const dashboard = DashboardPanel.show(context.extensionUri);
    statusBar.setPipelineRunning(pipelineName, 0, 0);

    // Stream pipeline execution
    const runName = pipelineName;
    const disposable = cli.execCliStreaming(
      "pipeline",
      ["run", runName],
      (line: string) => {
        // Try to parse JSON progress updates
        try {
          const update = JSON.parse(line) as PipelineRunData;
          if (update.pipeline) {
            dashboard.updateRun(update);
            statusBar.setPipelineRunning(
              update.pipeline,
              update.current_step,
              update.total_steps,
            );

            if (update.context_budget) {
              statusBar.setBudget(
                update.context_budget.used,
                update.context_budget.total,
              );
            }
          }
        } catch {
          // Non-JSON line — log to output channel
        }
      },
      (code: number | null) => {
        if (code === 0) {
          statusBar.setPipelineComplete(runName);
          vscode.window.showInformationMessage(
            `Pipeline "${runName}" completed successfully.`,
          );
        } else {
          statusBar.setPipelineFailed(runName, "unknown");
          vscode.window.showErrorMessage(
            `Pipeline "${runName}" failed with exit code ${code}.`,
          );
        }
        pipelinesTree.refresh();
      },
    );

    context.subscriptions.push(disposable);
  });

  // ─── Show Dashboard ─────────────────────────────────────────────────
  register("omniskill.showDashboard", () => {
    DashboardPanel.show(context.extensionUri);
  });

  // ─── Run Doctor ─────────────────────────────────────────────────────
  register("omniskill.runDoctor", async () => {
    const cliOk = await cli.checkCliAvailable();
    if (!cliOk) {
      await cli.showInstallPrompt();
      return;
    }
    await HealthPanel.show();
  });

  // ─── Validate Workspace ─────────────────────────────────────────────
  register("omniskill.validateWorkspace", async () => {
    try {
      const result = await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: "OMNISKILL: Validating workspace...",
        },
        async () => cli.validateWorkspace(),
      );

      const data = result.data;
      if (data.valid) {
        vscode.window.showInformationMessage(
          `Workspace valid! Checked: ${data.checked.join(", ")}` +
            (data.warnings.length > 0
              ? ` (${data.warnings.length} warnings)`
              : ""),
        );
      } else {
        vscode.window.showWarningMessage(
          `Workspace validation failed: ${data.errors.join("; ")}`,
        );
      }
    } catch (err) {
      vscode.window.showErrorMessage(
        `Validation failed: ${err instanceof Error ? err.message : err}`,
      );
    }
  });

  // ─── Search Skills ──────────────────────────────────────────────────
  register("omniskill.searchSkills", async () => {
    const query = await vscode.window.showInputBox({
      prompt: "Search OMNISKILL skills",
      placeHolder: "Enter keywords (e.g., django, testing, ux)",
    });

    if (!query) {
      return;
    }

    // Use tree filter for quick search
    skillsTree.setFilter(query);

    // Also try CLI search for broader results
    try {
      const result = await cli.searchSkills(query);
      if (result.data.results.length === 0) {
        vscode.window.showInformationMessage(
          `No results found for "${query}".`,
        );
      }
    } catch {
      // Fall back to tree filter only
    }
  });

  // ─── Admin Dashboard ────────────────────────────────────────────────
  register("omniskill.adminDashboard", async () => {
    try {
      const result = await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: "Loading admin stats...",
        },
        async () => cli.getAdminStats(),
      );

      const data = result.data;
      const msg = [
        `OMNISKILL v${data.version}`,
        `Skills: ${data.skills_installed}/${data.skills_total} installed`,
        `Agents: ${data.agents_total}`,
        `Pipelines: ${data.pipelines_total}`,
        `Bundles: ${data.bundles_total}`,
        `Platforms: ${data.platforms.join(", ")}`,
      ].join(" | ");

      vscode.window
        .showInformationMessage(msg, "Open Dashboard")
        .then((choice) => {
          if (choice === "Open Dashboard") {
            DashboardPanel.show(context.extensionUri);
          }
        });
    } catch (err) {
      vscode.window.showErrorMessage(
        `Admin stats failed: ${err instanceof Error ? err.message : err}`,
      );
    }
  });

  // ─── Update ─────────────────────────────────────────────────────────
  register("omniskill.update", async () => {
    try {
      const checkResult = await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: "Checking for OMNISKILL updates...",
        },
        async () => cli.checkUpdate(),
      );

      const data = checkResult.data;
      if (!data.update_available) {
        vscode.window.showInformationMessage(
          `OMNISKILL is up to date (v${data.current_version}).`,
        );
        return;
      }

      const choice = await vscode.window.showInformationMessage(
        `OMNISKILL update available: v${data.current_version} → v${data.latest_version}`,
        "Update Now",
        "Later",
      );

      if (choice === "Update Now") {
        await vscode.window.withProgress(
          {
            location: vscode.ProgressLocation.Notification,
            title: "Updating OMNISKILL...",
          },
          async () => {
            await cli.applyUpdate();
            vscode.window.showInformationMessage(
              `OMNISKILL updated to v${data.latest_version}!`,
            );
            cli.resetCliCache();
            skillsTree.refresh();
            agentsTree.refresh();
            pipelinesTree.refresh();
            bundlesTree.refresh();
          },
        );
      }
    } catch (err) {
      vscode.window.showErrorMessage(
        `Update check failed: ${err instanceof Error ? err.message : err}`,
      );
    }
  });

  // ─── Open Settings ──────────────────────────────────────────────────
  register("omniskill.openSettings", () => {
    vscode.commands.executeCommand(
      "workbench.action.openSettings",
      "omniskill",
    );
  });

  // ─── Show Context Budget ────────────────────────────────────────────
  register("omniskill.showContextBudget", async () => {
    try {
      const result = await cli.execCli<import("./types").ContextBudgetData>(
        "config",
        ["context-budget"],
      );
      const data = result.data;

      const usedStr =
        data.used_tokens >= 1000
          ? Math.round(data.used_tokens / 1000) + "K"
          : String(data.used_tokens);
      const totalStr =
        data.total_tokens >= 1000
          ? Math.round(data.total_tokens / 1000) + "K"
          : String(data.total_tokens);

      let breakdown = "";
      if (data.breakdown && data.breakdown.length > 0) {
        breakdown =
          "\n\nBreakdown:\n" +
          data.breakdown
            .map(
              (b) => `  ${b.component}: ${Math.round(b.tokens / 1000)}K tokens`,
            )
            .join("\n");
      }

      vscode.window.showInformationMessage(
        `Context Budget: ${usedStr}/${totalStr} tokens (${data.percentage}%)${breakdown}`,
      );

      statusBar.setBudget(data.used_tokens, data.total_tokens);
    } catch (err) {
      vscode.window.showWarningMessage(
        `Context budget unavailable: ${err instanceof Error ? err.message : err}`,
      );
    }
  });

  // ─── Show Skill Detail (internal) ───────────────────────────────────
  register("omniskill.showSkillDetail", async (...args: unknown[]) => {
    const skill = args[0] as Skill | undefined;
    if (skill) {
      await SkillDetailPanel.show(skill);
    }
  });

  // ─── Show Agent Detail (internal) ───────────────────────────────────
  register("omniskill.showAgentDetail", async (...args: unknown[]) => {
    const agent = args[0] as Agent | undefined;
    if (!agent) {
      return;
    }

    // Show agent documentation in a simple webview
    try {
      const detail = await cli.getAgentInfo(agent.name);
      const doc = detail.data.documentation || "No documentation available.";

      const panel = vscode.window.createWebviewPanel(
        "omniskill.agentDetail",
        `Agent: ${agent.name}`,
        vscode.ViewColumn.One,
        { enableScripts: false },
      );

      panel.webview.html = getAgentDetailHtml(agent, doc);
    } catch {
      // Fallback: show basic info
      const panel = vscode.window.createWebviewPanel(
        "omniskill.agentDetail",
        `Agent: ${agent.name}`,
        vscode.ViewColumn.One,
        { enableScripts: false },
      );

      panel.webview.html = getAgentDetailHtml(
        agent,
        "*Documentation unavailable — CLI may not be reachable.*",
      );
    }
  });

  // ─── Invoke Agent (context menu) ────────────────────────────────────
  register("omniskill.invokeAgent", async (...args: unknown[]) => {
    let agentName: string | undefined;

    if (
      args[0] &&
      typeof args[0] === "object" &&
      "agent" in (args[0] as Record<string, unknown>)
    ) {
      agentName = ((args[0] as Record<string, unknown>).agent as Agent).name;
    }

    if (!agentName) {
      agentName = await vscode.window.showInputBox({
        prompt: "Enter agent name to invoke",
        placeHolder: "e.g., spec-writer-agent",
      });
    }

    if (!agentName) {
      return;
    }

    const input = await vscode.window.showInputBox({
      prompt: `Provide input for ${agentName}`,
      placeHolder: "Describe what you want the agent to do...",
    });

    if (!input) {
      return;
    }

    // Run in terminal
    const terminal = vscode.window.createTerminal(`OMNISKILL: ${agentName}`);
    const cliPath = vscode.workspace
      .getConfiguration("omniskill")
      .get<string>("cliPath", "omniskill");
    terminal.sendText(
      `${cliPath} pipeline run-agent ${agentName} --input "${input.replace(/"/g, '\\"')}"`,
    );
    terminal.show();
  });

  // ─── Refresh commands for tree views ────────────────────────────────
  register("omniskill.refreshSkills", () => skillsTree.refresh());
  register("omniskill.refreshAgents", () => agentsTree.refresh());
  register("omniskill.refreshPipelines", () => pipelinesTree.refresh());
  register("omniskill.refreshBundles", () => bundlesTree.refresh());
  register("omniskill.refreshDashboard", () => {
    // Placeholder for dashboard refresh
  });
}

// ─── Agent Detail HTML Helper ───────────────────────────────────────────────

function getAgentDetailHtml(agent: Agent, documentation: string): string {
  const esc = (s: string) =>
    s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");

  return /*html*/ `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent: ${esc(agent.name)}</title>
    <style>
        body {
            font-family: var(--vscode-font-family, 'Segoe UI', sans-serif);
            background: var(--vscode-editor-background, #1a1a2e);
            color: var(--vscode-editor-foreground, #e0e0e0);
            margin: 0; padding: 24px; line-height: 1.6;
        }

        .agent-header {
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--vscode-panel-border, #2a3a5e);
        }

        .agent-header h1 {
            margin: 0 0 4px 0; font-size: 22px;
            display: flex; align-items: center; gap: 10px;
        }

        .badge {
            font-size: 12px; padding: 2px 8px;
            background: rgba(108, 63, 232, 0.2);
            color: #a78bfa; border-radius: 10px;
        }

        .meta-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px; margin-bottom: 24px;
        }

        .meta-card {
            background: var(--vscode-sideBar-background, #1e2a4a);
            border: 1px solid var(--vscode-panel-border, #2a3a5e);
            border-radius: 8px; padding: 12px;
        }

        .meta-card h3 {
            margin: 0 0 6px 0; font-size: 11px;
            text-transform: uppercase; letter-spacing: 0.5px;
            color: var(--vscode-descriptionForeground, #a0a0b0);
        }

        .tag {
            display: inline-block; padding: 2px 8px; margin: 2px;
            background: rgba(59, 130, 246, 0.15);
            color: #60a5fa; border-radius: 4px; font-size: 11px;
        }

        .doc-content {
            background: var(--vscode-sideBar-background, #1e2a4a);
            border: 1px solid var(--vscode-panel-border, #2a3a5e);
            border-radius: 8px; padding: 20px;
            white-space: pre-wrap; font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="agent-header">
        <h1>
            🤖 ${esc(agent.name)}
            <span class="badge">${esc(agent.workflow_phase)}</span>
        </h1>
        <div style="color:var(--vscode-descriptionForeground);font-size:14px;">
            ${esc(agent.role)} — ${esc(agent.description)}
        </div>
    </div>

    <div class="meta-grid">
        <div class="meta-card">
            <h3>Skills</h3>
            <div>${agent.skills.map((s) => `<span class="tag">${esc(s)}</span>`).join(" ")}</div>
        </div>
        <div class="meta-card">
            <h3>Capabilities</h3>
            <div>${agent.capabilities.map((c) => `<span class="tag">${esc(c)}</span>`).join(" ")}</div>
        </div>
        ${
          agent.handoff
            ? `
        <div class="meta-card">
            <h3>Handoff</h3>
            <div>→ ${esc(agent.handoff.next_agent)}<br/>
            <span style="font-size:11px;color:var(--vscode-descriptionForeground);">Produces: ${esc(agent.handoff.artifact)}</span></div>
        </div>
        `
            : ""
        }
    </div>

    <div class="doc-content">${esc(documentation)}</div>
</body>
</html>`;
}
