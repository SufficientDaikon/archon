# Using Archon — The Gatekeeper

> **Type:** Meta-process (always active)  
> **Priority:** CRITICAL — fires before every response  
> **Category:** Enforcement

## Iron Law

```
CHECK FOR APPLICABLE SKILLS BEFORE EVERY RESPONSE — EVEN A 1% CHANCE MEANS INVOKE
```

## Purpose

This meta-skill ensures that every agent response is informed by the relevant skills in the Archon framework. It prevents the common failure mode where agents "go rogue" and ignore available skills, processes, and guardrails.

## The Protocol

Before responding to ANY user message:

1. **SCAN** — Review the user's request against all installed skills
2. **MATCH** — Identify which skills apply (even partially — 1% chance = invoke)
3. **PRIORITIZE** — Process skills before implementation skills:
   - Design skills (brainstorming) → before planning
   - Planning skills (writing-plans) → before implementation
   - Testing skills (TDD) → before writing production code
   - Verification skills → before claiming completion
4. **INVOKE** — Read and follow the matched skill(s)
5. **RESPOND** — Now respond, guided by the skill content

## Skill Priority Order

```
1. brainstorming           → Design FIRST (any creative/feature work)
2. using-git-worktrees     → Isolate workspace (before implementation)
3. writing-plans           → Break into TDD tasks (before coding)
4. subagent-driven-dev     → Execute with subagents + 2-stage review
5. executing-plans         → Fallback if no subagents
6. test-driven-development → RED-GREEN-REFACTOR (any code)
7. verification-before-completion → Before claiming "done"
8. finishing-a-dev-branch  → Merge / PR / Cleanup
```

## Red Flags — Thoughts That Mean STOP

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "I can check git/files quickly" | Files lack conversation context. Check for skills. |
| "This doesn't need a formal skill" | If a skill exists, use it. Period. |
| "I already know how to do this" | Your knowledge may be outdated. Skills are current. |

## Subagent Exception

Subagents dispatched for specific tasks (implementer, reviewer, etc.) do NOT run this meta-check — they have focused jobs with pre-assigned skills. Only the main orchestrating agent uses this gatekeeper.

## Integration

- **Hooks:** The `session-start` hook injects this skill's content at session beginning
- **Synapses:** Works with `anti-rationalization` to prevent skill-skipping excuses
- **Pipeline:** Not a pipeline step — it's a pre-step check that runs everywhere
