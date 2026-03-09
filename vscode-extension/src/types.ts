/**
 * OMNISKILL VS Code Extension — TypeScript type definitions
 * Types for CLI JSON response envelopes and domain entities.
 */

// ─── CLI Response Envelope ──────────────────────────────────────────────────

/** Standard JSON response envelope from `omniskill --json` commands */
export interface CliResponse<T = unknown> {
  status: "success" | "error" | "warning";
  command: string;
  version: string;
  data: T;
  errors: string[];
  diagnostics?: Record<string, unknown>;
}

// ─── Skills ─────────────────────────────────────────────────────────────────

export interface Skill {
  name: string;
  version: string;
  description: string;
  category: string;
  tags: string[];
  priority: string;
  platforms: string[];
  installed: boolean;
  path: string;
}

export interface SkillCategory {
  name: string;
  skills: Skill[];
  count: number;
}

export interface SkillListData {
  skills: Skill[];
  categories: SkillCategory[];
  total: number;
  installed_count: number;
}

export interface SkillDetailData {
  skill: Skill;
  documentation: string;
  examples: string[];
  dependencies: string[];
  triggers: string[];
}

// ─── Agents ─────────────────────────────────────────────────────────────────

export interface Agent {
  name: string;
  version: string;
  role: string;
  description: string;
  capabilities: string[];
  skills: string[];
  workflow_phase: string;
  handoff?: {
    next_agent: string;
    artifact: string;
  };
  path: string;
}

export interface AgentListData {
  agents: Agent[];
  total: number;
}

export interface AgentDetailData {
  agent: Agent;
  documentation: string;
}

// ─── Pipelines ──────────────────────────────────────────────────────────────

export interface PipelineStep {
  name: string;
  agent: string;
  input: string;
  output: string;
  on_failure: "halt" | "skip" | "loop";
  status: "pending" | "running" | "complete" | "failed" | "skipped";
  loop_target?: string;
  max_iterations?: number;
}

export interface Pipeline {
  name: string;
  version: string;
  description: string;
  trigger: string;
  tags: string[];
  steps: PipelineStep[];
  resumable: boolean;
  path: string;
}

export interface PipelineListData {
  pipelines: Pipeline[];
  total: number;
}

export interface PipelineRunData {
  pipeline: string;
  run_id: string;
  status: "running" | "complete" | "failed" | "paused";
  current_step: number;
  total_steps: number;
  steps: PipelineStep[];
  context_budget: {
    used: number;
    total: number;
    percentage: number;
  };
  artifacts: PipelineArtifact[];
  started_at: string;
  elapsed_seconds: number;
}

export interface PipelineArtifact {
  name: string;
  path: string;
  type: string;
  step: string;
  size_bytes: number;
}

// ─── Bundles ────────────────────────────────────────────────────────────────

export interface Bundle {
  name: string;
  version: string;
  description: string;
  skills: string[];
  installed_skills: string[];
  status: "installed" | "partial" | "not-installed";
  path: string;
}

export interface BundleListData {
  bundles: Bundle[];
  total: number;
}

// ─── Health / Doctor ────────────────────────────────────────────────────────

export interface PlatformHealth {
  name: string;
  id: string;
  status: "healthy" | "degraded" | "error" | "not-installed";
  message: string;
  checks: HealthCheck[];
}

export interface HealthCheck {
  name: string;
  status: "pass" | "warn" | "fail";
  message: string;
  suggestion?: string;
}

export interface DoctorData {
  overall_score: number;
  cli_version: string;
  python_version: string;
  platforms: PlatformHealth[];
  skills_count: number;
  installed_count: number;
  agents_count: number;
  pipelines_count: number;
  issues: HealthCheck[];
}

// ─── Admin / Stats ──────────────────────────────────────────────────────────

export interface AdminData {
  version: string;
  skills_total: number;
  skills_installed: number;
  agents_total: number;
  pipelines_total: number;
  bundles_total: number;
  platforms: string[];
  recent_runs: { pipeline: string; date: string; status: string }[];
}

// ─── Search ─────────────────────────────────────────────────────────────────

export interface SearchResult {
  type: "skill" | "agent" | "pipeline" | "bundle";
  name: string;
  description: string;
  match_score: number;
}

export interface SearchData {
  query: string;
  results: SearchResult[];
  total: number;
}

// ─── Validation ─────────────────────────────────────────────────────────────

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  checked: string[];
}

// ─── Context Budget ─────────────────────────────────────────────────────────

export interface ContextBudgetData {
  used_tokens: number;
  total_tokens: number;
  percentage: number;
  breakdown: {
    component: string;
    tokens: number;
  }[];
}

// ─── Init ───────────────────────────────────────────────────────────────────

export interface InitData {
  platforms_detected: string[];
  config_created: boolean;
  config_path: string;
}

// ─── Update ─────────────────────────────────────────────────────────────────

export interface UpdateData {
  current_version: string;
  latest_version: string;
  update_available: boolean;
  changelog: string;
}
