// ============================================================
// Archon Registry — Data Access Layer
// ============================================================
import registryData from "@/data/registry.json";
import type {
  Registry,
  Skill,
  Agent,
  Pipeline,
  Bundle,
  Platform,
  Synapse,
  SkillCategory,
} from "./types";

const registry = registryData as unknown as Registry;

// --- Skills ---
export function getAllSkills(): Skill[] {
  return registry.skills;
}

export function getSkillBySlug(slug: string): Skill | undefined {
  return registry.skills.find((s) => s.slug === slug);
}

export function getSkillsByCategory(category: SkillCategory): Skill[] {
  return registry.skills.filter((s) => s.category === category);
}

export function searchSkills(query: string): Skill[] {
  const q = query.toLowerCase();
  return registry.skills.filter(
    (s) =>
      s.name.toLowerCase().includes(q) ||
      s.description.toLowerCase().includes(q) ||
      s.tags.some((t) => t.toLowerCase().includes(q)),
  );
}

export function getSkillCategories(): SkillCategory[] {
  return [
    "Django",
    "Godot",
    "UX/Design",
    "Testing",
    "SDD",
    "Meta",
    "Development",
  ];
}

export function getAllSkillSlugs(): string[] {
  return registry.skills.map((s) => s.slug);
}

// --- Agents ---
export function getAllAgents(): Agent[] {
  return registry.agents;
}

export function getAgentBySlug(slug: string): Agent | undefined {
  return registry.agents.find((a) => a.slug === slug);
}

// --- Pipelines ---
export function getAllPipelines(): Pipeline[] {
  return registry.pipelines;
}

export function getPipelineBySlug(slug: string): Pipeline | undefined {
  return registry.pipelines.find((p) => p.slug === slug);
}

// --- Bundles ---
export function getAllBundles(): Bundle[] {
  return registry.bundles;
}

export function getBundleBySlug(slug: string): Bundle | undefined {
  return registry.bundles.find((b) => b.slug === slug);
}

// --- Synapses ---
export function getAllSynapses(): Synapse[] {
  return registry.synapses || [];
}

export function getSynapseBySlug(slug: string): Synapse | undefined {
  return (registry.synapses || []).find((s) => s.slug === slug);
}

export function getAllSynapseSlugs(): string[] {
  return (registry.synapses || []).map((s) => s.slug);
}

export function getSynapseCategories(): string[] {
  const types = new Set((registry.synapses || []).map((s) => s.synapseType));
  return Array.from(types);
}

// --- Platforms ---
export function getAllPlatforms(): Platform[] {
  return registry.platforms;
}

// --- Stats ---
export function getStats() {
  return registry.stats;
}

// --- Meta ---
export function getMeta() {
  return registry.meta;
}

// --- Helpers ---
export function getCategoryColor(category: string): string {
  const colors: Record<string, string> = {
    Django: "bg-green-500/20 text-green-400 border-green-500/30",
    Godot: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    "UX/Design": "bg-pink-500/20 text-pink-400 border-pink-500/30",
    Testing: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    SDD: "bg-purple-500/20 text-purple-400 border-purple-500/30",
    Meta: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
    Development: "bg-orange-500/20 text-orange-400 border-orange-500/30",
  };
  return colors[category] || "bg-gray-500/20 text-gray-400 border-gray-500/30";
}

export function getPriorityColor(priority: string): string {
  const colors: Record<string, string> = {
    P0: "bg-red-500/20 text-red-400 border-red-500/30",
    P1: "bg-orange-500/20 text-orange-400 border-orange-500/30",
    P2: "bg-slate-500/20 text-slate-400 border-slate-500/30",
    P3: "bg-slate-700/20 text-slate-500 border-slate-700/30",
  };
  return (
    colors[priority] || "bg-slate-500/20 text-slate-400 border-slate-500/30"
  );
}

export function getCategoryEmoji(category: string): string {
  const emojis: Record<string, string> = {
    Django: "🐍",
    Godot: "🎮",
    "UX/Design": "🎨",
    Testing: "🧪",
    SDD: "📋",
    Meta: "⚙️",
    Development: "💻",
  };
  return emojis[category] || "📦";
}
