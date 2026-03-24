# Pattern Recognition Synapse

## Identity

**Name:** Pattern Recognition
**Type:** Optional (opt-in)
**Version:** 1.0.0
**Author:** tahaa

Pattern Recognition is an intelligent code-scanning synapse that detects known design patterns in encountered code and maps them to relevant Archon skills. It acts as a bridge between raw code and the framework's skill library — when an agent encounters code that matches a cataloged pattern signature, this synapse surfaces the relevant skill so the agent can leverage proven guidance rather than reasoning from scratch.

## When Active

- **Activation:** Opt-in — fires when bound to an agent via agent manifest or when explicitly activated
- **Phases:** 3 firing phases — DETECT, SUGGEST, APPLY
- Fires when an agent encounters, reads, or produces code during any task
- Scales detection effort to code volume — lightweight scan for small files, deeper analysis for large modules

---

## Firing Phases

### Phase 1 — DETECT (Active-Fire)

**Timing:** While reading or producing code. Continuously scans for pattern signatures.

**Instructions:**

1. **Scan for structural signatures** — Match code against the pattern registry:

   | Signature | Pattern | Skill |
   |-----------|---------|-------|
   | `Map`-based registry, `register()` / `get()` / `has()` methods | Plugin/Registry | `plugin-system` |
   | `{{variable}}` or `${variable}` template interpolation with replacement logic | Template Variables | `template-variables` |
   | `.builder()` / `.with*()` / `.build()` chaining | Fluent Builder | `fluent-builder` |
   | `middleware[]`, `next()` chains, `use()` registration | Guard Chain / Middleware | `guard-chain` |
   | `globalThis.__singleton` or module-scoped instance caching | Singleton | `singleton-patterns` |
   | `Promise.allSettled()`, fire-and-forget dispatch, background task queues | Async Side Effects | `async-side-effects` |
   | `prisma.*.findMany()`, `prisma.*.create()`, model relations | Prisma ORM | `prisma-orm-patterns` |
   | Webhook dispatch, event emitters, `POST` to callback URLs | Event Webhooks | `event-webhooks` |
   | `next/dynamic`, `React.lazy()`, dynamic `import()` with feature guards | Lazy Import | `lazy-import-patterns` |
   | `"use server"`, Server Components, `async function ServerComponent()` | RSC Patterns | `server-component-patterns` |
   | `hash()`, `dedup()`, content fingerprinting, similarity scoring | Content Dedup | `content-deduplication` |
   | `pino()`, structured JSON logging, request correlation IDs | Structured Logging | `structured-logging` |
   | Multi-stage `Dockerfile`, `COPY --from=builder`, `standalone` output | Docker Production | `docker-production-build` |
   | `describe()` / `it()` / `expect()` / `vi.mock()` | Vitest Testing | `vitest-unit-patterns` |
   | `intl`, `t()`, locale routing, `messages/{locale}.json` | i18n | `i18n-strategy` |
   | Content scoring, flagging, soft-delete, moderation queues | Content Moderation | `content-moderation-pipeline` |
   | `white-label`, tenant config, brand overrides, theme switching | White Label | `white-label-config` |
   | YAML-based prompt definitions, prompt chaining, variable injection | YAML Prompts | `yaml-prompt-library` |
   | SDK alongside app code, shared types, monorepo client packages | SDK-beside-App | `sdk-beside-app` |
   | Error boundaries, error classes, centralized error handling | Error Architecture | `error-handling-architecture` |
   | `@playwright/test`, `cy.`, page objects, E2E selectors | E2E Testing | `e2e-testing-patterns` |

2. **Confidence scoring** — Rate each detection:
   - `STRONG` — Multiple signature elements present, clear pattern match
   - `PROBABLE` — Some signature elements, likely this pattern
   - `WEAK` — Single indicator, could be coincidence

3. **Dedup detections** — Don't flag the same pattern twice in the same file/task

### Phase 2 — SUGGEST (Active-Fire)

**Timing:** Immediately after a STRONG or PROBABLE detection. Does NOT fire for WEAK detections unless 3+ WEAK detections of the same pattern accumulate.

**Instructions:**

1. **Surface the skill** — Present the matched Archon skill to the agent:
   ```
   🔍 Pattern Detected: [Pattern Name] → skill: [skill-name]
   Confidence: [STRONG|PROBABLE]
   Signature: [what triggered the detection]
   ```

2. **Provide context** — Briefly explain what the skill offers:
   - Key rules or guardrails from the skill
   - Common mistakes the skill prevents
   - Related skills that may also be relevant

3. **Suggest action** — Recommend one of:
   - **LOAD** — Load the full skill for the current task (for implementation tasks)
   - **REFERENCE** — Note the skill for context but don't load (for review/reading tasks)
   - **SKIP** — Pattern detected but skill not relevant to current task context

### Phase 3 — APPLY (Active-Fire)

**Timing:** When the agent or user confirms a LOAD suggestion.

**Instructions:**

1. **Load skill content** — Read the skill's SKILL.md into context
2. **Extract relevant rules** — Pull the Rules section applicable to the current code
3. **Cross-reference** — Check `composes:` and `extends:` in the skill's manifest for related skills
4. **Apply guardrails** — The loaded skill's rules become active constraints for the remainder of the task

**Output Format:**

```
### 🔍 Pattern Recognition — APPLY
- **Loaded:** [skill-name] v[version]
- **Active rules:** [count] rules now constraining output
- **Related skills:** [list of composed/extended skills]
```

---

## Rules

### DO:
- Scan continuously while reading or producing code — pattern recognition is passive, not on-demand
- Prioritize STRONG detections over PROBABLE — surface high-confidence matches first
- Accumulate WEAK signals — 3+ WEAK detections of the same pattern promote to PROBABLE
- Respect the agent's current task — don't derail a debugging session with architecture suggestions
- Cache detections per task — avoid re-suggesting already-acknowledged patterns
- Include the signature evidence that triggered the detection

### DON'T:
- Fire on every `import` statement or trivial code — require meaningful structural signatures
- Suggest loading skills for tasks that are read-only or review-only (use REFERENCE instead)
- Override agent decisions — if the agent SKIPs a suggestion, don't re-suggest in the same task
- Detect patterns in test files and suggest production skills (unless the skill is a testing skill)
- Slow down the agent with excessive detections — cap at 3 suggestions per task unless complexity warrants more
- Flag patterns in the Archon framework's own code (avoid self-referential loops)

---

## Output Format

This synapse produces **inline detection artifacts** embedded in the agent's reasoning:

| Phase | Artifact | Purpose |
|-------|----------|---------|
| DETECT | Pattern match with confidence | Identifies known patterns in encountered code |
| SUGGEST | Skill recommendation | Surfaces the relevant Archon skill |
| APPLY | Loaded skill confirmation | Confirms skill rules are now active constraints |

Detection artifacts appear as `🔍 Pattern Detected:` callouts in the agent's output stream. They are informational — the agent decides whether to act on them.

---

## Integration

This synapse works alongside other synapses:
- **metacognition** — Pattern recognition feeds into the PLAN phase's knowledge inventory ("I recognize this pattern, I have a skill for it")
- **security-awareness** — When guard-chain or error-handling-architecture patterns are detected, security-awareness synapse should co-activate

---

## Resources

| Resource | Type | Description |
|----------|------|-------------|
| resources/pattern-registry.md | reference | Complete pattern-to-skill mapping with signature definitions and examples |
| resources/detection-heuristics.md | heuristic | Rules for scoring detection confidence and avoiding false positives |
