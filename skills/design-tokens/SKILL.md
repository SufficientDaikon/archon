# Design Tokens - CSS Custom Property Generation

## What This Skill Does

Converts a DESIGN.md into production-ready CSS custom properties.

This skill always runs AFTER design-system skill has produced a DESIGN.md.
Its output (tokens.css or similar) is the implementation bridge.

---

## Canonical Token Architecture

Token names follow DESIGN.md section hierarchy:

| Token Prefix     | DESIGN.md Section | Example |
|-----------------|-------------------|---------|
| --surface-*     | Section 2 > Backgrounds | --surface-base, --surface-elevated |
| --text-*        | Section 2 > Text | --text-primary, --text-secondary |
| --accent-*      | Section 2 > Brand/Accent | --accent-brand, --accent-hover |
| --status-*      | Section 2 > Status | --status-success, --status-error |
| --border-*      | Section 2 > Borders | --border-prominent, --border-subtle |
| --font-*        | Section 3 > Font Family | --font-primary, --font-mono |
| --text-size-*   | Section 3 > Hierarchy | --text-size-display-xl, --text-size-h1 |
| --font-weight-* | Section 3 > Hierarchy | --font-weight-display, --font-weight-body |
| --tracking-*    | Section 3 > Letter Spacing | --tracking-display, --tracking-body |
| --space-*       | Section 5 > Spacing | --space-1 (4px) through --space-16 (64px) |
| --radius-*      | Section 5 > Radius | --radius-sm, --radius-card, --radius-pill |
| --shadow-*      | Section 6 > Elevation | --shadow-1 through --shadow-dialog |

---

## Standard Spacing Scale

Always use multiples of 4px:
  --space-px: 1px
  --space-0-5: 2px
  --space-1: 4px
  --space-1-5: 6px
  --space-2: 8px
  --space-3: 12px
  --space-4: 16px
  --space-5: 20px
  --space-6: 24px
  --space-8: 32px
  --space-10: 40px
  --space-12: 48px
  --space-16: 64px
  --space-20: 80px
  --space-24: 96px

---

## Standard Elevation Scale

  --shadow-1: minimal micro lift
  --shadow-2: surface/card level
  --shadow-3: popovers/dropdowns
  --shadow-4: modal/dialog
  --shadow-focus: keyboard focus ring

---

## Token File Header (always include)

/* ============================================================
 * DESIGN TOKENS - Generated from DESIGN.md
 * ============================================================
 * Source of truth: DESIGN.md in project root
 * Update DESIGN.md first, then regenerate this file.
 * Do not edit tokens directly - changes will be overwritten.
 * Version: [version]
 * Last updated: [date]
 * ============================================================ */

---

## Dark/Light Mode Implementation

For designs with both themes, use CSS color-scheme:

:root { /* light mode defaults */ }
[data-theme=dark] { /* dark mode overrides */ }

Or use prefers-color-scheme:

@media (prefers-color-scheme: dark) { :root { /* dark overrides */ } }

Each token that changes between themes gets two definitions.
Tokens that are identical in both themes are defined once in :root.

---

## Token Audit Procedure

When auditing whether codebase matches DESIGN.md:

1. Extract all CSS values from codebase
2. Check each against corresponding token in tokens.css
3. Flag hardcoded values that should be token references
4. Flag tokens that exist in tokens.css but are unused
5. Flag tokens used but not defined

Output: Token Coverage Report with % coverage and violation list.
