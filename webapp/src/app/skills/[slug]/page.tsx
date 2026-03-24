import { Metadata } from "next";
import Link from "next/link";
import InstallCommand from "@/components/InstallCommand";
import {
  getAllSkillSlugs,
  getSkillBySlug,
  getCategoryColor,
  getPriorityColor,
  getCategoryEmoji,
  getAllPlatforms,
} from "@/lib/registry";

export function generateStaticParams() {
  return getAllSkillSlugs().map((slug) => ({ slug }));
}

interface Props {
  params: { slug: string };
}

export function generateMetadata({ params }: Props): Metadata {
  const skill = getSkillBySlug(params.slug);
  if (!skill) {
    return { title: "Skill Not Found" };
  }
  return {
    title: `${skill.name} — Archon Skill`,
    description: skill.description,
    openGraph: {
      title: `${skill.name} — Archon Skill`,
      description: skill.description,
      type: "website",
    },
  };
}

export default function SkillDetailPage({ params }: Props) {
  const skill = getSkillBySlug(params.slug);
  const platforms = getAllPlatforms();

  if (!skill) {
    return (
      <div className="px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h1 className="text-2xl font-bold text-brand-text mb-4">
          Skill Not Found
        </h1>
        <Link
          href="/skills/"
          className="text-brand-purple hover:text-brand-cyan transition-colors"
        >
          ← Back to Skills
        </Link>
      </div>
    );
  }

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
            href="/skills/"
            className="hover:text-brand-text transition-colors"
          >
            Skills
          </Link>
          <span>/</span>
          <span className="text-brand-text">{skill.name}</span>
        </nav>

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-start gap-4 mb-4">
            <span className="text-3xl" role="img" aria-label={skill.category}>
              {getCategoryEmoji(skill.category)}
            </span>
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold text-brand-text font-mono">
                {skill.name}
              </h1>
              <p className="text-brand-muted mt-1">{skill.description}</p>
            </div>
          </div>

          {/* Metadata badges */}
          <div className="flex flex-wrap gap-2 mb-6">
            <span
              className={`text-xs font-medium px-2.5 py-1 rounded-full border ${getCategoryColor(skill.category)}`}
            >
              {skill.category}
            </span>
            <span
              className={`text-xs font-bold px-2.5 py-1 rounded-full border ${getPriorityColor(skill.priority)}`}
            >
              {skill.priority}
            </span>
            <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-white/5 text-brand-muted border border-white/10">
              v{skill.version}
            </span>
          </div>

          {/* Tags */}
          {skill.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-6">
              {skill.tags.map((tag) => (
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

        {/* Install Command Generator */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 mb-8">
          <h2 className="text-lg font-semibold text-brand-text mb-4">
            Install this skill
          </h2>
          <div className="space-y-3">
            {platforms.map((platform) => (
              <div key={platform.id} className="flex items-center gap-3">
                <span className="text-lg shrink-0" title={platform.name}>
                  {platform.icon}
                </span>
                <div className="flex-1 min-w-0">
                  <InstallCommand
                    command={`archon install ${skill.slug} --platform ${platform.id}`}
                    compact
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Platform Compatibility */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 mb-8">
          <h2 className="text-lg font-semibold text-brand-text mb-4">
            Platform Compatibility
          </h2>
          <div className="flex flex-wrap gap-3">
            {platforms.map((platform) => {
              const supported = skill.platforms.includes(platform.id);
              return (
                <div
                  key={platform.id}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${
                    supported
                      ? "bg-green-500/10 border-green-500/20 text-green-400"
                      : "bg-white/5 border-white/10 text-brand-muted opacity-40"
                  }`}
                >
                  <span className="text-lg">{platform.icon}</span>
                  <span className="text-xs font-medium">{platform.name}</span>
                  {supported && (
                    <svg
                      className="w-3 h-3"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Bundles & Pipelines */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
          {/* Bundles */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-brand-text mb-3">
              Part of Bundles
            </h2>
            {skill.bundles.length > 0 ? (
              <div className="space-y-2">
                {skill.bundles.map((b) => (
                  <Link
                    key={b}
                    href="/bundles/"
                    className="block text-sm text-brand-purple hover:text-brand-cyan transition-colors font-mono"
                  >
                    📦 {b}
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-sm text-brand-muted">
                Not included in any bundles.
              </p>
            )}
          </div>

          {/* Pipelines */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-brand-text mb-3">
              Used in Pipelines
            </h2>
            {skill.pipelines.length > 0 ? (
              <div className="space-y-2">
                {skill.pipelines.map((p) => (
                  <Link
                    key={p}
                    href="/pipelines/"
                    className="block text-sm text-brand-purple hover:text-brand-cyan transition-colors font-mono"
                  >
                    🔗 {p}
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-sm text-brand-muted">
                Not used in any pipelines directly.
              </p>
            )}
          </div>
        </div>

        {/* Skill Content Placeholder */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-brand-text mb-4">
            Skill Documentation
          </h2>
          <div className="border border-dashed border-white/20 rounded-lg p-8 text-center">
            <p className="text-brand-muted text-sm mb-2">
              Full SKILL.md content will be rendered here at build time.
            </p>
            <a
              href={`https://github.com/SufficientDaikon/archon/tree/main/skills/${skill.slug}`}
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
            href="/skills/"
            className="text-sm text-brand-muted hover:text-brand-text transition-colors"
          >
            ← Back to all skills
          </Link>
        </div>
      </div>
    </div>
  );
}
