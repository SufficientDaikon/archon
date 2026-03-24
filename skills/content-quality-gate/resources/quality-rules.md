# Quality Rules Reference

> Extracted from prompts.chat `packages/prompts.chat/src/quality/index.ts`.

## Core API

```typescript
export interface QualityResult {
  score: number;           // 0-1 overall score
  isValid: boolean;        // score >= threshold
  issues: Issue[];         // problems found
  suggestions: string[];   // actionable improvements
  dimensions: Record<string, number>; // per-dimension scores
}

export interface Issue {
  id: string;
  dimension: string;
  severity: "error" | "warning" | "info";
  message: string;
  suggestion: string;
}

export interface Rule {
  id: string;
  dimension: string;
  weight: number;
  check: (content: string) => boolean;
  message: string;
  suggestion: string;
}

export function check(content: string, options?: { threshold?: number }): QualityResult;
export function validate(content: string, customRules?: Rule[]): boolean;
export function isValid(content: string): boolean;
export function getSuggestions(content: string): string[];
```

## Common Rules by Content Type

### Prompt Quality Rules

| Rule ID | Dimension | Check | Suggestion |
|---------|-----------|-------|------------|
| `min-length` | Length | `content.length >= 20` | "Add more detail — prompts under 20 chars are too vague" |
| `max-length` | Length | `content.length <= 10000` | "Shorten your prompt — very long prompts lose focus" |
| `has-task` | Specificity | contains an imperative verb | "Start with a clear action verb (write, analyze, create)" |
| `no-vague` | Clarity | no "stuff", "things", "etc" | "Replace vague words with specific terms" |
| `has-context` | Completeness | has role or context setting | "Add context: who should the AI act as?" |
| `has-format` | Structure | specifies output format | "Specify the desired output format (list, table, code)" |
| `no-please` | Efficiency | no excessive politeness | "Remove unnecessary politeness — be direct with AI" |

### Documentation Quality Rules

| Rule ID | Dimension | Check | Suggestion |
|---------|-----------|-------|------------|
| `has-title` | Structure | starts with `# ` heading | "Add a title heading" |
| `has-sections` | Structure | has 2+ `## ` headings | "Break content into sections with headings" |
| `has-examples` | Completeness | contains code fences | "Add code examples" |
| `no-todos` | Completeness | no TODO/FIXME/HACK | "Resolve all TODO comments before publishing" |
| `readable-sentences` | Clarity | avg sentence < 25 words | "Break long sentences into shorter ones" |

## Scoring Implementation

```typescript
const DIMENSIONS = {
  length:       { weight: 0.15 },
  clarity:      { weight: 0.25 },
  specificity:  { weight: 0.25 },
  structure:    { weight: 0.20 },
  completeness: { weight: 0.15 },
};

function score(content: string, rules: Rule[]): QualityResult {
  const issues: Issue[] = [];
  const dimensionScores: Record<string, number[]> = {};

  for (const rule of rules) {
    const passed = rule.check(content);
    if (!dimensionScores[rule.dimension]) dimensionScores[rule.dimension] = [];
    dimensionScores[rule.dimension].push(passed ? 1 : 0);
    if (!passed) {
      issues.push({
        id: rule.id,
        dimension: rule.dimension,
        severity: rule.weight > 0.2 ? "error" : "warning",
        message: rule.message,
        suggestion: rule.suggestion,
      });
    }
  }

  // Weighted average across dimensions
  let totalScore = 0;
  const dimensions: Record<string, number> = {};
  for (const [dim, config] of Object.entries(DIMENSIONS)) {
    const scores = dimensionScores[dim] || [1];
    const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
    dimensions[dim] = avg;
    totalScore += avg * config.weight;
  }

  return {
    score: totalScore,
    isValid: totalScore >= 0.6,
    issues,
    suggestions: issues.map((i) => i.suggestion),
    dimensions,
  };
}
```

## AI Tier Integration

```yaml
# quality-check.prompt.yml
name: quality-check
model: gpt-4o-mini
messages:
  - role: system
    content: |
      You are a content quality evaluator. Score the following content on:
      1. Clarity (0-10): Is it easy to understand?
      2. Specificity (0-10): Does it contain concrete details?
      3. Structure (0-10): Is it well-organized?
      4. Completeness (0-10): Does it cover the topic adequately?
      Return JSON: { scores: { clarity, specificity, structure, completeness }, overall: number, suggestions: string[] }
  - role: user
    content: "Evaluate this content:\n\n{{content}}"
```
