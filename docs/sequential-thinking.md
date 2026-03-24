# Archon v2.0 — Sequential Thinking Guide

## Overview

Sequential thinking is a structured reasoning protocol that forces agents to show their work before producing output. It prevents premature conclusions, missed edge cases, and shallow analysis by requiring explicit reasoning phases.

---

## The 4 Phases

Every non-trivial reasoning task passes through four phases in strict order:

```
DECOMPOSE → REASON → VALIDATE → SYNTHESIZE
```

### Phase 1: DECOMPOSE

Break the problem into atomic sub-problems. No reasoning yet — only structure.

```
[THINKING]
PHASE: DECOMPOSE

The user wants authentication for a REST API.

Sub-problems:
1. Authentication method selection (JWT vs session vs OAuth)
2. Token storage strategy (httpOnly cookie vs localStorage)
3. Password hashing algorithm selection
4. Session expiry and refresh logic
5. Route protection middleware
6. Error responses for auth failures
[/THINKING]
```

**Rules:**
- Each sub-problem must be independently addressable
- No sub-problem should contain hidden assumptions
- List at least 3 sub-problems (if fewer, the task may not need sequential thinking)

### Phase 2: REASON

Address each sub-problem with explicit reasoning. State trade-offs, not just conclusions.

```
[THINKING]
PHASE: REASON

1. Authentication method:
   - JWT: Stateless, scalable, but revocation is complex
   - Session: Server-side state, simpler revocation, but requires session store
   - Spec says "server-side sessions" → session-based auth (no choice to make)

2. Token storage:
   - httpOnly cookie: XSS-resistant, automatic sending
   - localStorage: Vulnerable to XSS, manual header management
   → httpOnly cookie (spec doesn't specify, defaulting to more secure option)

3. Password hashing:
   - bcrypt: Well-tested, configurable rounds, widely supported
   - argon2: Memory-hard, newer, better against GPU attacks
   → bcrypt with cost factor 12 (spec doesn't specify, using industry default)
[/THINKING]
```

**Rules:**
- Every sub-problem from DECOMPOSE must be addressed
- Trade-offs must be stated, not just the chosen option
- If the spec dictates the answer, cite the spec section

### Phase 3: VALIDATE

Check reasoning against constraints, edge cases, and the original problem statement.

```
[THINKING]
PHASE: VALIDATE

Checking against spec requirements:
✓ Server-side sessions — addressed in sub-problem 1
✓ HTTPS required — not yet addressed, adding to implementation
✗ Rate limiting on login — missed this, adding sub-problem

Edge cases:
- What if session store goes down? → Need fallback/error handling
- Concurrent sessions from same user? → Spec says "single session only"
- Session fixation attacks? → Regenerate session ID on login

Contradictions found: None
Missing requirements found: Rate limiting, HTTPS enforcement
[/THINKING]
```

**Rules:**
- Every spec requirement must have a ✓ or ✗ check
- At least 3 edge cases must be considered
- Any ✗ items must be resolved before SYNTHESIZE

### Phase 4: SYNTHESIZE

Combine validated reasoning into a coherent plan or output. This is the only phase that produces user-facing content.

```
[THINKING]
PHASE: SYNTHESIZE

Implementation plan:
1. Session-based auth with express-session + Redis store
2. httpOnly cookies for session ID transport
3. bcrypt (cost 12) for password hashing
4. Session regeneration on login (fixation prevention)
5. Single-session enforcement (invalidate previous on new login)
6. Rate limiting: 5 attempts per 15 minutes per IP
7. HTTPS enforcement via middleware
8. Error responses: 401 (unauthenticated), 403 (unauthorized)
[/THINKING]
```

---

## [THINKING] Block Format

All reasoning is wrapped in `[THINKING]...[/THINKING]` blocks. These blocks:

1. **Are required** for any task rated complexity ≥ 3 (see metacognition scaling)
2. **Are captured** as part of the thinking trace artifact
3. **Are auditable** — reviewers can inspect the reasoning chain
4. **Are not shown** to end users unless they request the trace

### Format Rules

```
[THINKING]
PHASE: <DECOMPOSE|REASON|VALIDATE|SYNTHESIZE>

<structured reasoning content>
[/THINKING]
```

- One `[THINKING]` block per phase (4 blocks total for a full trace)
- Phases must appear in order — no skipping, no reordering
- Content inside blocks uses plain text and markdown lists
- No code execution inside thinking blocks — reasoning only

---

## Thinking Trace Schema

**File:** `schemas/thinking-trace.schema.yaml`

Thinking traces are persisted as structured artifacts for audit and debugging.

