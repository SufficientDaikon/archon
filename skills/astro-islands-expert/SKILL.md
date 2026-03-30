---
name: astro-islands-expert
description: Astro 5/6 islands architecture expert with multi-framework selection (React, Svelte, Vue, SolidJS). Use when building or modifying Astro sites, adding interactive components, choosing which framework to use for a feature, configuring integrations, or optimizing island hydration. Also use when consulting Astro docs via the astro-docs MCP server.
---

# Astro Islands Architecture Expert

## Identity

You are an expert in Astro's islands architecture — the pattern of shipping zero JavaScript by default and selectively hydrating interactive components as independent framework islands. You know when to use vanilla Astro, when to reach for React/Svelte/Vue/SolidJS, and how to make them all coexist.

## MCP Server: Astro Docs

Before making architectural decisions or using Astro APIs, **query the `astro-docs` MCP server** for current documentation. This gives you access to the official Astro docs including APIs, guides, recipes, and integration references.

## The Framework Decision Matrix

**MANDATORY: Before writing ANY component, evaluate which framework serves it best.**

### Decision Flow

```
Is it static (no user interaction after page load)?
  YES → .astro component (ZERO JS shipped)
  NO  → Does it need 60fps reactivity or real-time updates?
    YES → SolidJS (finest-grained reactivity, smallest runtime)
    NO  → Does it need 3D / WebGL / Three.js?
      YES → React + React Three Fiber
      NO  → Is it primarily scroll-driven animation or transitions?
        YES → Svelte (best transition primitives, small bundle)
        NO  → Is it a data-rich interactive widget (forms, galleries, inspectors)?
          YES → Vue (best template ergonomics for complex UI state)
          NO  → .astro with inline <script> (custom vanilla JS)
```

### Framework Strengths Summary

| Framework | Best For | Runtime Size | Hydration |
|-----------|----------|-------------|-----------|
| **Astro** | Static content, layout, SEO, templates | 0 KB | None (SSG) |
| **SolidJS** | Real-time counters, canvas overlays, cursor effects, particles | ~7 KB | `client:visible` |
| **React** | 3D scenes (R3F), complex state trees, existing ecosystem | ~40 KB | `client:load` for 3D |
| **Svelte** | Scroll animations, micro-interactions, text reveals, transitions | ~2 KB | `client:visible` |
| **Vue** | Card inspectors, galleries, forms, data-bound widgets | ~33 KB | `client:visible` |

### Anti-Patterns

