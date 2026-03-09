# OMNISKILL Web App

![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)
![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178c6?logo=typescript)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06b6d4?logo=tailwindcss)
![Static Pages](https://img.shields.io/badge/Pages-58_static-8b5cf6)
![License](https://img.shields.io/badge/License-MIT-green)

The public-facing website for **OMNISKILL** — a universal AI agent & skills framework. Browse, search, and explore 49 skills, 8 agents, 5 pipelines, and 8 bundles across 5 platforms, all from a fast, statically-exported Next.js site.

---

## Features

- **Landing Page** — Hero section, animated stats bar (49 skills · 8 agents · 5 pipelines · 8 bundles · 5 platforms), feature grid, platform showcase, and call-to-action
- **Skill Marketplace** — Browse, search, and filter all 49 skills by category with real-time client-side filtering
- **Skill Detail Pages** — 49 individual pages with metadata (category, priority, version, tags), install commands for every platform, and related bundles/pipelines
- **Agent Directory** — 8 specialized agents displayed with roles, personas, philosophies, and a visual workflow-phase diagram
- **Pipeline Gallery** — 5 pipelines with step-by-step orchestration flow visualizations
- **Bundle Showcase** — 8 curated skill bundles with descriptions and expandable skill lists
- **Documentation Hub** — Quick-start guide and links to all documentation topics on GitHub

---

## Tech Stack

| Layer     | Technology                                    |
| --------- | --------------------------------------------- |
| Framework | **Next.js 14** (App Router)                   |
| Language  | **TypeScript 5.4** (strict mode)              |
| Styling   | **Tailwind CSS 3.4** + custom theme           |
| Fonts     | **Inter** (UI) + **JetBrains Mono** (code)    |
| Output    | **Static Export** (`next build` → `out/`)     |
| Data      | JSON registry extracted from `omniskill.yaml` |

---

## Getting Started

```bash
cd webapp
npm install
npm run dev      # Development server at localhost:3000
npm run build    # Production build (58 static pages)
npm run start    # Serve production build locally
npm run lint     # Run Next.js linter
```

---

## Project Structure

```
webapp/
├── src/
│   ├── app/                        # Next.js 14 App Router
│   │   ├── layout.tsx              # Root layout (Navbar, Footer, metadata)
│   │   ├── page.tsx                # Landing page
│   │   ├── globals.css             # Global styles & Tailwind directives
│   │   ├── agents/page.tsx         # Agent directory
│   │   ├── bundles/page.tsx        # Bundle showcase
│   │   ├── docs/page.tsx           # Documentation hub
│   │   ├── pipelines/page.tsx      # Pipeline gallery
│   │   ├── skills/page.tsx         # Skills marketplace (client component)
│   │   └── skills/[slug]/page.tsx  # Dynamic skill detail pages
│   ├── components/                 # Reusable React components
│   │   ├── AgentCard.tsx
│   │   ├── BundleCard.tsx
│   │   ├── CategoryFilter.tsx
│   │   ├── Footer.tsx
│   │   ├── InstallCommand.tsx
│   │   ├── Navbar.tsx
│   │   ├── PipelineFlow.tsx
│   │   ├── SearchBar.tsx
│   │   └── SkillCard.tsx
│   ├── data/
│   │   └── registry.json           # Central data source (all skills, agents, etc.)
│   └── lib/
│       ├── registry.ts             # Data access functions
│       └── types.ts                # TypeScript interfaces
├── public/
│   └── favicon.svg
├── next.config.js                  # Static export + trailing slash config
├── tailwind.config.js              # Custom dark theme + animations
├── tsconfig.json                   # Strict TypeScript, path aliases (@/*)
├── postcss.config.js
└── package.json
```

---

## Design System

| Token            | Value                                                       |
| ---------------- | ----------------------------------------------------------- |
| Background       | `#06060e` (near-black)                                      |
| Background Light | `#0a0a1a`                                                   |
| Primary Accent   | `#8b5cf6` (purple)                                          |
| Secondary Accent | `#06b6d4` (cyan)                                            |
| Gradient         | `linear-gradient(135deg, #8b5cf6, #06b6d4)` (purple → cyan) |
| Text             | `#e2e8f0` (light slate)                                     |
| Muted Text       | `#94a3b8`                                                   |
| Card Background  | `rgba(255, 255, 255, 0.05)` (glassmorphism)                 |
| Card Border      | `rgba(255, 255, 255, 0.10)`                                 |
| UI Font          | **Inter** (400–800)                                         |
| Code Font        | **JetBrains Mono** (400–700)                                |
| Animations       | `fadeIn`, `slideUp`, `glow` (purple ↔ cyan pulse)           |

The design follows a **dark-mode-first** approach with glassmorphism cards, gradient accents, and subtle glow animations for an immersive developer-focused aesthetic.

---

## Deployment

### Vercel (Recommended)

```bash
npm i -g vercel
vercel --prod
```

### Any Static Host

The `npm run build` command outputs a fully static site to the `out/` directory. Serve it with any static hosting provider:

```bash
npm run build
npx serve out          # Quick local preview
```

Compatible with **Vercel**, **Netlify**, **GitHub Pages**, **Cloudflare Pages**, **AWS S3 + CloudFront**, or any server that can serve static HTML files.

---

## Data Source

All content is driven by a single file:

```
src/data/registry.json
```

This file is extracted from the root `omniskill.yaml` manifest and contains the complete registry — skills, agents, pipelines, bundles, platforms, and stats.

**To update the site content:**

1. Edit `omniskill.yaml` in the repository root
2. Re-extract the registry: regenerate `src/data/registry.json`
3. Rebuild: `npm run build`

The registry schema includes:

| Collection  | Count | Key Fields                                                            |
| ----------- | ----- | --------------------------------------------------------------------- |
| `skills`    | 49    | name, slug, description, category, tags, priority, platforms, version |
| `agents`    | 8     | name, slug, role, emoji, persona, skills, philosophy                  |
| `pipelines` | 5     | name, slug, description, trigger, steps, version                      |
| `bundles`   | 8     | name, slug, description, skills, skillCount, category                 |
| `platforms` | 5     | id, name, icon, target                                                |

---

## Pages

| Route            | Page               | Description                                    |
| ---------------- | ------------------ | ---------------------------------------------- |
| `/`              | Landing            | Hero, stats, features grid, platforms, CTA     |
| `/skills`        | Skill Marketplace  | Search, filter, and browse all 49 skills       |
| `/skills/[slug]` | Skill Detail (×49) | Metadata, install commands, related resources  |
| `/agents`        | Agent Directory    | 8 agents with roles, workflow phases, personas |
| `/pipelines`     | Pipeline Gallery   | 5 pipelines with step-by-step flow diagrams    |
| `/bundles`       | Bundle Showcase    | 8 curated bundles with skill lists             |
| `/docs`          | Documentation Hub  | Quick start, links to all doc topics on GitHub |

**Total: 58 static pages** (7 section pages + 49 skill detail pages + index variants)

---

## Contributing

### Adding a New Page

1. Create a new directory under `src/app/` with a `page.tsx` file
2. Add navigation links in `src/components/Navbar.tsx`
3. Use existing components or create new ones in `src/components/`
4. Follow the established Tailwind theme tokens (`brand-*` classes)

### Updating Registry Data

1. Modify `omniskill.yaml` in the repository root
2. Regenerate `src/data/registry.json` from the updated YAML
3. If new fields are added, update `src/lib/types.ts` with the new interfaces
4. Update `src/lib/registry.ts` if new accessor functions are needed
5. Run `npm run build` to verify all pages generate correctly

### Adding a New Skill

When a new skill is added to the registry, the `/skills/[slug]` dynamic route automatically generates a detail page for it — no manual page creation required. Just update `registry.json` and rebuild.

### Code Conventions

- **TypeScript strict mode** — all types must be explicit
- **Path aliases** — use `@/` for `src/` imports (e.g., `@/lib/registry`)
- **Server components by default** — only use `"use client"` when interactivity is required
- **Tailwind only** — no CSS modules or styled-components

---

<p align="center">
  Built with 💜 by the OMNISKILL team
</p>