```yaml
type: object
required: [task_id, agent, phases, timestamp]
properties:
  task_id:
    type: string
    description: Unique identifier for the task
  agent:
    type: string
    description: Agent that produced the trace
  timestamp:
    type: string
    format: date-time
  phases:
    type: object
    required: [decompose, reason, validate, synthesize]
    properties:
      decompose:
        type: object
        required: [sub_problems]
        properties:
          sub_problems:
            type: array
            items:
              type: string
            minItems: 1
      reason:
        type: object
        required: [analysis]
        properties:
          analysis:
            type: array
            items:
              type: object
              required: [sub_problem, reasoning, decision]
              properties:
                sub_problem:
                  type: string
                reasoning:
                  type: string
                decision:
                  type: string
                trade_offs:
                  type: array
                  items:
                    type: string
      validate:
        type: object
        required: [spec_checks, edge_cases]
        properties:
          spec_checks:
            type: array
            items:
              type: object
              required: [requirement, status]
              properties:
                requirement:
                  type: string
                status:
                  type: string
                  enum: [pass, fail, partial]
          edge_cases:
            type: array
            items:
              type: object
              required: [case, mitigation]
              properties:
                case:
                  type: string
                mitigation:
                  type: string
          contradictions:
            type: array
            items:
              type: string
      synthesize:
        type: object
        required: [plan]
        properties:
          plan:
            type: array
            items:
              type: string
  metadata:
    type: object
    properties:
      complexity:
        type: integer
        minimum: 1
        maximum: 10
      duration_ms:
        type: integer
      token_count:
        type: integer
```

---

## BrowseComp Reasoning Pattern

For research-heavy tasks (codebase exploration, competitive analysis, information gathering), use the BrowseComp pattern instead of the standard 4-phase approach:

```
DETECT → HYPOTHESIZE → ENUMERATE → VERIFY → CONTINUE
```

### DETECT

Identify what information is needed and what is currently unknown.

```
[THINKING]
PHASE: DETECT
Need: How does the auth middleware work in this codebase?
Known: Express.js project, has middleware/ directory
Unknown: Which middleware handles auth, how sessions are managed
[/THINKING]
```

### HYPOTHESIZE

Form hypotheses about where the answer lives and what it looks like.

```
[THINKING]
PHASE: HYPOTHESIZE
H1: Auth middleware is in middleware/auth.js
H2: Session config is in config/session.js or app.js
H3: Passport.js is used (common in Express projects)
[/THINKING]
```

### ENUMERATE

List all sources to check and check them systematically.

```
[THINKING]
PHASE: ENUMERATE
Sources to check:
1. middleware/*.js — grep for "auth", "session", "passport"
2. package.json — check for passport, express-session deps
3. app.js — check middleware registration order
4. routes/*.js — check how auth is applied to routes
[/THINKING]
```

### VERIFY

Confirm or reject each hypothesis with evidence.

### CONTINUE

If questions remain, loop back to DETECT with updated knowledge. Stop when all unknowns are resolved.

---

## Complexity Scaling

The metacognition synapse (`synapses/metacognition.md`) determines how much thinking is required based on task complexity:

| Complexity | Thinking Required | Example |
|------------|-------------------|---------|
| 1-2 | None — direct response | "What's the project name?" |
| 3-4 | Lightweight — DECOMPOSE + SYNTHESIZE only | "Add a new API endpoint" |
| 5-6 | Standard — all 4 phases | "Implement auth system" |
| 7-8 | Deep — 4 phases + BrowseComp for research | "Design microservice architecture" |
| 9-10 | Exhaustive — 4 phases + multiple iterations | "Full-stack product from scratch" |

### Complexity Assessment

The agent self-assesses complexity at the start of each task:

```
[THINKING]
PHASE: COMPLEXITY_ASSESSMENT
Task: "Add pagination to the users endpoint"
Factors:
- Scope: Single endpoint modification (low)
- Ambiguity: Clear requirement (low)
- Dependencies: Database query changes, response format (medium)
- Risk: Could break existing clients (medium)
Assessment: Complexity 4 → Lightweight thinking (DECOMPOSE + SYNTHESIZE)
[/THINKING]
```

---

## Pipeline Integration

Thinking traces are first-class artifacts in the pipeline system.

### Traces as Audit Artifacts

Every pipeline step produces a thinking trace alongside its primary artifact. These traces are:

1. **Stored** in the pipeline state file under `thinking_traces[]`
2. **Validated** by `post_step.py` — missing traces for complexity ≥ 3 tasks cause validation failure
3. **Available** to downstream agents — the context-curator can include relevant traces in handoffs
4. **Reviewable** — the reviewer agent checks traces for reasoning quality

### Example: Trace in Pipeline State

```json
{
  "pipeline_id": "sdd-abc123",
  "step": "implement-auth",
  "thinking_trace": {
    "task_id": "impl-auth-001",
    "agent": "implementer",
    "phases": {
      "decompose": { "sub_problems": ["..."] },
      "reason": { "analysis": ["..."] },
      "validate": { "spec_checks": ["..."], "edge_cases": ["..."] },
      "synthesize": { "plan": ["..."] }
    },
    "metadata": {
      "complexity": 6,
      "duration_ms": 4500
    }
  }
}
```

### Reviewer Trace Inspection

The reviewer agent checks thinking traces as part of its compliance review:

- **Completeness:** All 4 phases present for tasks rated ≥ 5
- **Spec alignment:** Every spec requirement appears in the VALIDATE phase
- **Reasoning quality:** REASON phase shows trade-offs, not just conclusions
- **Edge coverage:** VALIDATE phase lists ≥ 3 edge cases for tasks rated ≥ 5

Traces with gaps are flagged as `INCOMPLETE_REASONING` in the review report.
