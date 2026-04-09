# github-expert

**Meta-Skill Coordinator for GitHub Documentation and PR Quality**

## Purpose

Orchestrates GitHub-facing content creation and quality assurance, combining deep GitHub Flavored Markdown expertise with a structured PR review pipeline. Ensures all documentation and pull requests meet professional standards with proper formatting, visual hierarchy, and citation integrity.

## Content Lifecycle Phases

GitHub content follows a create-then-validate workflow:

```
1. CONTENT CREATION   -> github-markdown-mastery
2. PR QUALITY AUDIT   -> pr-quality-agent
```

---

## Routing Logic

### 1. Markdown and Documentation -> **github-markdown-mastery**

**Trigger keywords:** Markdown, GFM, README, documentation, Mermaid diagram, badges, shields.io, alerts, admonitions, HTML in Markdown, table formatting, GitHub Pages

**Use when:**
- Writing or improving README files
- Creating documentation with GitHub Flavored Markdown
- Building Mermaid diagrams (flowcharts, sequence, state, ER)
- Adding badges and shields to repositories
- Using GitHub-specific features (alerts, task lists, footnotes)
- Formatting tables, code blocks, and collapsible sections
- Working with the 63 allowed HTML elements in GitHub Markdown
- Creating GitHub Pages content

**Deliverable:** Production-quality Markdown documents with full GFM feature usage

**Example requests:**
- "Write a README for this project"
- "Add a Mermaid architecture diagram"
- "Create badges for build status and coverage"
- "Format this documentation with GitHub alerts"
- "Build a collapsible FAQ section"

---

### 2. Pull Request Quality -> **pr-quality-agent**

**Trigger keywords:** PR body, pull request review, PR quality, citations, scope clarity, visual hierarchy, self-review, PR audit, PR description, changelog

**Use when:**
- Writing pull request descriptions
- Auditing PR body quality against the 7-rule framework
- Adding citations and source references to PRs
- Ensuring scope clarity (in-scope, out-of-scope, unchanged)
- Building visual hierarchy with badges, alerts, and Mermaid in PRs
- Self-reviewing PRs before submission
- Structuring PR descriptions with progressive disclosure

**Deliverable:** Audit-compliant PR description with citations, scope, and visual hierarchy

**Example requests:**
- "Write a PR description for these changes"
- "Audit this PR body for quality"
- "Add citations to this pull request"
- "Review this PR description for completeness"
- "Structure this PR with scope clarity and visual hierarchy"

---

## Core GitHub Content Workflow

### Full Documentation Pipeline
```
github-markdown-mastery (create content)
    |
pr-quality-agent (validate PR describing the changes)
    |
DONE
```

### Documentation-Only Pipeline
```
github-markdown-mastery (write docs)
    |
DONE
```

### PR-Only Pipeline
```
pr-quality-agent (write + audit PR)
    |
DONE
```

### Combined Pipeline (Docs + PR)
```
github-markdown-mastery (create/update docs)
    |
pr-quality-agent (write PR describing doc changes)
    |
DONE
```

---

## Decision Tree

```
What GitHub content are you creating?

+-- DOCUMENTATION OR MARKDOWN?
|   -> github-markdown-mastery
|
+-- PULL REQUEST DESCRIPTION?
|   -> pr-quality-agent
|
+-- BOTH (docs change with PR)?
    -> github-markdown-mastery THEN pr-quality-agent
```

---

## State-Based Routing

| Current State | Next Action | Routed To |
|---------------|-------------|-----------|
| **Need Documentation** | Write Markdown | github-markdown-mastery |
| **Docs Complete** | Write PR | pr-quality-agent |
| **PR Draft Ready** | Audit quality | pr-quality-agent |
| **Need Diagrams** | Add Mermaid | github-markdown-mastery |
| **PR Feedback Received** | Revise PR body | pr-quality-agent |
| **Need Badges** | Add shields | github-markdown-mastery |

---

## Skill Priority Matrix

| Task Category | Primary | Secondary |
|--------------|---------|-----------|
| **README Creation** | github-markdown-mastery | - |
| **PR Description** | pr-quality-agent | github-markdown-mastery |
| **Diagrams** | github-markdown-mastery | - |
| **Documentation** | github-markdown-mastery | pr-quality-agent |
| **PR Audit** | pr-quality-agent | - |
| **Badges/Shields** | github-markdown-mastery | - |

---

## Quality Gates

### Gate 1: Markdown Standards
- **Checked by:** github-markdown-mastery
- **Criteria:** Valid GFM syntax, proper heading hierarchy, accessible images with alt text, Mermaid renders correctly, tables well-formed
- **Pass -> Content ready for publication or PR**

### Gate 2: PR Quality (7-Rule Audit)
- **Checked by:** pr-quality-agent
- **Criteria:** Citations present, scope clarity defined, honest uncertainty flagged, progressive disclosure used, visual hierarchy applied, no unsourced claims, chunked corrections
- **Pass -> PR ready for review**

---

## Input/Output Contracts

### github-markdown-mastery
- **Input:** Content requirements, repository context, diagram needs
- **Output:** Production Markdown with GFM features, Mermaid diagrams, badges

### pr-quality-agent
- **Input:** Code changes, PR context, existing PR body (for audit)
- **Output:** Audit-compliant PR description or quality report

---

## Notes for AI Assistants

- **Use github-markdown-mastery first** when creating content that will be referenced in a PR
- **Always run pr-quality-agent** before submitting any non-trivial PR
- **Mermaid diagrams** should be verified for render compatibility on GitHub
- **Badge URLs** must use shields.io or equivalent stable services
- **Citations are mandatory** in PR descriptions -- no unsourced claims
- **Consult each SKILL.md** before applying skill knowledge
- **GitHub has 63 allowed HTML elements** -- use github-markdown-mastery for the full list
