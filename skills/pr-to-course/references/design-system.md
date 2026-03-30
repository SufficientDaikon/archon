# Design System Reference

Complete CSS design tokens for PR courses. Copy the entire `:root` block into your course HTML and adapt the accent color to suit the PR's domain.

## Color Palette

```css
:root {
  /* --- BACKGROUNDS --- */
  --color-bg: #faf7f2; /* warm off-white, like aged paper */
  --color-bg-warm: #f5f0e8; /* slightly warmer for alternating modules */
  --color-bg-code: #1e1e2e; /* deep indigo-charcoal for code blocks */
  --color-text: #2c2a28; /* dark charcoal, easy on eyes */
  --color-text-secondary: #6b6560; /* warm gray for secondary text */
  --color-text-muted: #9e9790; /* muted for timestamps, labels */
  --color-border: #e5dfd6; /* subtle warm border */
  --color-border-light: #eeebe5; /* even lighter border */
  --color-surface: #ffffff; /* card surfaces */
  --color-surface-warm: #fdf9f3; /* warm card surface */

  /* --- ACCENT (adapt per PR domain) ---
     Default: vermillion. Alternatives:
     - coral (#E06B56) — UI/frontend PRs
     - teal (#2A7B9B) — networking/API PRs
     - amber (#D4A843) — build system/CI PRs
     - forest (#2D8B55) — testing/quality PRs
     Avoid purple gradients. */
  --color-accent: #d94f30;
  --color-accent-hover: #c4432a;
  --color-accent-light: #fdeee9;
  --color-accent-muted: #e8836c;

  /* --- SEMANTIC --- */
  --color-success: #2d8b55;
  --color-success-light: #e8f5ee;
  --color-error: #c93b3b;
  --color-error-light: #fde8e8;
  --color-info: #2a7b9b;
  --color-info-light: #e4f2f7;

  /* --- ACTOR COLORS (assign to key components in the PR) ---
     Each major "character" gets a distinct color for
     chat bubbles, diagrams, flow animations, and highlights */
  --color-actor-1: #d94f30; /* vermillion — primary component */
  --color-actor-2: #2a7b9b; /* teal — secondary component */
  --color-actor-3: #7b6daa; /* muted plum — OS/platform */
  --color-actor-4: #d4a843; /* golden — configuration/manifest */
  --color-actor-5: #2d8b55; /* forest — tests/validation */
}
```

**Rules:**

- Even-numbered modules use `--color-bg`, odd-numbered use `--color-bg-warm`
- Actor colors must be visually distinct from each other and the accent
- Code blocks always use `--color-bg-code` with light text
- For PR courses, assign actor colors to the main components that interact (e.g., OS, manifest, entry point, console API, test framework)

---

## Typography

```css
:root {
  /* --- FONTS ---
     Display: bold, geometric, personality-driven. NOT Inter/Roboto/Arial.
     Body: readable with character. NOT system fonts.
     Mono: developer-friendly with clear character distinction. */
  --font-display: "Bricolage Grotesque", Georgia, serif;
  --font-body: "DM Sans", -apple-system, sans-serif;
  --font-mono: "JetBrains Mono", "Fira Code", "Consolas", monospace;

  /* --- TYPE SCALE (1.25 ratio) --- */
  --text-xs: 0.75rem; /* 12px — labels, badges, file paths */
  --text-sm: 0.875rem; /* 14px — secondary text, code */
  --text-base: 1rem; /* 16px — body text */
  --text-lg: 1.125rem; /* 18px — lead paragraphs */
  --text-xl: 1.25rem; /* 20px — screen headings */
  --text-2xl: 1.5rem; /* 24px — sub-module titles */
  --text-3xl: 1.875rem; /* 30px — module subtitles */
  --text-4xl: 2.25rem; /* 36px — module titles */
  --text-5xl: 3rem; /* 48px — hero text */
  --text-6xl: 3.75rem; /* 60px — module numbers (faded background) */

  /* --- LINE HEIGHTS --- */
  --leading-tight: 1.15; /* headings */
  --leading-snug: 1.3; /* subheadings */
  --leading-normal: 1.6; /* body text */
  --leading-loose: 1.8; /* relaxed reading */
}
```

**Google Fonts link (put in `<head>`):**

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
  href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400;1,9..40,500&family=JetBrains+Mono:wght@400;500;600&display=swap"
  rel="stylesheet"
/>
```

**Rules:**

- Module numbers: `--text-6xl`, font-display, weight 800, accent color at 8-15% opacity, position absolute
- Module titles: `--text-4xl`, font-display, weight 700
- Screen headings: `--text-xl` or `--text-2xl`, font-display, weight 600
- Body text: `--text-base` or `--text-lg`, font-body, `--leading-normal`
- Code: `--text-sm`, font-mono
- File paths: `--text-xs`, font-mono, `--color-text-muted`
- Labels/badges: `--text-xs`, font-mono, uppercase, letter-spacing 0.05em

---

## Spacing & Layout

```css
:root {
  --space-1: 0.25rem; /* 4px */
  --space-2: 0.5rem; /* 8px */
  --space-3: 0.75rem; /* 12px */
  --space-4: 1rem; /* 16px */
  --space-5: 1.25rem; /* 20px */
  --space-6: 1.5rem; /* 24px */
  --space-8: 2rem; /* 32px */
  --space-10: 2.5rem; /* 40px */
  --space-12: 3rem; /* 48px */
  --space-16: 4rem; /* 64px */
  --space-20: 5rem; /* 80px */
  --space-24: 6rem; /* 96px */

  --content-width: 800px; /* standard reading width */
  --content-width-wide: 1000px; /* for side-by-side layouts */
  --nav-height: 50px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-full: 9999px;
}
```

**Module layout:**

```css
.module {
  min-height: 100dvh;
  scroll-snap-align: start;
  padding: var(--space-16) var(--space-6);
  padding-top: calc(var(--nav-height) + var(--space-12));
}
.module-content {
  max-width: var(--content-width);
  margin: 0 auto;
}
```

**Stats grid (PR-specific — always 4 columns):**

```css
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
}
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

