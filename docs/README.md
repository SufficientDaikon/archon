# Archon Documentation

Comprehensive documentation for Archon v2.0 — the Universal AI Agent & Skills Framework.

## 📚 Documentation Pages

### Getting Started
- **[Getting Started](getting-started.md)** — Installation, setup, and your first skill

### Creating Components
- **[Creating Skills](creating-skills.md)** — Deep dive into skill authoring
- **[Creating Bundles](creating-bundles.md)** — Group skills into domain kits
- **[Creating Agents](creating-agents.md)** — Define formal agent personas with enforced guardrails
- **[Creating Pipelines](creating-pipelines.md)** — Build multi-agent workflows with real execution
- **[Creating Synapses](creating-synapses.md)** — Custom cognitive capabilities

### v2.0 Guides
- **[Architecture](architecture.md)** — 5-Layer architecture, data flow, validation
- **[Guardrails](guardrails.md)** — Guardrails engine, Iron Laws, deviation protocol
- **[Sequential Thinking](sequential-thinking.md)** — Chain-of-thought protocol, decomposition patterns
- **[Pipeline Orchestration](pipeline-orchestration.md)** — Real execution engine, state persistence, context curation
- **[Migration Guide (v2.0)](migration-v2.md)** — Upgrading from v0.x to v2.0

### Reference
- **[Platform Guide](platform-guide.md)** — Claude Code, Copilot, Cursor, Windsurf, Antigravity
- **[CLI Guide](cli-guide.md)** — Full CLI command reference
- **[Agent Cards](agent-cards.md)** — Machine-readable agent metadata
- **[MCP Integration Catalog](integration-catalog.md)** — 20 curated MCP servers
- **[FAQ](faq.md)** — Frequently asked questions

## 🎨 Design

The documentation uses the same stunning design system as the main Archon page:

- **Dark theme** with glassmorphism effects
- **Gradient accents** (blue → cyan → purple)
- **Inter + JetBrains Mono** fonts from Google Fonts
- **Smooth animations** and scroll effects
- **Responsive design** — works on mobile, tablet, and desktop
- **Left sidebar navigation** with all doc pages
- **Beautiful code blocks** with syntax-like styling
- **Interactive elements** — FAQ accordions, hover effects

## 🚀 Quick Start

1. Open any `.html` file in a browser
2. Navigate using the left sidebar
3. Use breadcrumbs to track your location
4. Enjoy the beautiful, readable documentation!

## 🔧 Customization

All styles are in `styles.css`. To customize:

- **Colors**: Edit CSS variables in `:root`
- **Fonts**: Change Google Fonts import in each HTML file
- **Layout**: Adjust `.doc-content`, `.sidebar`, etc.
- **Components**: Modify `.content-section`, `.code-block`, etc.

## 📝 Content Sources

Documentation content is derived from the markdown files in this directory:

- `getting-started.md` → `getting-started.html`
- `creating-skills.md` → `creating-skills.html`
- (and so on for all pages)

## ✨ Features

- ✓ Glassmorphism sidebar with blur effects
- ✓ Terminal-style code blocks with green prompts
- ✓ Step indicators with numbered circles
- ✓ File tree visualization
- ✓ Alert boxes (info, success, warning)
- ✓ Beautiful tables with hover effects
- ✓ Platform cards with icons
- ✓ Architecture diagrams with gradient layers
- ✓ FAQ accordion with smooth animations
- ✓ Previous/Next navigation at bottom
- ✓ Breadcrumb navigation
- ✓ Mobile-responsive sidebar toggle

## 🌐 Live Preview

To preview locally, just open any HTML file in your browser. No server needed!

For a live server with hot reload:

```bash
# Python
python -m http.server 8000

# Node.js
npx serve

# VS Code Live Server extension
# Right-click HTML file → Open with Live Server
```

Then visit: `http://localhost:8000/getting-started.html`

## 📦 Building HTML Documentation

The HTML documentation is auto-generated from the Markdown files in this directory using `scripts/build_docs.py`:

```bash
python scripts/build_docs.py
```

This generates styled HTML files in `docs/html/` with:

- Dark GitHub-inspired theme
- Mermaid.js diagram rendering (ASCII art is auto-converted to Mermaid)
- Sidebar navigation across all pages
- Responsive mobile-friendly layout

Output: `docs/html/` directory with one HTML file per Markdown doc.

### Deploying

The HTML files are static — deploy them to:

- GitHub Pages (recommended: serve from `docs/html/`)
- Netlify
- Vercel
- Any static hosting service

## 🎯 Design Inspiration

This documentation is designed to be screenshot-worthy. The aesthetic matches high-end SaaS documentation with:

- Modern glassmorphism
- Smooth gradient accents
- Thoughtful typography
- Delightful micro-interactions
- Professional color palette

Perfect for showcasing Archon's design excellence!
