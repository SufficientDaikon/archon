import Link from "next/link";
import InstallCommand from "@/components/InstallCommand";
import { getStats } from "@/lib/registry";

const stats = getStats();

const features = [
  {
    icon: "🧩",
    title: "49 Expert Skills",
    description:
      "From Django ORM to Godot particles, UX research to systematic debugging — deep domain expertise ready to install.",
  },
  {
    icon: "🤖",
    title: "8 Specialized Agents",
    description:
      "Pre-built personas that chain skills into intelligent workflows — spec writing, implementation, review, and more.",
  },
  {
    icon: "🔗",
    title: "5 Automated Pipelines",
    description:
      "Multi-step workflows that orchestrate agents automatically — from idea to shipped feature in one command.",
  },
  {
    icon: "📦",
    title: "8 Curated Bundles",
    description:
      "Opinionated skill packs for Django, Godot, UX design, testing, and more — install everything at once.",
  },
  {
    icon: "🌐",
    title: "5 Platform Adapters",
    description:
      "Write once, use everywhere — Claude Code, Copilot CLI, Cursor, Windsurf, and Antigravity.",
  },
  {
    icon: "🧠",
    title: "Cognitive Synapses",
    description:
      "Enhance HOW agents think — metacognition, confidence calibration, stuck detection, and structured reflection.",
  },
  {
    icon: "📋",
    title: "Spec-Driven Dev (SDD)",
    description:
      "A complete development methodology — spec → implement → review — enforced by the framework itself.",
  },
];

const platforms = [
  { name: "Claude Code", icon: "⚡" },
  { name: "Copilot CLI", icon: "🤖" },
  { name: "Cursor", icon: "🎯" },
  { name: "Windsurf", icon: "🌊" },
  { name: "Antigravity", icon: "🚀" },
];

export default function HomePage() {
  return (
    <div className="relative">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-grid-pattern opacity-50 pointer-events-none" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-gradient-radial pointer-events-none" />

      {/* Hero Section */}
      <section className="relative px-4 sm:px-6 lg:px-8 pt-20 pb-16 sm:pt-28 sm:pb-24">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-4">
            <span className="inline-block text-xs font-mono text-brand-purple border border-brand-purple/30 rounded-full px-3 py-1 bg-brand-purple/10">
              v0.2.0 — Universal Framework
            </span>
          </div>

          <h1 className="text-5xl sm:text-7xl lg:text-8xl font-extrabold tracking-tight mb-6">
            <span className="gradient-text">OMNI</span>
            <span className="text-brand-text">SKILL</span>
          </h1>

          <p className="text-lg sm:text-xl text-brand-muted max-w-2xl mx-auto mb-8 leading-relaxed">
            Universal AI Agent &amp; Skills Framework.{" "}
            <span className="text-brand-text font-medium">
              One repo, one format, every platform.
            </span>
          </p>

          <div className="max-w-md mx-auto mb-10">
            <InstallCommand
              command="pip install omniskill"
              label="Get started in seconds"
            />
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              href="/skills/"
              className="px-6 py-3 bg-gradient-to-r from-brand-purple to-brand-cyan text-white font-semibold rounded-xl hover:opacity-90 transition-opacity text-sm shadow-lg shadow-brand-purple/20"
            >
              Browse Skills →
            </Link>
            <Link
              href="/docs/"
              className="px-6 py-3 bg-white/5 border border-white/10 text-brand-text font-semibold rounded-xl hover:bg-white/10 transition-all text-sm"
            >
              View Docs
            </Link>
            <a
              href="https://github.com/SufficientDaikon/omniskill"
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-3 bg-white/5 border border-white/10 text-brand-text font-semibold rounded-xl hover:bg-white/10 transition-all text-sm"
            >
              GitHub ↗
            </a>
          </div>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="relative px-4 sm:px-6 lg:px-8 py-12 border-y border-white/10 bg-white/[0.02]">
        <div className="mx-auto max-w-5xl">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-6 sm:gap-4">
            {[
              {
                value: stats.skills,
                label: "Skills",
                color: "text-brand-purple",
              },
              {
                value: stats.agents,
                label: "Agents",
                color: "text-brand-cyan",
              },
              {
                value: stats.pipelines,
                label: "Pipelines",
                color: "text-pink-400",
              },
              {
                value: stats.bundles,
                label: "Bundles",
                color: "text-yellow-400",
              },
              {
                value: stats.platforms,
                label: "Platforms",
                color: "text-green-400",
              },
              {
                value: stats.synapses,
                label: "Synapses",
                color: "text-violet-400",
              },
            ].map((stat) => (
              <div key={stat.label} className="text-center">
                <p className={`text-3xl sm:text-4xl font-bold ${stat.color}`}>
                  {stat.value}
                </p>
                <p className="text-xs text-brand-muted mt-1 font-medium uppercase tracking-wider">
                  {stat.label}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="relative px-4 sm:px-6 lg:px-8 py-20">
        <div className="mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-brand-text mb-3">
              Everything You Need
            </h2>
            <p className="text-brand-muted max-w-xl mx-auto">
              A complete framework for supercharging AI-assisted development
              across every platform and domain.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:border-brand-purple/30 transition-all duration-300 group"
              >
                <span
                  className="text-2xl mb-3 block"
                  role="img"
                  aria-label={feature.title}
                >
                  {feature.icon}
                </span>
                <h3 className="text-base font-semibold text-brand-text mb-2 group-hover:text-white transition-colors">
                  {feature.title}
                </h3>
                <p className="text-sm text-brand-muted leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Platforms Section */}
      <section className="relative px-4 sm:px-6 lg:px-8 py-16 border-t border-white/10 bg-white/[0.02]">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="text-2xl sm:text-3xl font-bold text-brand-text mb-3">
            One Framework, Every Platform
          </h2>
          <p className="text-brand-muted mb-10 max-w-lg mx-auto">
            Write skills once and deploy them anywhere. OMNISKILL adapts to your
            IDE of choice.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            {platforms.map((p) => (
              <div
                key={p.name}
                className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-xl px-5 py-3 hover:border-brand-purple/30 transition-all"
              >
                <span className="text-xl" role="img" aria-label={p.name}>
                  {p.icon}
                </span>
                <span className="text-sm font-medium text-brand-text">
                  {p.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative px-4 sm:px-6 lg:px-8 py-20">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-brand-text mb-4">
            Ready to Level Up?
          </h2>
          <p className="text-brand-muted mb-8 max-w-lg mx-auto">
            Install OMNISKILL and start using expert AI skills in seconds. No
            config, no friction.
          </p>
          <div className="max-w-md mx-auto mb-8">
            <InstallCommand command="pip install omniskill" />
          </div>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              href="/skills/"
              className="px-8 py-3.5 bg-gradient-to-r from-brand-purple to-brand-cyan text-white font-semibold rounded-xl hover:opacity-90 transition-opacity text-sm shadow-lg shadow-brand-purple/20"
            >
              Explore All 49 Skills →
            </Link>
            <Link
              href="/bundles/"
              className="px-8 py-3.5 bg-white/5 border border-white/10 text-brand-text font-semibold rounded-xl hover:bg-white/10 transition-all text-sm"
            >
              Browse Bundles
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
