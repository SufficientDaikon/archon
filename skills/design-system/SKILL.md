# DESIGN.md - Archon Design Intelligence

## Overview

This skill teaches the design agent to produce, read, audit, and apply DESIGN.md
- the canonical plain-text design system format.

A DESIGN.md is a single markdown file that captures the complete visual language of a product.

The design agent primary output is always a DESIGN.md (or code that implements one).

---

## Core Principle

Design decisions are made ONCE in DESIGN.md. Then referenced everywhere. Never ad-hoc.

When Archon makes a UI decision, it must trace back to a section in DESIGN.md.

---

## The DESIGN.md Format - 9 Sections

Every DESIGN.md must follow this structure.

### Section 1 - Visual Theme and Atmosphere [Required]

Narrative foundation. 3-5 paragraphs: feel, density, philosophy. Not specs - story.
Capture: dominant surfaces, typography strategy, color philosophy, brand personality.
End with Key Characteristics: 8-12 bullet points of most distinctive tokens.

### Section 2 - Color Palette and Roles [Required]

Every color named semantically with hex and one-line role.
Subsections: Background Surfaces, Text/Content, Brand/Accent, Status, Borders, Interactive, Overlay.
Rule: semantic names only. rgba for translucent values. Every color in Sec 4 must be listed here.

### Section 3 - Typography Rules [Required]

Font Family + fallbacks, OpenType Features, Hierarchy Table.
Table columns: Role | Font | Size | Weight | Line Height | Letter Spacing | Notes
Required roles: Display XL/Large/Base, H1/H2/H3, Body Large/Body/Small, Caption, Label, Mono.
Rules: letter-spacing in px, line-height as ratio, weight as number, document OpenType features.

### Section 4 - Component Stylings [Required]

Exact CSS token values for all repeating elements.
Required: Buttons (all variants), Cards, Inputs, Badges/Pills, Navigation, Image Treatment.
Each entry: Background, Text, Padding, Radius, Border, Shadow, Hover, Use.
Rules: actual CSS syntax, include hover/focus/disabled states, note shadow-as-border.

### Section 5 - Layout Principles [Required]

Spacing Scale, Grid/Container, Whitespace Philosophy paragraph, Border Radius Scale.
Radius scale: 2px micro, 4px compact, 6px buttons/inputs, 8px cards, 12px panels, 9999px pills.

### Section 6 - Depth and Elevation [Required]

Shadow system as table: Flat(L0), Subtle(L1), Surface(L2), Elevated(L3), Dialog(L4), Focus.
Shadow Philosophy paragraph: how depth is communicated in this specific system.

### Section 7 - Dos and Donts [Required]

Design guardrails. Minimum 8 Dos and 8 Donts with specific token values. Critical rules first.

### Section 8 - Responsive Behavior [Recommended]

Breakpoints table, Touch Targets (44x44px min), Typography Scaling with clamp(), Grid Collapsing.

### Section 9 - Agent Prompt Guide [Required]

Quick Reference token summary + prompt templates for Hero Section, Card, Navigation.
Templates use actual resolved values - no placeholders in final output.

---
## How to Generate a DESIGN.md

### From a Project Description

1. Extract constraints: product category, target audience, dark/light preference, brand colors, platform.
2. Choose an archetype from the Brand Library below.
3. Customize: modify accent color, adjust density for audience, adapt fonts.
4. Write all 9 sections in order - atmosphere first, tokens last, prompts always.
5. Self-audit: every color in Sec 4 is in Sec 2, Sec 9 uses real values, no speculative tokens.

### From an Existing Site or Design

1. Extract actual CSS values - measure from source, never guess.
2. Name colors semantically by function, not shade.
3. Document typography by inspecting computed styles.
4. Note distinctive techniques: shadow-as-border, luminance stepping, etc.
5. Build Section 9 last, after all tokens are confirmed.

---

## Brand Library - Reference Archetypes

### Ultra-Minimal Precision (Linear-style)
Best for: Developer tools, productivity apps, B2B SaaS
Surfaces: #08090a (base) / #0f1011 (panel) / #191a1b (elevated)
Text: #f7f8f8 primary, #d0d6e0 secondary, #8a8f98 tertiary
Accent: Single indigo-violet #5e6ad2 / #7170ff (interactive) / #828fff (hover)
Type: Inter Variable, weight 510 signature, -1.584px tracking at 72px
Borders: rgba(255,255,255,0.05) to rgba(255,255,255,0.08)
Depth: Luminance stepping - each level slightly increases white opacity
Philosophy: Darkness as native medium. Content emerges from black.

### Gallery Minimalism (Vercel-style)
Best for: Infrastructure products, developer platforms, clean B2B
Surfaces: #ffffff canvas, #fafafa tint, #171717 text
Accent: Workflow-specific #0a72ef (dev), #de1d8d (preview), #ff5b4f (ship)
Type: Geist, weight 600 at display, -2.4px to -2.88px tracking
Depth: Shadow-as-border rgba(0,0,0,0.08) 0px 0px 0px 1px everywhere
Philosophy: Radical whitespace. Every element earns its pixel.

