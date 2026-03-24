---
name: ui-visual-design
description: Visual design mastery including color theory, typography systems, visual hierarchy, hero section patterns, page section patterns, design tokens, and modern design trends. Use when creating visual designs, building design systems, designing hero sections, or establishing design tokens.
---

# UI Visual Design Mastery

## Color Theory & Palette Generation

### 60-30-10 Rule
- **60% Neutral**: Base colors for backgrounds, containers, text. Use gray scales (50-950) or off-white tints
- **30% Primary**: Brand color and main interactive elements. Should have complete shade scale
- **10% Accent**: Highlights, CTAs, alerts, status indicators. High contrast, attention-grabbing

### Generating Shade Scales with HSL Manipulation

Complete shade scale generation for any base color:

```css
/* Base HSL: hsl(220, 80%, 50%) - Primary Blue Example */
--color-primary-50: hsl(220, 80%, 95%);   /* Lightest tint */
--color-primary-100: hsl(220, 80%, 90%);
--color-primary-200: hsl(220, 80%, 80%);
--color-primary-300: hsl(220, 80%, 70%);
--color-primary-400: hsl(220, 80%, 60%);
--color-primary-500: hsl(220, 80%, 50%);  /* Base color */
--color-primary-600: hsl(220, 80%, 40%);
--color-primary-700: hsl(220, 80%, 30%);
--color-primary-800: hsl(220, 80%, 20%);
--color-primary-900: hsl(220, 80%, 10%);
--color-primary-950: hsl(220, 80%, 5%);   /* Darkest shade */
```

**Scale Generation Formula**:
- Tints (50-400): Increase lightness, slightly reduce saturation
- Base (500): Original color
- Shades (600-950): Decrease lightness, maintain or slightly increase saturation

### Semantic Color Systems

**Success Green Scale**:
```css
--color-success-50: hsl(120, 60%, 95%);
--color-success-500: hsl(120, 60%, 45%);  /* Base green */
--color-success-900: hsl(120, 60%, 15%);
```

**Warning Amber Scale**:
```css
--color-warning-50: hsl(45, 90%, 95%);
--color-warning-500: hsl(45, 90%, 55%);   /* Base amber */
--color-warning-900: hsl(45, 90%, 20%);
```

**Error Red Scale**:
```css
--color-error-50: hsl(0, 70%, 95%);
--color-error-500: hsl(0, 70%, 50%);      /* Base red */
--color-error-900: hsl(0, 70%, 20%);
```

**Info Blue Scale**:
```css
--color-info-50: hsl(210, 80%, 95%);
--color-info-500: hsl(210, 80%, 55%);     /* Base info blue */
--color-info-900: hsl(210, 80%, 20%);
```

### Neutral Scale Generation

**Pure Gray** (Balanced):
```css
--color-neutral-50: hsl(0, 0%, 98%);
--color-neutral-500: hsl(0, 0%, 50%);
--color-neutral-900: hsl(0, 0%, 10%);
```

**Warm Gray** (Slight yellow/red tint):
```css
--color-neutral-50: hsl(30, 5%, 98%);
--color-neutral-500: hsl(30, 5%, 50%);
--color-neutral-900: hsl(30, 5%, 10%);
```

**Cool Gray** (Slight blue tint):
```css
--color-neutral-50: hsl(220, 8%, 98%);
--color-neutral-500: hsl(220, 8%, 50%);
--color-neutral-900: hsl(220, 8%, 10%);
```

### Gradient Patterns with CSS

**Linear Gradients**:
```css
/* Subtle brand gradient */
background: linear-gradient(135deg, var(--color-primary-400) 0%, var(--color-primary-600) 100%);

/* Hero gradient overlay */
background: linear-gradient(135deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 100%);

/* Mesh gradient effect */
background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
```

**Radial Gradients**:
```css
/* Spotlight effect */
background: radial-gradient(circle at 50% 20%, rgba(255,255,255,0.1) 0%, transparent 50%);

/* Glow effect */
background: radial-gradient(ellipse at center, var(--color-primary-500) 0%, transparent 70%);
```

