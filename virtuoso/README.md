# Virtuoso Engine

The cognitive kernel for Archon-powered AI sessions.

## What It Is

Virtuoso is a single XML system prompt (`virtuoso.xml`) that gets loaded into every Claude Code session through a `SKILL.md` wrapper. It provides:

1. **5 Cognitive Synapses** — always-on reasoning protocols that fire automatically:
   - **Metacognition** — plan before acting, monitor confidence, reflect on quality
   - **Anti-Rationalization** — 10 Iron Laws that prevent cutting corners
   - **Sequential Thinking** — structured step-by-step reasoning
   - **Pattern Recognition** — detects code patterns and surfaces relevant Archon skills
   - **Security Awareness** — catches OWASP Top 10 during code production

2. **The Virtuoso Loop** — a 5-phase execution model:
   ```
   ORIENT → PLAN → BUILD → EVALUATE → SHIP
   ```
   Scaled by complexity: trivial tasks skip PLAN/EVALUATE entirely.

3. **Model-Aware Scaffolding** — every component is tagged with the model capability it compensates for. When stronger models arrive, stress-test and strip what's no longer load-bearing.

## How It Gets Installed

```bash
archon init          # Detects platforms + installs Virtuoso
archon init --force  # Reinstalls everything
```

The `init` command:
1. Detects AI platforms (Claude Code, Copilot CLI, Cursor, etc.)
2. Copies `virtuoso.xml` wrapped in `SKILL.md` → `~/.claude/skills/virtuoso/SKILL.md`
3. Installs all 5 synapses → `~/.claude/skills/_synapses/`
4. Adds a Virtuoso marker to `CLAUDE.md`

## Design Philosophy

> "Every harness component encodes an assumption about what the model can't do alone.
> Stress-test those assumptions."
> — Anthropic Labs, Harness Design for Long-Running Agents

- **Trust the model first.** Only scaffold where it demonstrably fails.
- **Synapses over scripts.** Reasoning quality > task workflow.
- **Minimum viable ceremony.** Scale process to complexity.
- **Evaluate like a stranger.** Role-switch to evaluator, grade against criteria.
- **Evolve or die.** Strip what models outgrow, add for new capability edges.

## File Structure

```
virtuoso/
  virtuoso.xml     ← The engine (this is the important file)
  README.md        ← You are here
```

## Evolving the Engine

Edit `virtuoso.xml` directly. The sections are independent and can be upgraded individually:

| Section | Purpose | When to change |
|---------|---------|----------------|
| `<identity>` | Core principles | When philosophy shifts |
| `<synapses>` | Reasoning protocols | When adding/tuning cognitive behaviors |
| `<execution-model>` | The Virtuoso Loop | When the task flow needs adjustment |
| `<context-strategy>` | Context window management | When context patterns change |
| `<model-scaling>` | Complexity tiers + model assumptions | When a new model lands |
| `<escape-hatches>` | Failure handling | When stuck patterns change |
| `<extensions>` | Integration points | When adding new component types |

After editing, reinstall with `archon init --force`.

## Version History

- **v1.0.0** — Initial release. All 5 synapses, Virtuoso Loop, model-aware scaling.
