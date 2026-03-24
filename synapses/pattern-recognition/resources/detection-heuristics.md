# Detection Heuristics — Confidence Scoring & False Positive Prevention

## Confidence Levels

### STRONG (auto-surface)
- **Criteria:** 3+ signature elements from the same pattern co-occur in the same file or module
- **Example:** File contains `new Map()`, a `register()` function, and a `get()` accessor → STRONG match for `plugin-system`
- **Action:** Automatically trigger SUGGEST phase

### PROBABLE (auto-surface)
- **Criteria:** 2 signature elements from the same pattern, or 1 highly specific signature
- **Example:** File contains `vi.mock()` and `describe()` → PROBABLE match for `vitest-unit-patterns`
- **Action:** Automatically trigger SUGGEST phase

### WEAK (accumulate)
- **Criteria:** 1 generic signature element that could belong to multiple patterns
- **Example:** File contains `new Map()` alone → WEAK (could be any Map usage, not necessarily a plugin registry)
- **Action:** Do NOT trigger SUGGEST. Accumulate. If 3+ WEAK detections of the same pattern occur across the task, promote to PROBABLE.

---

## False Positive Prevention

### Rule 1: Context Matters
- A `describe()` in a `.test.ts` file → testing pattern (valid)
- A `describe()` in a non-test file → likely not a testing pattern (ignore)
- A `new Map()` in a utility function → generic usage (WEAK at best)
- A `new Map()` with `register()/get()/has()` → plugin registry (STRONG)

### Rule 2: File Type Awareness
| File type | Valid pattern detections | Suppress |
|-----------|------------------------|----------|
| `*.test.ts`, `*.spec.ts` | Testing patterns (vitest, e2e) | Production patterns |
| `*.md`, `*.yaml` | YAML prompts, documentation | Code patterns |
| `Dockerfile` | Docker production | All non-Docker patterns |
| `schema.prisma` | Prisma ORM | All non-Prisma patterns |
| `*.tsx`, `*.jsx` | UI patterns, server components | Backend-only patterns |

### Rule 3: Framework Self-Reference
- Do NOT detect patterns in Archon's own framework files (`skills/`, `synapses/`, `agents/`, `pipelines/`, `bundles/`)
- The framework defines these patterns — detecting them in the framework code creates noise

### Rule 4: Import-Only Detection
- Seeing `import { PrismaClient } from '@prisma/client'` alone is WEAK
- Seeing actual query usage (`prisma.user.findMany()`) is STRONG
- Imports indicate potential pattern usage but are not sufficient alone

### Rule 5: Comment/String Exclusion
- Pattern signatures inside comments or string literals should be ignored
- `// TODO: add middleware` is NOT a guard-chain detection
- `const msg = "use server"` is NOT a server component detection (must be a directive)

---

## Detection Caps

| Scope | Maximum suggestions | Rationale |
|-------|-------------------|-----------|
| Per file | 2 | Avoid overwhelming on complex files |
| Per task | 3 (default) | Keep focus on primary task |
| Per task (complex) | 5 | Allow more for architecture-level tasks |
| Same pattern | 1 per task | Never re-suggest an acknowledged pattern |

---

## Promotion Rules

| Condition | Action |
|-----------|--------|
| 3+ WEAK same pattern | Promote to PROBABLE, trigger SUGGEST |
| PROBABLE + user confirms | Promote to STRONG for future tasks |
| User SKIPs a pattern | Suppress for remainder of task |
| STRONG match in test file for non-test skill | Demote to WEAK |

---

## Edge Cases

### Multi-Pattern Files
When a file matches multiple patterns (e.g., a route handler with middleware AND Prisma queries AND structured logging):
1. Surface the most relevant pattern for the current task first
2. Mention related patterns as secondary suggestions
3. Do not exceed the per-file cap (2 suggestions)

### Partial Pattern Matches
When code partially matches a pattern but uses a non-standard approach:
1. Flag as PROBABLE, not STRONG
2. Note the deviation in the suggestion
3. The skill may still provide useful guardrails even for non-standard implementations

### Generated/Vendored Code
- Skip pattern detection in `node_modules/`, `vendor/`, `.next/`, `dist/`, `build/` directories
- These contain third-party code that should not trigger skill suggestions
