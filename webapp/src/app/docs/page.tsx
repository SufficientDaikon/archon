import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Documentation",
  description:
    "Learn how to use Archon — getting started guides, skill creation, architecture, and more.",
  openGraph: {
    title: "Documentation — Archon",
    description: "Comprehensive documentation for the Archon framework.",
  },
};

const docSections = [
  {
    title: "Getting Started",
    description:
      "Install Archon, configure your platform, and run your first skill in minutes.",
    icon: "🚀",
    href: "https://github.com/SufficientDaikon/archon#readme",
  },
  {
    title: "Creating Skills",
    description:
      "Learn the Archon skill format — manifest.yaml, SKILL.md, resources, examples, and tests.",
    icon: "🧩",
    href: "https://github.com/SufficientDaikon/archon/blob/main/docs/creating-skills.md",
  },
  {
    title: "Building Agents",
    description:
      "Create specialized agent personas with role definitions, skill bindings, and workflow phases.",
    icon: "🤖",
    href: "https://github.com/SufficientDaikon/archon/blob/main/docs/building-agents.md",
  },
  {
    title: "Pipeline Architecture",
    description:
      "Understand multi-step pipeline orchestration, triggers, context curation, and failure handling.",
    icon: "🔗",
    href: "https://github.com/SufficientDaikon/archon/blob/main/docs/pipelines.md",
  },
  {
    title: "Platform Adapters",
    description:
      "How Archon adapts skills to Claude Code, Copilot CLI, Cursor, Windsurf, and Antigravity.",
    icon: "🌐",
    href: "https://github.com/SufficientDaikon/archon/blob/main/docs/adapters.md",
  },
  {
    title: "Spec-Driven Development",
    description:
      "The SDD methodology — spec → implement → review — enforced by the framework.",
    icon: "📋",
    href: "https://github.com/SufficientDaikon/archon/blob/main/docs/sdd.md",
  },
  {
    title: "Contributing",
    description:
      "How to contribute skills, agents, adapters, and improvements to Archon.",
    icon: "🤝",
    href: "https://github.com/SufficientDaikon/archon/blob/main/CONTRIBUTING.md",
  },
  {
    title: "Architecture Overview",
    description:
      "Deep dive into Archon's internal architecture — manifests, routing, and the skill lifecycle.",
    icon: "🏗️",
    href: "https://github.com/SufficientDaikon/archon/blob/main/docs/architecture.md",
  },
  {
    title: "Changelog",
    description:
      "Track all changes, additions, and improvements across Archon versions.",
    icon: "📝",
    href: "https://github.com/SufficientDaikon/archon/blob/main/CHANGELOG.md",
  },
];

export default function DocsPage() {
  return (
    <div className="px-4 sm:px-6 lg:px-8 py-12">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold text-brand-text mb-2">
            Documentation
          </h1>
          <p className="text-brand-muted max-w-2xl">
            Everything you need to know about using, creating, and extending the
            Archon framework.
          </p>
        </div>

        {/* Quick Start Banner */}
        <div className="bg-gradient-to-r from-brand-purple/20 to-brand-cyan/20 border border-brand-purple/30 rounded-xl p-6 mb-10">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
            <span className="text-3xl">⚡</span>
            <div className="flex-1">
              <h2 className="text-base font-semibold text-brand-text mb-1">
                Quick Start
              </h2>
              <p className="text-sm text-brand-muted">
                Install Archon and get your first skill running in under 2
                minutes.
              </p>
            </div>
            <code className="text-sm font-mono text-brand-cyan bg-black/30 px-4 py-2 rounded-lg border border-white/10">
              pip install archon
            </code>
          </div>
        </div>

        {/* Doc Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {docSections.map((section) => (
            <a
              key={section.title}
              href={section.href}
              target="_blank"
              rel="noopener noreferrer"
              className="group bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:border-brand-purple/40 hover:bg-white/[0.07] transition-all duration-300"
            >
              <span
                className="text-2xl mb-3 block"
                role="img"
                aria-label={section.title}
              >
                {section.icon}
              </span>
              <h3 className="text-base font-semibold text-brand-text mb-2 group-hover:text-white transition-colors">
                {section.title}
              </h3>
              <p className="text-sm text-brand-muted leading-relaxed">
                {section.description}
              </p>
              <span className="inline-block mt-3 text-xs text-brand-purple group-hover:text-brand-cyan transition-colors">
                Read on GitHub ↗
              </span>
            </a>
          ))}
        </div>

        {/* Links */}
        <div className="mt-12 text-center">
          <p className="text-sm text-brand-muted mb-4">
            Looking for something specific? Browse the full repository.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <a
              href="https://github.com/SufficientDaikon/archon"
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-2.5 bg-white/5 border border-white/10 text-brand-text font-medium rounded-xl hover:bg-white/10 transition-all text-sm"
            >
              View Repository ↗
            </a>
            <Link
              href="/skills/"
              className="px-6 py-2.5 bg-white/5 border border-white/10 text-brand-text font-medium rounded-xl hover:bg-white/10 transition-all text-sm"
            >
              Browse Skills →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
