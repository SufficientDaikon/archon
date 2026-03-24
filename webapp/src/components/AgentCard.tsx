import type { Agent } from "@/lib/types";

interface AgentCardProps {
  agent: Agent;
}

export default function AgentCard({ agent }: AgentCardProps) {
  return (
    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:border-brand-purple/40 hover:bg-white/[0.07] transition-all duration-300 hover:shadow-lg hover:shadow-brand-purple/5 group">
      <div className="flex items-start gap-4 mb-4">
        <span className="text-3xl" role="img" aria-label={agent.role}>
          {agent.emoji}
        </span>
        <div className="min-w-0">
          <h3 className="text-base font-semibold text-brand-text group-hover:text-white transition-colors">
            {agent.name}
          </h3>
          <p className="text-xs font-medium text-brand-purple mt-0.5">
            {agent.role}
          </p>
        </div>
      </div>

      <p className="text-sm text-brand-muted leading-relaxed mb-4">
        {agent.persona}
      </p>

      <div className="border-t border-white/10 pt-3 mt-auto">
        <div className="flex items-center justify-between">
          <span className="text-xs text-brand-muted">
            <span className="font-medium text-brand-text">
              {agent.skills.length}
            </span>{" "}
            {agent.skills.length === 1 ? "skill" : "skills"} bound
          </span>
          <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-white/5 text-brand-muted border border-white/10">
            {agent.workflowPhase}
          </span>
        </div>
        <div className="flex flex-wrap gap-1 mt-2">
          {agent.skills.map((skill) => (
            <span
              key={skill}
              className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-brand-purple/10 text-brand-purple border border-brand-purple/20"
            >
              {skill}
            </span>
          ))}
        </div>
      </div>

      <blockquote className="mt-4 text-[11px] text-brand-muted/70 italic border-l-2 border-brand-purple/30 pl-3">
        &ldquo;{agent.philosophy}&rdquo;
      </blockquote>
    </div>
  );
}
