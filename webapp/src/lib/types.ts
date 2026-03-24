// ============================================================
// Archon Web App — TypeScript Interfaces
// ============================================================

export interface Skill {
  name: string;
  slug: string;
  description: string;
  category: SkillCategory;
  tags: string[];
  priority: "P0" | "P1" | "P2" | "P3";
  platforms: string[];
  version: string;
  bundles: string[]; // bundle names this skill belongs to
  pipelines: string[]; // pipeline names this skill is used in (via agents)
}

export type SkillCategory =
  | "Django"
  | "Godot"
  | "UX/Design"
  | "Testing"
  | "SDD"
  | "Meta"
  | "Development";

export interface Agent {
  name: string;
  slug: string;
  role: string;
  emoji: string;
  persona: string;
  skills: string[];
  philosophy: string;
  workflowPhase: string;
}

export interface PipelineStep {
  name: string;
  agent: string;
  description: string;
}

export interface Pipeline {
  name: string;
  slug: string;
  description: string;
  trigger: string;
  steps: PipelineStep[];
  version: string;
}

export interface Bundle {
  name: string;
  slug: string;
  description: string;
  skills: string[];
  skillCount: number;
  category: string;
}

export interface Platform {
  id: string;
  name: string;
  icon: string;
  target: string;
}

export interface SynapsePhase {
  name: string;
  timing: "pre-task" | "active" | "post-task";
  description: string;
}

export interface Synapse {
  name: string;
  slug: string;
  description: string;
  synapseType: "core" | "optional";
  version: string;
  tags: string[];
  firingPhases: SynapsePhase[];
  agents: string[]; // agents that use this synapse
}

export interface Registry {
  meta: {
    name: string;
    version: string;
    description: string;
    repository: string;
  };
  skills: Skill[];
  agents: Agent[];
  pipelines: Pipeline[];
  bundles: Bundle[];
  platforms: Platform[];
  synapses: Synapse[];
  stats: {
    skills: number;
    agents: number;
    pipelines: number;
    bundles: number;
    platforms: number;
    synapses: number;
  };
}