**Conic Gradients**:
```css
/* Rainbow conic */
background: conic-gradient(from 0deg, #ff0000, #ff8000, #ffff00, #80ff00, #00ff00, #00ff80, #00ffff, #0080ff, #0000ff, #8000ff, #ff0080, #ff0000);
```

### Dark Mode Color Mapping Strategy

**Inversion Rules**:
- Light mode 50 → Dark mode 950
- Light mode 100 → Dark mode 900
- Light mode 900 → Dark mode 100
- Light mode 950 → Dark mode 50

```css
:root {
  --color-bg-primary: var(--color-neutral-50);
  --color-text-primary: var(--color-neutral-900);
}

[data-theme="dark"] {
  --color-bg-primary: var(--color-neutral-950);
  --color-text-primary: var(--color-neutral-50);
}
```

## Typography Scale Systems

### Modular Scales

**Minor Third (1.200)**:
```css
--text-xs: 0.694rem;    /* 11.11px */
--text-sm: 0.833rem;    /* 13.33px */
--text-base: 1rem;      /* 16px */
--text-lg: 1.2rem;      /* 19.2px */
--text-xl: 1.44rem;     /* 23.04px */
--text-2xl: 1.728rem;   /* 27.65px */
--text-3xl: 2.074rem;   /* 33.18px */
--text-4xl: 2.488rem;   /* 39.81px */
--text-5xl: 2.986rem;   /* 47.78px */
```

**Perfect Fourth (1.333)**:
```css
--text-xs: 0.563rem;    /* 9px */
--text-sm: 0.75rem;     /* 12px */
--text-base: 1rem;      /* 16px */
--text-lg: 1.333rem;    /* 21.33px */
--text-xl: 1.777rem;    /* 28.43px */
--text-2xl: 2.369rem;   /* 37.9px */
--text-3xl: 3.158rem;   /* 50.53px */
--text-4xl: 4.21rem;    /* 67.36px */
--text-5xl: 5.614rem;   /* 89.83px */
```

### Font Pairing Rules

**Serif + Sans-Serif**:
```css
--font-display: 'Playfair Display', serif;  /* Headlines */
--font-body: 'Inter', sans-serif;           /* Body text */
```

**Geometric + Humanist**:
```css
--font-display: 'Outfit', sans-serif;       /* Clean, geometric */
--font-body: 'Plus Jakarta Sans', sans-serif; /* Humanist, readable */
```

**Display + Body Combinations**:
```css
/* Modern tech stack */
--font-display: 'Geist', sans-serif;
--font-body: 'Inter', sans-serif;

/* Creative/startup */
--font-display: 'Satoshi', sans-serif;
--font-body: 'Plus Jakarta Sans', sans-serif;
```

### Fluid Typography with CSS clamp()

```css
/* Responsive heading scale */
--text-xl: clamp(1.2rem, 2vw + 1rem, 1.44rem);
--text-2xl: clamp(1.44rem, 3vw + 1rem, 1.728rem);
--text-3xl: clamp(1.728rem, 4vw + 1rem, 2.488rem);
--text-4xl: clamp(2.074rem, 5vw + 1rem, 3.158rem);
--text-5xl: clamp(2.488rem, 6vw + 1rem, 4.21rem);

/* Body text responsive */
--text-base: clamp(0.9rem, 1vw + 0.5rem, 1.1rem);
```

### System Font Stacks

