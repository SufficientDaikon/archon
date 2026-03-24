import Link from "next/link";
import { getCategoryColor, getPriorityColor } from "@/lib/registry";
import type { Skill } from "@/lib/types";

interface SkillCardProps {
  skill: Skill;
}

export default function SkillCard({ skill }: SkillCardProps) {
  return (
    <Link
      href={`/skills/${skill.slug}/`}
      className="group block bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-5 hover:border-brand-purple/40 hover:bg-white/[0.07] transition-all duration-300 hover:shadow-lg hover:shadow-brand-purple/5"
    >
      <div className="flex items-start justify-between gap-2 mb-3">
        <h3 className="text-sm font-semibold text-brand-text group-hover:text-white transition-colors font-mono truncate">
          {skill.name}
        </h3>
        <span
          className={`shrink-0 text-[10px] font-bold px-1.5 py-0.5 rounded border ${getPriorityColor(skill.priority)}`}
        >
          {skill.priority}
        </span>
      </div>

      <p className="text-xs text-brand-muted leading-relaxed mb-4 line-clamp-2">
        {skill.description}
      </p>

      <div className="flex items-center justify-between gap-2">
        <span
          className={`text-[10px] font-medium px-2 py-0.5 rounded-full border ${getCategoryColor(skill.category)}`}
        >
          {skill.category}
        </span>
        <div
          className="flex gap-1"
          aria-label={`Supports ${skill.platforms.length} platforms`}
        >
          {skill.platforms.slice(0, 5).map((p) => (
            <span
              key={p}
              className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-brand-purple to-brand-cyan"
              title={p}
            />
          ))}
        </div>
      </div>
    </Link>
  );
}
