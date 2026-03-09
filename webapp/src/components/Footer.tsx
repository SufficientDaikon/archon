import Link from "next/link";

export default function Footer() {
  return (
    <footer className="border-t border-white/10 bg-brand-bg" role="contentinfo">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="sm:col-span-2 lg:col-span-1">
            <Link
              href="/"
              className="text-xl font-bold bg-gradient-to-r from-brand-purple to-brand-cyan bg-clip-text text-transparent"
            >
              OMNISKILL
            </Link>
            <p className="mt-2 text-sm text-brand-muted leading-relaxed">
              Universal AI Agent &amp; Skills Framework.
              <br />
              One repo, one format, every platform.
            </p>
          </div>

          {/* Explore */}
          <div>
            <h3 className="text-sm font-semibold text-brand-text mb-3">
              Explore
            </h3>
            <ul className="space-y-2">
              {[
                { href: "/skills/", label: "Skills Marketplace" },
                { href: "/agents/", label: "Agent Directory" },
                { href: "/pipelines/", label: "Pipeline Gallery" },
                { href: "/bundles/", label: "Bundle Showcase" },
              ].map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-brand-muted hover:text-brand-text transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-sm font-semibold text-brand-text mb-3">
              Resources
            </h3>
            <ul className="space-y-2">
              {[
                { href: "/docs/", label: "Documentation" },
                {
                  href: "https://github.com/SufficientDaikon/omniskill",
                  label: "GitHub",
                  external: true,
                },
                {
                  href: "https://github.com/SufficientDaikon/omniskill/blob/main/CONTRIBUTING.md",
                  label: "Contributing",
                  external: true,
                },
                {
                  href: "https://github.com/SufficientDaikon/omniskill/blob/main/CHANGELOG.md",
                  label: "Changelog",
                  external: true,
                },
              ].map((link) => (
                <li key={link.href}>
                  {"external" in link ? (
                    <a
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-brand-muted hover:text-brand-text transition-colors"
                    >
                      {link.label} ↗
                    </a>
                  ) : (
                    <Link
                      href={link.href}
                      className="text-sm text-brand-muted hover:text-brand-text transition-colors"
                    >
                      {link.label}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>

          {/* Platforms */}
          <div>
            <h3 className="text-sm font-semibold text-brand-text mb-3">
              Platforms
            </h3>
            <ul className="space-y-2">
              {[
                "Claude Code",
                "Copilot CLI",
                "Cursor",
                "Windsurf",
                "Antigravity",
              ].map((p) => (
                <li key={p} className="text-sm text-brand-muted">
                  {p}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-white/10 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-xs text-brand-muted">
            © {new Date().getFullYear()} OMNISKILL. MIT License.
          </p>
          <p className="text-xs text-brand-muted">
            Built with Next.js &amp; Tailwind CSS
          </p>
        </div>
      </div>
    </footer>
  );
}
