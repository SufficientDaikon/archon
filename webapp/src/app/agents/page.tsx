import { Metadata } from "next";
import AgentCard from "@/components/AgentCard";
import { getAllAgents } from "@/lib/registry";

export const metadata: Metadata = {
  title: "Agent Directory",
  description:
    "Explore 8 specialized AI agents — pre-built personas with deep skill bindings for complete workflows.",
  openGraph: {
    title: "Agent Directory — OMNISKILL",
    description: "Explore 8 specialized AI agents with deep skill bindings.",
  },
};

export default function AgentsPage() {
  const agents = getAllAgents();

  return (
    <div className="px-4 sm:px-6 lg:px-8 py-12">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold text-brand-text mb-2">
            Agent Directory
          </h1>
          <p className="text-brand-muted max-w-2xl">
            {agents.length} specialized AI agents — pre-built personas that
            chain skills into intelligent, multi-step workflows. Each agent has
            a distinct role, philosophy, and bound skillset.
          </p>
        </div>

        {/* Agent Flow Overview */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 mb-10">
          <h2 className="text-sm font-semibold text-brand-text mb-4">
            Typical Agent Flow
          </h2>
          <div className="flex flex-wrap items-center gap-2 text-sm">
            {[
              { emoji: "🔬", label: "Research" },
              { emoji: "📝", label: "Specify" },
              { emoji: "🎨", label: "Design" },
              { emoji: "🔨", label: "Implement" },
              { emoji: "🧪", label: "Test" },
              { emoji: "📋", label: "Review" },
              { emoji: "🧹", label: "Curate" },
            ].map((step, i) => (
              <div key={step.label} className="flex items-center gap-2">
                <div className="flex items-center gap-1.5 bg-white/5 border border-white/10 rounded-lg px-3 py-1.5">
                  <span>{step.emoji}</span>
                  <span className="text-brand-text font-medium text-xs">
                    {step.label}
                  </span>
                </div>
                {i < 6 && (
                  <svg
                    className="w-3 h-3 text-brand-muted shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Agents Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {agents.map((agent) => (
            <AgentCard key={agent.slug} agent={agent} />
          ))}
        </div>
      </div>
    </div>
  );
}
