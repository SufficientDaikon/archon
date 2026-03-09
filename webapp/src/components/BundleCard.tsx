"use client";

import { useState } from "react";
import InstallCommand from "./InstallCommand";
import type { Bundle } from "@/lib/types";

interface BundleCardProps {
  bundle: Bundle;
}

export default function BundleCard({ bundle }: BundleCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:border-brand-purple/40 hover:bg-white/[0.07] transition-all duration-300">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <h3 className="text-base font-semibold text-brand-text">
            {bundle.name}
          </h3>
          <p className="text-xs text-brand-muted mt-0.5">
            <span className="font-medium text-brand-purple">
              {bundle.skillCount}
            </span>{" "}
            {bundle.skillCount === 1 ? "skill" : "skills"}
          </p>
        </div>
        <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-white/5 text-brand-muted border border-white/10 shrink-0">
          {bundle.category}
        </span>
      </div>

      <p className="text-sm text-brand-muted leading-relaxed mb-4">
        {bundle.description}
      </p>

      {/* Expandable skill list */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1 text-xs text-brand-purple hover:text-brand-cyan transition-colors mb-3"
        aria-expanded={expanded}
      >
        <svg
          className={`w-3 h-3 transition-transform ${expanded ? "rotate-90" : ""}`}
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
        {expanded ? "Hide" : "Show"} included skills
      </button>

      {expanded && (
        <div className="mb-4 animate-fade-in">
          <div className="flex flex-wrap gap-1.5">
            {bundle.skills.map((skill) => (
              <a
                key={skill}
                href={`/skills/${skill}/`}
                className="text-[11px] font-mono px-2 py-1 rounded bg-white/5 text-brand-text border border-white/10 hover:border-brand-purple/40 hover:text-brand-purple transition-all"
              >
                {skill}
              </a>
            ))}
          </div>
        </div>
      )}

      <InstallCommand
        command={`omniskill install-bundle ${bundle.slug}`}
        compact
      />
    </div>
  );
}
