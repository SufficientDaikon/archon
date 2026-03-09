import { Metadata } from "next";
import Link from "next/link";
import { getAllSynapseSlugs, getSynapseBySlug } from "@/lib/registry";

export function generateStaticParams() {
  return getAllSynapseSlugs().map((slug) => ({ slug }));
}

interface Props {
  params: { slug: string };
}

export function generateMetadata({ params }: Props): Metadata {
  const synapse = getSynapseBySlug(params.slug);
  if (!synapse) {
    return { title: "Synapse Not Found" };
  }
  return {
    title: `${synapse.name} — OMNISKILL Synapse`,
    description: synapse.description,
    openGraph: {
      title: `${synapse.name} — OMNISKILL Synapse`,
      description: synapse.description,
      type: "website",
    },
  };
}

export default function SynapseDetailPage({ params }: Props) {
  const synapse = getSynapseBySlug(params.slug);

  if (!synapse) {
    return (
      <div className="px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h1 className="text-2xl font-bold text-brand-text mb-4">
          Synapse Not Found
        </h1>
        <Link
          href="/synapses/"
          className="text-brand-purple hover:text-brand-cyan transition-colors"
        >
          ← Back to Synapses
        </Link>
      </div>
    );
  }

  const timingColors: Record<string, string> = {
    "pre-task": "bg-blue-500/20 text-blue-400 border-blue-500/30",
    active: "bg-green-500/20 text-green-400 border-green-500/30",
    "post-task": "bg-orange-500/20 text-orange-400 border-orange-500/30",
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8 py-12">
      <div className="mx-auto max-w-4xl">
        {/* Breadcrumb */}
        <nav
          className="flex items-center gap-2 text-sm text-brand-muted mb-8"
          aria-label="Breadcrumb"
        >
          <Link href="/" className="hover:text-brand-text transition-colors">
            Home
          </Link>
          <span>/</span>
          <Link
            href="/synapses/"
            className="hover:text-brand-text transition-colors"
          >
            Synapses
          </Link>
          <span>/</span>
          <span className="text-brand-text">{synapse.name}</span>
        </nav>

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-start gap-4 mb-4">
            <span className="text-3xl" role="img" aria-label="Brain">
              🧠
            </span>
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold text-brand-text font-mono">
                {synapse.name}
              </h1>
              <p className="text-brand-muted mt-1">{synapse.description}</p>
            </div>
          </div>

          {/* Metadata badges */}
          <div className="flex flex-wrap gap-2 mb-6">
            <span
              className={`text-xs font-bold px-2.5 py-1 rounded-full border ${
                synapse.synapseType === "core"
                  ? "bg-purple-500/20 text-purple-400 border-purple-500/30"
                  : "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
              }`}
            >
              {synapse.synapseType}
            </span>
            <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-white/5 text-brand-muted border border-white/10">
              v{synapse.version}
            </span>
          </div>

          {/* Tags */}
          {synapse.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-6">
              {synapse.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-[11px] font-mono px-2 py-0.5 rounded bg-white/5 text-brand-muted border border-white/10"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Firing Phases */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 mb-8">
          <h2 className="text-lg font-semibold text-brand-text mb-4">
            Firing Phases
          </h2>
          <div className="space-y-4">
            {synapse.firingPhases.map((phase, i) => (
              <div
                key={phase.name}
                className="bg-white/5 border border-white/10 rounded-lg p-4"
              >
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-sm font-bold text-brand-text">
                    Phase {i + 1}
                  </span>
                  <span className="text-sm font-mono font-bold text-brand-purple">
                    {phase.name}
                  </span>
                  <span
                    className={`text-[10px] font-medium px-2 py-0.5 rounded-full border ${
                      timingColors[phase.timing] ||
                      "bg-white/5 text-brand-muted border-white/10"
                    }`}
                  >
                    {phase.timing}
                  </span>
                </div>
                <p className="text-sm text-brand-muted">{phase.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Agents */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 mb-8">
          <h2 className="text-lg font-semibold text-brand-text mb-3">
            Used by Agents
          </h2>
          {synapse.agents.length > 0 ? (
            <div className="space-y-2">
              {synapse.agents.map((agent) => (
                <Link
                  key={agent}
                  href="/agents/"
                  className="block text-sm text-brand-purple hover:text-brand-cyan transition-colors font-mono"
                >
                  🤖 {agent}
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-sm text-brand-muted">
              Not bound to any agents.
            </p>
          )}
        </div>

        {/* Synapse Content Placeholder */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-brand-text mb-4">
            Synapse Documentation
          </h2>
          <div className="border border-dashed border-white/20 rounded-lg p-8 text-center">
            <p className="text-brand-muted text-sm mb-2">
              Full SYNAPSE.md content will be rendered here at build time.
            </p>
            <a
              href={`https://github.com/SufficientDaikon/omniskill/tree/main/synapses/${synapse.slug}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-brand-purple hover:text-brand-cyan transition-colors"
            >
              View on GitHub ↗
            </a>
          </div>
        </div>

        {/* Back Link */}
        <div className="mt-8">
          <Link
            href="/synapses/"
            className="text-sm text-brand-muted hover:text-brand-text transition-colors"
          >
            ← Back to all synapses
          </Link>
        </div>
      </div>
    </div>
  );
}
