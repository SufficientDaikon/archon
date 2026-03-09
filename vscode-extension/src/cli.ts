/**
 * OMNISKILL CLI Subprocess Wrapper
 *
 * Spawns `omniskill <command> --json` and parses the JSON envelope response.
 * Handles CLI-not-found gracefully with install prompts.
 * Configurable via `omniskill.cliPath` setting.
 *
 * FR-001: Spawn CLI as subprocess (never reimplement logic)
 * FR-002: Use --json output mode for all commands
 * FR-003: Handle timeouts gracefully (30s default)
 * FR-004: Verify CLI availability and guide install
 */

import * as vscode from "vscode";
import { spawn } from "child_process";
import type { CliResponse } from "./types";

/** Default subprocess timeout in milliseconds (30 seconds per NFR-002) */
const DEFAULT_TIMEOUT_MS = 30_000;

/** Cached CLI availability status */
let cliAvailable: boolean | null = null;

/**
 * Get the configured CLI path from settings.
 */
function getCliPath(): string {
  const config = vscode.workspace.getConfiguration("omniskill");
  return config.get<string>("cliPath", "omniskill");
}

/**
 * Get the configured default platform.
 */
function getDefaultPlatform(): string {
  const config = vscode.workspace.getConfiguration("omniskill");
  return config.get<string>("defaultPlatform", "auto");
}

/**
 * Execute an OMNISKILL CLI command and return the parsed JSON response.
 *
 * @param command - The CLI subcommand (e.g., 'list', 'install', 'doctor')
 * @param args - Additional arguments to pass after the command
 * @param options - Execution options (timeout, cwd)
 * @returns Parsed CliResponse<T> on success
 * @throws Error if CLI not found, timeout, or invalid JSON
 */
export async function execCli<T = unknown>(
  command: string,
  args: string[] = [],
  options: { timeout?: number; cwd?: string } = {},
): Promise<CliResponse<T>> {
  const cliPath = getCliPath();
  const timeout = options.timeout ?? DEFAULT_TIMEOUT_MS;
  const cwd = options.cwd ?? vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

  const fullArgs = [command, "--json", ...args];

  return new Promise<CliResponse<T>>((resolve, reject) => {
    let stdout = "";
    let stderr = "";
    let settled = false;

    const proc = spawn(cliPath, fullArgs, {
      cwd: cwd || undefined,
      shell: true,
      env: { ...process.env },
      windowsHide: true,
    });

    // Timeout handler (NFR-002: 30s)
    const timer = setTimeout(() => {
      if (!settled) {
        settled = true;
        proc.kill("SIGTERM");
        reject(
          new Error(
            `OMNISKILL CLI timed out after ${timeout / 1000}s running: ${command} ${args.join(" ")}`,
          ),
        );
      }
    }, timeout);

    proc.stdout.on("data", (chunk: Buffer) => {
      stdout += chunk.toString();
    });

    proc.stderr.on("data", (chunk: Buffer) => {
      stderr += chunk.toString();
    });

    proc.on("error", (err: NodeJS.ErrnoException) => {
      if (settled) {
        return;
      }
      settled = true;
      clearTimeout(timer);

      if (err.code === "ENOENT") {
        cliAvailable = false;
        reject(new CliNotFoundError(cliPath));
      } else {
        reject(new Error(`OMNISKILL CLI error: ${err.message}`));
      }
    });

    proc.on("close", (code) => {
      if (settled) {
        return;
      }
      settled = true;
      clearTimeout(timer);

      // Mark CLI as available since the process ran
      cliAvailable = true;

      // Try parsing JSON from stdout
      const jsonText = stdout.trim();
      if (!jsonText) {
        if (code !== 0) {
          reject(
            new Error(
              `OMNISKILL CLI exited with code ${code}: ${stderr.trim() || "No output"}`,
            ),
          );
        } else {
          reject(new Error("OMNISKILL CLI returned empty response"));
        }
        return;
      }

      try {
        const response = JSON.parse(jsonText) as CliResponse<T>;
        if (response.status === "error" && response.errors.length > 0) {
          reject(new CliCommandError(command, response.errors));
        } else {
          resolve(response);
        }
      } catch {
        // JSON parse failed — maybe the CLI printed non-JSON output
        // Try to extract JSON from the output (it may have log lines before it)
        const jsonMatch = jsonText.match(/\{[\s\S]*\}$/);
        if (jsonMatch) {
          try {
            const response = JSON.parse(jsonMatch[0]) as CliResponse<T>;
            resolve(response);
            return;
          } catch {
            // fall through
          }
        }
        reject(
          new Error(
            `Failed to parse OMNISKILL CLI JSON output for '${command}': ${jsonText.substring(0, 200)}`,
          ),
        );
      }
    });
  });
}

/**
 * Execute a CLI command that streams output (e.g., pipeline runs).
 * Returns a disposable that can cancel the process.
 */