---

## Shadows & Depth

```css
:root {
  --shadow-sm: 0 1px 2px rgba(44, 42, 40, 0.05);
  --shadow-md: 0 4px 12px rgba(44, 42, 40, 0.08);
  --shadow-lg: 0 8px 24px rgba(44, 42, 40, 0.1);
  --shadow-xl: 0 16px 48px rgba(44, 42, 40, 0.12);
}
```

Use warm-tinted RGBA (44, 42, 40) — never pure black shadows.

---

## Animations & Transitions

```css
:root {
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --stagger-delay: 120ms;
}
```

**Scroll-triggered reveal:**

```css
.animate-in {
  opacity: 0;
  transform: translateY(20px);
  transition:
    opacity var(--duration-slow) var(--ease-out),
    transform var(--duration-slow) var(--ease-out);
}
.animate-in.visible {
  opacity: 1;
  transform: translateY(0);
}
```

**IntersectionObserver setup:**

```javascript
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  },
  { rootMargin: "0px 0px -10% 0px", threshold: 0.1 },
);

document.querySelectorAll(".animate-in").forEach((el) => observer.observe(el));
```

---

## Navigation & Progress

```html
<nav class="nav">
  <div class="progress-bar" role="progressbar" aria-valuenow="0"></div>
  <div class="nav-inner">
    <span class="nav-title">Course Title</span>
    <div class="nav-dots">
      <button
        class="nav-dot"
        data-target="module-0"
        data-tooltip="Overview"
        role="tab"
        aria-label="Module 0"
      ></button>
      <!-- one dot per module -->
    </div>
  </div>
</nav>
```

**Nav dot states:**

- Default: `border: 2px solid var(--color-text-muted)`, empty
- Current: `border-color: var(--color-accent)`, filled, subtle glow
- Visited: `background: var(--color-accent)`, solid fill

---

## PR-Specific Elements

### Before/After Visual

```css
.before-after {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  margin: var(--space-8) 0;
}
.before-side {
  background: var(--color-error-light);
  border: 2px solid var(--color-error);
  border-radius: var(--radius-md);
  padding: var(--space-6);
  text-align: center;
}
.after-side {
  background: var(--color-success-light);
  border: 2px solid var(--color-success);
  border-radius: var(--radius-md);
  padding: var(--space-6);
  text-align: center;
}
@media (max-width: 480px) {
  .before-after {
    grid-template-columns: 1fr;
  }
}
```

### Source File Cards

```css
.file-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  margin-bottom: var(--space-4);
  box-shadow: var(--shadow-sm);
}
.file-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}
.file-path {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}
.file-badge {
  font-size: var(--text-xs);
  font-family: var(--font-mono);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-full);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.file-badge.new {
  background: var(--color-success-light);
  color: var(--color-success);
}
.file-badge.modified {
  background: var(--color-info-light);
  color: var(--color-info);
}
```

### Test Coverage Cards

```css
.test-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-4);
}
.test-card {
  background: var(--color-surface);
  border-left: 4px solid var(--color-success);
  border-radius: var(--radius-sm);
  padding: var(--space-4);
  box-shadow: var(--shadow-sm);
}
.test-card-name {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 600;
  margin-bottom: var(--space-2);
}
.test-card-desc {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}
```

---

## Responsive Breakpoints

```css
@media (max-width: 768px) {
  :root {
    --text-4xl: 1.875rem;
    --text-5xl: 2.25rem;
    --text-6xl: 3rem;
  }
  .translation-block {
    grid-template-columns: 1fr;
  }
  .before-after {
    grid-template-columns: 1fr;
  }
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  :root {
    --text-4xl: 1.5rem;
    --text-5xl: 1.875rem;
    --text-6xl: 2.25rem;
  }
  .module {
    padding: var(--space-8) var(--space-4);
  }
  .flow-steps {
    flex-direction: column;
  }
  .flow-arrow {
    transform: rotate(90deg);
  }
}
```

---

## Code Blocks

```css
pre,
code {
  white-space: pre-wrap;
  word-break: break-word;
  overflow-x: hidden;
}
```

**Syntax highlighting (Catppuccin-inspired on #1E1E2E):**

```css
.code-keyword {
  color: #cba6f7;
} /* purple — if, else, return, try, catch */
.code-string {
  color: #a6e3a1;
} /* green — "strings" */
.code-function {
  color: #89b4fa;
} /* blue — function/method names */
.code-comment {
  color: #6c7086;
} /* muted gray — // comments */
.code-number {
  color: #fab387;
} /* peach — numbers, constants */
.code-property {
  color: #f9e2af;
} /* yellow — property names, keys */
.code-operator {
  color: #94e2d5;
} /* teal — =, =>, +, etc. */
.code-tag {
  color: #f38ba8;
} /* pink — XML/HTML tags */
.code-attr {
  color: #f9e2af;
} /* yellow — XML/HTML attributes */
.code-value {
  color: #a6e3a1;
} /* green — attribute values */
.code-type {
  color: #89dceb;
} /* sky — type names (C#, TS) */
```

---

## Scrollbar & Background

```css
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: var(--radius-full);
}

body {
  background: var(--color-bg);
  background-image: radial-gradient(
    ellipse at 20% 50%,
    rgba(217, 79, 48, 0.03) 0%,
    transparent 50%
  );
}

html {
  scroll-snap-type: y proximity;
  scroll-behavior: smooth;
}
```
