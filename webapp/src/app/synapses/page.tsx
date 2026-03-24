"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { getAllSynapses } from "@/lib/registry";
import type { Synapse } from "@/lib/types";

const allSynapses = getAllSynapses();

export default function SynapsesPage() {
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    let result: Synapse[] = allSynapses;

    if (search) {
      const q = search.toLowerCase();
      result = result.filter(
        (s) =>
          s.name.toLowerCase().includes(q) ||
          s.description.toLowerCase().includes(q) ||
          s.tags.some((t) => t.toLowerCase().includes(q)),
      );
    }

    return result;
  }, [search]);

  return (
    <div className="px-4 sm:px-6 lg:px-8 py-12">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-brand-text mb-2">
            🧠 Cognitive Synapses
          </h1>
          <p className="text-brand-muted">
            Synapses enhance <strong className="text-brand-text">how</strong>{" "}
            agents think, not what they do. They provide cognitive capabilities
            like metacognition, confidence calibration, and structured
            reflection.
          </p>
        </div>

        {/* Search */}
        <div className="mb-8">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search synapses by name, description, or tags..."
            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-brand-text placeholder:text-brand-muted/50 focus:outline-none focus:border-brand-purple/50 focus:ring-1 focus:ring-brand-purple/30 transition-all"
          />
        </div>

        {/* Results count */}
        <p className="text-sm text-brand-muted mb-4">
          Showing{" "}
          <span className="font-medium text-brand-text">{filtered.length}</span>{" "}
          {filtered.length === 1 ? "synapse" : "synapses"}
        </p>

        {/* Synapses Grid */}
        {filtered.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {filtered.map((synapse) => (
              <Link
                key={synapse.slug}
                href={`/synapses/${synapse.slug}/`}
                className="group bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:border-brand-purple/30 transition-all duration-300"
              >
                <div className="flex items-start justify-between mb-3">
                  <span className="text-2xl">🧠</span>
                  <span
                    className={`text-xs font-bold px-2.5 py-1 rounded-full border ${
                      synapse.synapseType === "core"
                        ? "bg-purple-500/20 text-purple-400 border-purple-500/30"
                        : "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
                    }`}
                  >
                    {synapse.synapseType}
                  </span>
                </div>
                <h3 className="text-base font-semibold text-brand-text mb-1 group-hover:text-white transition-colors font-mono">
                  {synapse.name}
                </h3>
                <p className="text-sm text-brand-muted leading-relaxed mb-3 line-clamp-2">
                  {synapse.description}
                </p>
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {synapse.firingPhases.map((phase) => (
                    <span
                      key={phase.name}
                      className="text-[10px] font-mono px-2 py-0.5 rounded bg-brand-purple/10 text-brand-purple border border-brand-purple/20"
                    >
                      {phase.name}
                    </span>
                  ))}
                </div>
                <div className="flex flex-wrap gap-1">
                  {synapse.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/5 text-brand-muted border border-white/10"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <p className="text-xl text-brand-muted mb-2">No synapses found</p>
            <p className="text-sm text-brand-muted">
              Try adjusting your search.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