export function execCliStreaming(
  command: string,
  args: string[] = [],
  onData: (line: string) => void,
  onComplete: (code: number | null) => void,
  options: { cwd?: string } = {},
): vscode.Disposable {
  const cliPath = getCliPath();
  const cwd = options.cwd ?? vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

  const proc = spawn(cliPath, [command, "--json", ...args], {
    cwd: cwd || undefined,
    shell: true,
    env: { ...process.env },
    windowsHide: true,
  });

  let buffer = "";

  proc.stdout.on("data", (chunk: Buffer) => {
    buffer += chunk.toString();
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed) {
        onData(trimmed);
      }
    }
  });

  proc.stderr.on("data", (chunk: Buffer) => {
    const text = chunk.toString().trim();
    if (text) {
      onData(`[stderr] ${text}`);
    }
  });

  proc.on("close", (code) => {
    if (buffer.trim()) {
      onData(buffer.trim());
    }
    onComplete(code);
  });

  proc.on("error", (err: NodeJS.ErrnoException) => {
    if (err.code === "ENOENT") {
      cliAvailable = false;
      onData(`[error] CLI not found at: ${cliPath}`);
    } else {
      onData(`[error] ${err.message}`);
    }
    onComplete(1);
  });

  return new vscode.Disposable(() => {
    if (!proc.killed) {
      proc.kill("SIGTERM");
    }
  });
}

/**
 * Check if the OMNISKILL CLI is available.
 * Caches the result for subsequent calls.
 */
export async function checkCliAvailable(): Promise<boolean> {
  if (cliAvailable !== null) {
    return cliAvailable;
  }

  try {
    await execCli("--version", [], { timeout: 10_000 });
    cliAvailable = true;
    return true;
  } catch (err) {
    if (err instanceof CliNotFoundError) {
      cliAvailable = false;
      return false;
    }
    // CLI exists but the command might have errored — still "available"
    cliAvailable = true;
    return true;
  }
}

/**
 * Reset the cached CLI availability status.
 * Called when user changes the cliPath setting.
 */
export function resetCliCache(): void {
  cliAvailable = null;
}

/**
 * Show an install prompt when CLI is not found.
 * FR-004: Guide users to install if missing.
 */
export async function showInstallPrompt(): Promise<void> {
  const cliPath = getCliPath();
  const choice = await vscode.window.showErrorMessage(
    `OMNISKILL CLI not found at "${cliPath}". The extension requires the OMNISKILL CLI to function.`,
    "Install with pip",
    "Set CLI Path",
    "Dismiss",
  );

  switch (choice) {
    case "Install with pip": {
      const terminal = vscode.window.createTerminal("OMNISKILL Install");
      terminal.sendText("pip install omniskill");
      terminal.show();
      resetCliCache();
      break;
    }
    case "Set CLI Path": {
      await vscode.commands.executeCommand(
        "workbench.action.openSettings",
        "omniskill.cliPath",
      );
      break;
    }
  }
}

// ─── Custom Error Classes ───────────────────────────────────────────────────

export class CliNotFoundError extends Error {
  constructor(public readonly cliPath: string) {
    super(`OMNISKILL CLI not found at: ${cliPath}`);
    this.name = "CliNotFoundError";
  }
}

export class CliCommandError extends Error {
  constructor(
    public readonly command: string,
    public readonly errors: string[],
  ) {
    super(`OMNISKILL CLI command '${command}' failed: ${errors.join("; ")}`);
    this.name = "CliCommandError";
  }
}

// ─── Convenience Methods ────────────────────────────────────────────────────

/** List all skills */
export async function listSkills() {
  return execCli<import("./types").SkillListData>("list", ["skills"]);
}

/** List all agents */
export async function listAgents() {
  return execCli<import("./types").AgentListData>("list", ["agents"]);
}

/** List all pipelines */
export async function listPipelines() {
  return execCli<import("./types").PipelineListData>("list", ["pipelines"]);
}

/** List all bundles */
export async function listBundles() {
  return execCli<import("./types").BundleListData>("list", ["bundles"]);
}

/** List all synapses */
export async function listSynapses() {
  return execCli<import("./types").SynapseListData>("list", ["synapses"]);
}

/** Get skill details */
export async function getSkillInfo(skillName: string) {
  return execCli<import("./types").SkillDetailData>("info", [skillName]);
}

/** Get agent details */
export async function getAgentInfo(agentName: string) {
  return execCli<import("./types").AgentDetailData>("info", [
    "--type",
    "agent",
    agentName,
  ]);
}

/** Install a skill */
export async function installSkill(skillName: string, platform?: string) {
  const args = [skillName];
  const plat = platform ?? getDefaultPlatform();
  if (plat !== "auto") {
    args.push("--platform", plat);
  }
  return execCli("install", args);
}

/** Install a bundle */
export async function installBundle(bundleName: string, platform?: string) {
  const args = [bundleName, "--bundle"];
  const plat = platform ?? getDefaultPlatform();
  if (plat !== "auto") {
    args.push("--platform", plat);
  }
  return execCli("install", args);
}

/** Uninstall a component */
export async function uninstallComponent(name: string) {
  return execCli("uninstall", [name]);
}

/** Run doctor */
export async function runDoctor() {
  return execCli<import("./types").DoctorData>("doctor", [], {
    timeout: 60_000,
  });
}

/** Search skills */
export async function searchSkills(query: string) {
  return execCli<import("./types").SearchData>("search", [query]);
}

/** Validate workspace */
export async function validateWorkspace() {
  return execCli<import("./types").ValidationResult>("validate");
}

/** Get admin stats */
export async function getAdminStats() {
  return execCli<import("./types").AdminData>("admin");
}

/** Initialize OMNISKILL in workspace */
export async function initOmniskill() {
  return execCli<import("./types").InitData>("init");
}

/** Check for updates */
export async function checkUpdate() {
  return execCli<import("./types").UpdateData>("update", ["--check"]);
}

/** Apply update */
export async function applyUpdate() {
  return execCli("update", ["--apply"], { timeout: 120_000 });
}