**Sans-Serif System Stack**:
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
```

**Monospace System Stack**:
```css
font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'Courier New', monospace;
```

**Premium Web Font Recommendations**:
- **Inter**: Perfect for body text, extensive weights
- **Plus Jakarta Sans**: Humanist, friendly, great for startups
- **Outfit**: Geometric, modern, good for headings
- **Geist**: Clean, minimal, excellent for tech products
- **Satoshi**: Distinctive, great for brands needing personality

### Typography Measures

**Line Height**:
- Headlines: 1.1-1.3
- Body text: 1.4-1.6
- Captions: 1.3-1.4

**Letter Spacing**:
- Large headings: -0.02em to -0.05em
- Body text: 0
- Small text/caps: 0.05em to 0.1em

**Optimal Line Length**: 45-75 characters per line for readability

## Visual Hierarchy Principles

### The 6 Levers of Hierarchy

1. **Size**: Larger elements draw attention first
2. **Weight**: Bold/heavy weights create emphasis
3. **Color**: High contrast colors command attention
4. **Contrast**: Light on dark, dark on light
5. **Spacing**: Isolated elements gain importance
6. **Position**: Top-left gets seen first (F-pattern)

### Reading Pattern Layouts

**F-Pattern** (Left-to-right languages):
- Strong horizontal at top (header/navigation)
- Second horizontal (subheading/key content)
- Vertical scan down left side
- Ideal for text-heavy content

**Z-Pattern** (Single-screen layouts):
- Top-left to top-right (header/nav)
- Diagonal to bottom-left
- Bottom-left to bottom-right (CTA)
- Perfect for landing pages

### Emphasis Techniques

**Isolation**: Surround important elements with whitespace
**Contrast**: Use color/size differences strategically
**Directional Cues**: Arrows, pointing hands, eye gaze direction

## Whitespace & Layout Principles

### Macro vs Micro Whitespace

**Macro Whitespace** (Between sections):
- Hero to first section: 80-120px
- Between major sections: 60-100px
- Footer separation: 80px+

**Micro Whitespace** (Between elements):
- Heading to paragraph: 16-24px
- Paragraph to paragraph: 16px
- Button internal padding: 12px 24px
- Card internal padding: 24-32px

### Optical vs Mathematical Alignment

**Mathematical**: Grid-based, pixel-perfect alignment
**Optical**: Adjusted for visual perception (icons may need slight adjustment to appear centered)

### Content Density Guidelines

**Consumer Products** (Spacious):
- More whitespace
- Larger touch targets (44px minimum)
- Generous padding
- Focus on key actions

**Enterprise Products** (Dense):
- Information density higher
- Smaller touch targets acceptable
- Compact layouts
- Multiple actions visible

## Hero Section Design Patterns

### 1. Gradient Hero
**When to use**: Modern tech products, SaaS tools, bold brand statements
**Visual description**: Full-width gradient background, centered white text
**Content structure**: Large headline, subtitle, primary CTA, optional secondary CTA
**Key CSS**:
```css
.gradient-hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: white;
}
```

### 2. Split Hero
**When to use**: Product showcases, service explanations, app downloads
**Visual description**: 50/50 left-right split, text left, visual right
**Content structure**: Headline, description, CTA buttons on left; product screenshot/illustration right
**Key CSS**:
```css
.split-hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  min-height: 80vh;
  padding: 2rem 5%;
}
```

### 3. Full-Image Hero
**When to use**: Photography portfolios, travel, lifestyle brands, events
**Visual description**: Full-bleed background image with dark overlay and centered text
**Content structure**: Hero image, overlay (rgba(0,0,0,0.4)), centered white text
**Key CSS**:
```css
.image-hero {
  background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url('hero-image.jpg');
  background-size: cover;
  background-position: center;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}