### Terminal Native (Ollama/Warp-style)
Best for: CLI tools, developer-first, open source
Surfaces: Pure or near-black, monochrome
Accent: Green or amber for functional states only
Type: Monospace-first, system fonts acceptable
Philosophy: Interface as instrument, not product.

### Trust-Forward Finance (Stripe-style)
Best for: Fintech, payments, banking, enterprise
Surfaces: Deep purple gradient or near-black
Accent: Brand purple #635bff or gradient
Type: Weight 300 for elegance at display sizes
Philosophy: Precision, credibility, frictionless transaction.

### Open Source Energy (Supabase-style)
Best for: Developer tools, OSS, community
Surfaces: #1c1c1c + #3ecf8e emerald accent
Accent: Vibrant brand color used more freely than B2B
Philosophy: Power made accessible.

### Premium Editorial (Apple-style)
Best for: Consumer products, creative tools, premium
Surfaces: White with generous padding, photography-driven
Text: #1d1d1f primary, #6e6e73 secondary
Accent: Minimal blue #0071e3 or warm neutrals
Philosophy: Product IS the design. Minimalism as luxury.

---
## How to Apply a DESIGN.md

When given a DESIGN.md and asked to build UI:
1. Read Section 9 first - Agent Prompt Guide has the critical token subset.
2. Section 1 - understand the spirit before touching code.
3. Each component: match the exact specification in Section 4.
4. Spacing: use values from Section 5 scale only - no arbitrary values.
5. Shadows: take a value from Section 6 elevation levels.
6. Before shipping: run Section 7 Donts as a checklist.

Never introduce a value not in DESIGN.md. Propose an amendment first.

---

## How to Audit UI Against a DESIGN.md

1. Color audit: extract all hex/rgb from code, map to Section 2, flag orphans.
2. Typography audit: check font-family/weight/size/letter-spacing against Section 3 table.
3. Spacing audit: check margin/padding/gap against Section 5 scale.
4. Radius audit: check border-radius against Section 5 radius scale.
5. Shadow audit: check box-shadow against Section 6 levels.
6. Rules audit: run through Section 7 Donts explicitly.

Audit Report format:
  Colors: N/M compliant. Violations: [list]
  Typography: N/M compliant
  Spacing: N violations [list]
  Shadows: compliant / [violations]
  Rules: N Dont violations
  Score: N/100

---

## CSS Token Implementation

Token names map to DESIGN.md section names.
--text-secondary = Section 2 > Text > Secondary Text.
--shadow-3 = Section 6 > Elevated (Level 3).

Canonical variable naming:
  --surface-{base|panel|elevated|hover}
  --text-{primary|secondary|tertiary|quaternary}
  --accent-{brand|interactive|hover}
  --status-{success|warning|error|info}
  --border-{prominent|subtle}
  --space-{1|2|3|4|6|8|12|16}   (multiples of 4px base unit)
  --radius-{micro|sm|md|card|panel|pill}
  --shadow-{1|2|3|dialog|focus}

Always include comment: Generated from DESIGN.md - update DESIGN.md not this file.

---

## Design Quality Checklist

Visual Integrity:
  [ ] All colors trace to Section 2
  [ ] All type specs follow Section 3 hierarchy table
  [ ] Components match Section 4 specs
  [ ] Spacing uses Section 5 scale only
  [ ] Shadows match Section 6 levels
  [ ] No Section 7 Dont violations

DESIGN.md Completeness:
  [ ] All 9 sections present
  [ ] Section 9 uses real values (no placeholders)
  [ ] 8+ Dos and 8+ Donts in Section 7
  [ ] Typography covers display/h1-h3/body/caption/mono

Implementation Readiness:
  [ ] CSS custom properties generated
  [ ] Font families have fallback stacks
  [ ] Responsive behavior documented
  [ ] DESIGN.md in project root

---

## Anti-Patterns (What Bad Design AI Does)

1. Generic Inter + Tailwind defaults - font-sans and text-gray-700 without a defined system
2. Arbitrary hex values - a color appearing nowhere in the design brief or palette
3. Inconsistent radius - mixing 4px/6px/8px/10px/12px without a scale
4. Default shadows - box-shadow: 0 1px 3px rgba(0,0,0,0.12) copy-pasted everywhere
5. Color inconsistency - different shades of brand color in different components
6. Over-accented - brand color everywhere instead of reserved for interactive/CTA
7. Weight abuse - font-weight: 700 everywhere for emphasis
8. Spacing improvisation - padding not on grid (13px, 17px, 23px)

Every item above should be caught by Section 7 Donts of a well-written DESIGN.md.