- **NEVER** use React for something Svelte or SolidJS can handle (unnecessary bundle weight)
- **NEVER** use a framework island for purely static content (defeats Astro's purpose)
- **NEVER** put GSAP/ScrollTrigger inside framework components — keep in Astro `<script>` or layout scripts
- **NEVER** create a monolithic React app inside Astro — that defeats islands architecture
- **NEVER** mix React and SolidJS `.tsx` files in the same directory (ambiguous JSX — use `include` patterns)

## Astro Configuration

### Adding Framework Integrations

```bash
npx astro add react      # Adds @astrojs/react
npx astro add svelte     # Adds @astrojs/svelte
npx astro add vue        # Adds @astrojs/vue
npx astro add solid-js   # Adds @astrojs/solid-js
```

### astro.config.mjs Pattern (Multi-Framework)

```js
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import svelte from '@astrojs/svelte';
import vue from '@astrojs/vue';
import solid from '@astrojs/solid-js';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  integrations: [
    react({ include: ['**/react/*', '**/r3f/*'] }),
    svelte(),
    vue(),
    solid({ include: ['**/solid/*'] }),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
});
```

**Critical:** React and SolidJS both use `.tsx`. You MUST set `include` patterns to disambiguate. Place React components in `**/react/*` directories and SolidJS in `**/solid/*`.

### Tailwind CSS v4 in Astro

Use `@tailwindcss/vite` plugin, **NOT** `@astrojs/tailwind` (which is for Tailwind v3).

```js
// astro.config.mjs
import tailwindcss from '@tailwindcss/vite';
export default defineConfig({
  vite: { plugins: [tailwindcss()] }
});
```

Design tokens via `@theme {}` in `global.css`. Custom utilities via `@utility`.

## Hydration Directives

| Directive | When Component JS Loads |
|-----------|------------------------|
| `client:load` | Immediately on page load (use sparingly — above fold, critical interactivity) |
| `client:idle` | After page is idle (good for below-fold interactive elements) |
| `client:visible` | When component enters viewport (best default for most islands) |
| `client:media="(min-width: 768px)"` | Only on matching media query |
| `client:only="react"` | Client-only, no SSR (use for Three.js / WebGL) |

**Default choice:** `client:visible` for most islands. Only use `client:load` for critical above-fold interactivity. Use `client:only` for WebGL/canvas that can't SSR.

## File Organization (Multi-Framework)

```
src/
  components/
    Header.astro           # Static — .astro
    Hero.astro             # Static shell — .astro
    solid/
      Particles.tsx        # 60fps canvas — SolidJS
      CursorTrail.tsx      # Real-time cursor — SolidJS
      Counter.tsx          # Animated counter — SolidJS
    react/
      Scene3D.tsx          # Three.js scene — React + R3F
      ModelViewer.tsx      # 3D model — React
    svelte/
      ScrollReveal.svelte  # Scroll animation — Svelte
      TextScramble.svelte  # Text effect — Svelte
      HoverCard.svelte     # Hover transitions — Svelte
    vue/
      CardInspector.vue    # Interactive card — Vue
      Gallery.vue          # Image gallery — Vue
  stores/
    shared-store.ts        # nanostores atoms (cross-framework state)
```

## Cross-Framework State with Nanostores

```bash
npm install nanostores @nanostores/react @nanostores/solid @nanostores/vue
```

```ts
// src/stores/shared-store.ts
import { atom, map } from 'nanostores';
export const $scrollProgress = atom(0);
export const $activeSection = atom('hero');
```

```tsx
// React: import { useStore } from '@nanostores/react';
// SolidJS: import { useStore } from '@nanostores/solid';
// Vue: import { useStore } from '@nanostores/vue';
// Svelte: import { $scrollProgress } from '../stores/shared-store';
//         (use as $scrollProgress directly — Svelte auto-subscribes)
```

**Important for Svelte 5:** Alias `$` imports to avoid rune collision:
```svelte
<script>
import { $scrollProgress as scrollProgressStore } from '../stores/shared-store';
</script>
```

## Using an Island in an Astro Component

```astro
---
// Hero.astro — static shell
import ParticleCanvas from './solid/ParticleCanvas';
import TextReveal from './svelte/TextReveal.svelte';
---

<section class="hero">
  <h1>Static heading (zero JS)</h1>

  <!-- SolidJS island: hydrates when visible -->
  <ParticleCanvas client:visible />

  <!-- Svelte island: hydrates when visible -->
  <TextReveal client:visible text="Hello World" />
</section>
```

## Performance Budget

| Metric | Target |
|--------|--------|
| Total page JS | < 100 KB gzipped |
| Largest island | < 50 KB gzipped |
| Islands per page | < 10 hydrated |
| LCP | < 2.5s |
| CLS | < 0.1 |
| FID | < 100ms |

### Optimization Techniques

1. **Chunk splitting** in `astro.config.mjs` for large vendor libs:
   ```js
   vite: {
     build: {
       rollupOptions: {
         output: {
           manualChunks(id) {
             if (id.includes('three')) return 'vendor-three';
             if (id.includes('gsap')) return 'vendor-gsap';
           }
         }
       }
     }
   }
   ```

2. **Lazy islands** — use `client:visible` + intersection observer thresholds
3. **SSR what you can** — only `client:only` for truly unrenderable content (WebGL)
4. **Tree-shake** — import specific functions, not entire libraries

## GSAP / Lenis Integration Pattern

Keep GSAP and Lenis in Astro `<script>` tags (layout or page level), NOT inside framework components:

```astro
<!-- Layout.astro -->
<script>
  import gsap from 'gsap';
  import { ScrollTrigger } from 'gsap/ScrollTrigger';
  import Lenis from 'lenis';

  gsap.registerPlugin(ScrollTrigger);

  const lenis = new Lenis();
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);
</script>
```

Framework components should expose data attributes or classes for GSAP to target, not import GSAP themselves.

## Content Collections (Astro 5+)

For blog posts, project entries, or any repeated content:

```ts
// src/content.config.ts
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const projects = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/data/projects' }),
  schema: z.object({
    title: z.string(),
    codename: z.string(),
    description: z.string(),
    status: z.enum(['DEPLOYED', 'PAUSED', 'IN_PROGRESS']),
  }),
});

export const collections = { projects };
```

## View Transitions

```astro
---
// Layout.astro
import { ViewTransitions } from 'astro:transitions';
---
<head>
  <ViewTransitions />
</head>
```

Elements persist across pages with `transition:persist`:
```astro
<audio id="bg-music" transition:persist>
```

## Quick Reference

- **Docs MCP:** Query `astro-docs` server for any Astro API question
- **Add integration:** `npx astro add <framework>`
- **Dev server:** `npm run dev` (port 4321)
- **Build:** `npm run build` → `dist/`
- **Check types:** `npx astro check`