```

### 4. Minimal Text Hero
**When to use**: Agency websites, portfolios, luxury brands, statement-making
**Visual description**: Large bold typography, no images, extensive whitespace
**Content structure**: Large headline (60-120px), minimal subtext, single CTA
**Key CSS**:
```css
.minimal-hero {
  text-align: center;
  padding: 10rem 5% 8rem;
  background: var(--color-neutral-50);
}
.minimal-hero h1 {
  font-size: clamp(3rem, 8vw, 7rem);
  font-weight: 900;
  line-height: 1.1;
  letter-spacing: -0.02em;
}
```

### 5. Video Background Hero
**When to use**: High-production brands, events, immersive experiences
**Visual description**: Autoplay looping video background with text overlay
**Content structure**: HTML5 video element, dark overlay, centered content
**Key CSS**:
```css
.video-hero {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}
.video-hero video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: -1;
}
```

### 6. Animated Particle Hero
**When to use**: Tech products, gaming, creative agencies, innovative brands
**Visual description**: Dark background with subtle moving particles/dots
**Content structure**: Canvas/SVG particles, centered text content
**Key CSS**:
```css
.particle-hero {
  background: #0f0f23;
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}
.particles-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}
```

### 7. Asymmetric Hero
**When to use**: Creative portfolios, design agencies, unique brand positioning
**Visual description**: Off-center layout with overlapping elements and dynamic composition
**Content structure**: Text positioned 1/3 from left, large decorative element overlapping
**Key CSS**:
```css
.asymmetric-hero {
  position: relative;
  min-height: 90vh;
  display: grid;
  grid-template-columns: 2fr 3fr;
  align-items: center;
}
.hero-decoration {
  position: absolute;
  right: -10%;
  top: 10%;
  z-index: -1;
  opacity: 0.1;
}
```

### 8. Card-Based Hero
**When to use**: Dashboards, SaaS products, feature showcases
**Visual description**: Hero text with floating preview cards of the product
**Content structure**: Main headline, cards showing product features/screens
**Key CSS**:
```css
.card-hero {
  position: relative;
  padding: 4rem 5% 6rem;
  overflow: hidden;
}
.floating-cards {
  position: absolute;
  right: -5%;
  top: 20%;
  transform: rotate(12deg);
}
```

### 9. Dark Mode Hero
**When to use**: Developer tools, gaming, tech products, modern apps
**Visual description**: Dark background with neon/glowing accent elements
**Content structure**: Dark theme, bright accent colors, subtle glows
**Key CSS**:
```css
.dark-hero {
  background: var(--color-neutral-950);
  color: var(--color-neutral-50);
  position: relative;
}
.neon-accent {
  color: #00ff88;
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
}
```

### 10. Illustration Hero
**When to use**: Startups, friendly brands, complex concept explanation
**Visual description**: Custom illustration or 3D render alongside hero text
**Content structure**: Split layout with custom illustration, friendly copy tone
**Key CSS**:
```css
.illustration-hero {
  display: flex;
  align-items: center;
  gap: 4rem;
  padding: 4rem 5%;
}
.hero-illustration {
  max-width: 500px;
  height: auto;
}
```

### 11. Interactive Hero
**When to use**: Interactive products, games, immersive experiences
**Visual description**: Elements respond to hover, parallax scroll effects
**Content structure**: Interactive elements, scroll-triggered animations
**Key CSS**:
```css
.interactive-hero {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}
.parallax-element {
  transform: translateZ(0);
  will-change: transform;
}
```

### 12. Stats Hero
**When to use**: B2B SaaS, startups showing traction, data-driven products
**Visual description**: Hero with key statistics that animate/count up
**Content structure**: Main headline, 3-4 key metrics with large numbers
**Key CSS**:
```css
.stats-hero {
  text-align: center;
  padding: 4rem 5%;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
}
.stat-number {
  font-size: 3rem;
  font-weight: 900;
  color: var(--color-primary-500);
}
```

## Page Section Design Patterns

### 1. Feature Grid
**Use case**: Product features, service offerings, benefits
**Content structure**: 3-4 features in columns with icons, titles, descriptions
**Layout variations**: 2x2 grid, 3-column, 4-column with wrap
```css
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  padding: 4rem 0;
}
```

### 2. Alternating Feature Rows
**Use case**: Detailed feature explanations, product storytelling
**Content structure**: Image left/text right alternating with text left/image right
**Layout variations**: 50/50 split, 60/40 split, mobile stacking
```css
.feature-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  margin-bottom: 6rem;
}
.feature-row:nth-child(even) {
  direction: rtl;
}
```

### 3. Testimonial Carousel
**Use case**: Customer validation, social proof, reviews
**Content structure**: Customer quotes, photos, names, companies, navigation
**Layout variations**: Single slide, 3-up carousel, auto-rotating

### 4. Testimonial Grid
**Use case**: Multiple testimonials, social proof wall
**Content structure**: 3-column grid of testimonial cards
**Layout variations**: Masonry layout, equal height cards

### 5. Pricing Tiers
**Use case**: SaaS products, service packages, subscription plans
**Content structure**: 3 tiers (Basic, Pro, Enterprise), highlighted recommended
**Layout variations**: Cards, table format, toggle annual/monthly

### 6. CTA Banner
**Use case**: Newsletter signup, free trial, contact conversion
**Content structure**: Compelling headline, benefit copy, prominent CTA button
**Layout variations**: Full-width, gradient background, icon accent

### 7. Stats/Numbers Strip
**Use case**: Company credibility, product metrics, user base
**Content structure**: 3-4 key metrics in a horizontal row
**Layout variations**: Centered, left-aligned, with separators

### 8. Team Grid
**Use case**: About pages, company culture, meet the team
**Content structure**: Photo cards with names, titles, brief bios
**Layout variations**: 3-column, 4-column, hover reveals

### 9. FAQ Accordion
**Use case**: Support content, common questions, feature explanations
**Content structure**: Collapsible question/answer pairs
**Layout variations**: Single column, two column, category grouping

### 10. Newsletter Signup
**Use case**: Email capture, content marketing, engagement
**Content structure**: Benefit headline, email input, subscribe button
**Layout variations**: Inline, modal, sidebar, footer

### 11. Logo Cloud
**Use case**: Social proof, partnerships, integrations
**Content structure**: "Trusted by" or "Used by" with company logos
**Layout variations**: Single row, grid, grayscale with color on hover

### 12. Comparison Table
**Use case**: Feature comparisons, plan differences, competitive analysis
**Content structure**: Feature list with checkmarks/X marks across plans
**Layout variations**: Responsive table, card format on mobile

### 13. Timeline/Process
**Use case**: How it works, step-by-step process, company history
**Content structure**: Numbered steps with titles and descriptions
**Layout variations**: Vertical timeline, horizontal steps, zigzag

### 14. Gallery/Portfolio
**Use case**: Work showcase, product gallery, case studies
**Content structure**: Image grid with titles, hover effects, lightbox
**Layout variations**: Masonry, equal grid, category filters

### 15. Integration Logos
**Use case**: API integrations, tool compatibility, ecosystem
**Content structure**: "Integrates with" section showing partner tools
**Layout variations**: Grid, slider, category groupings

### 16. Footer
**Use case**: Site navigation, legal links, contact information
**Content structure**: Multi-column with links, social media, newsletter signup
**Layout variations**: 4-column, minimal single column, mega footer

## Design Token Architecture

### Complete CSS Custom Property Structure

```css
:root {
  /* Colors */
  --color-primary-50: hsl(220, 80%, 95%);
  --color-primary-500: hsl(220, 80%, 50%);
  --color-primary-900: hsl(220, 80%, 10%);
  
  /* Neutral colors */
  --color-neutral-50: hsl(0, 0%, 98%);
  --color-neutral-500: hsl(0, 0%, 50%);
  --color-neutral-900: hsl(0, 0%, 10%);
  
  /* Semantic colors */
  --color-success-500: hsl(120, 60%, 45%);
  --color-warning-500: hsl(45, 90%, 55%);
  --color-error-500: hsl(0, 70%, 50%);
  
  /* Typography */
  --font-family-display: 'Inter', sans-serif;
  --font-family-body: 'Inter', sans-serif;
  --font-family-mono: 'SF Mono', monospace;
  
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;
  
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;
  
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-loose: 1.75;
  
  --letter-spacing-tight: -0.025em;
  --letter-spacing-normal: 0;
  --letter-spacing-wide: 0.025em;
  
  /* Spacing */
  --spacing-px: 1px;
  --spacing-0: 0;
  --spacing-1: 0.25rem;
  --spacing-2: 0.5rem;
  --spacing-3: 0.75rem;
  --spacing-4: 1rem;
  --spacing-5: 1.25rem;
  --spacing-6: 1.5rem;
  --spacing-8: 2rem;
  --spacing-10: 2.5rem;
  --spacing-12: 3rem;
  --spacing-16: 4rem;
  --spacing-20: 5rem;
  --spacing-24: 6rem;
  --spacing-32: 8rem;
  
  /* Border radius */
  --radius-none: 0;
  --radius-sm: 0.125rem;
  --radius-base: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-2xl: 1rem;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  
  /* Transitions */
  --transition-fast: 150ms ease-out;
  --transition-base: 200ms ease-out;
  --transition-slow: 300ms ease-out;
  
  /* Z-index */
  --z-index-dropdown: 1000;
  --z-index-sticky: 1020;
  --z-index-fixed: 1030;
  --z-index-modal-backdrop: 1040;
  --z-index-modal: 1050;
  --z-index-popover: 1060;
  --z-index-tooltip: 1070;
}
```

### Naming Convention
Format: `--{category}-{property}-{variant}-{state}`

Examples:
- `--color-primary-500` (category: color, property: primary, variant: 500)
- `--spacing-button-padding-horizontal` (category: spacing, property: button-padding, variant: horizontal)
- `--transition-button-hover` (category: transition, property: button, variant: hover)

## Current Design Trends (2025-2026)

### Bento Grid Layouts
**Description**: Dashboard-style grid layouts inspired by Apple's design language
**Implementation**: CSS Grid with varying cell sizes
```css
.bento-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  grid-template-rows: repeat(4, 1fr);
  gap: 1rem;
}
.bento-large { grid-column: span 4; grid-row: span 2; }
.bento-medium { grid-column: span 2; grid-row: span 2; }
.bento-small { grid-column: span 2; grid-row: span 1; }
```

### Glassmorphism 2.0
**Description**: Frosted glass effect with subtle borders and shadows
**Implementation**: backdrop-filter with blur and transparency
```css
.glass-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}
```

### Neo-Brutalism
**Description**: Bold, blocky designs with high contrast and stark shadows
**Implementation**: Hard shadows, bold typography, bright colors
```css
.neo-brutal-card {
  background: #ff6b6b;
  border: 3px solid #000;
  box-shadow: 8px 8px 0 #000;
  transform: none;
  transition: transform 0.2s ease;
}
.neo-brutal-card:hover {
  transform: translate(-4px, -4px);
}
```

### Soft Gradients
**Description**: Subtle, multi-stop gradients with low contrast
**Implementation**: Multiple color stops with gentle transitions
```css
.soft-gradient {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 25%, #e0c3fc 75%, #9bb5ff 100%);
}
```

### 3D Elements
**Description**: Subtle 3D transforms and perspective effects
**Implementation**: CSS transform3d and perspective
```css
.card-3d {
  transform-style: preserve-3d;
  transition: transform 0.3s ease;
}
.card-3d:hover {
  transform: rotateX(5deg) rotateY(10deg) translateZ(20px);
}
```

### AI-Generated Illustration Integration
**Description**: Seamless blend of AI art with design layouts
**Best practices**: Use consistent style prompts, maintain brand color palette

### Variable Fonts and Kinetic Typography
**Description**: Fonts that change weight, width, or style dynamically
**Implementation**: CSS animation with font-variation-settings
```css
@keyframes font-weight-pulse {
  0%, 100% { font-variation-settings: 'wght' 400; }
  50% { font-variation-settings: 'wght' 700; }
}
```

### Micro-Animations and Scroll-Triggered Reveals
**Description**: Subtle animations that enhance UX without distraction
**Implementation**: CSS animations with intersection observer
```css
.fade-up {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}
.fade-up.visible {
  opacity: 1;
  transform: translateY(0);
}
```

### Dark Mode as Default
**Description**: Dark themes as primary design option, not afterthought
**Implementation**: Design dark first, then create light mode variant
```css
:root {
  color-scheme: dark;
  --color-bg: #0f0f0f;
  --color-text: #ffffff;
}
@media (prefers-color-scheme: light) {
  :root {
    --color-bg: #ffffff;
    --color-text: #000000;
  }
}
```