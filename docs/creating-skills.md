# Creating Skills

## Skill Anatomy

Every Archon skill lives in its own directory under `skills/` and follows this structure:

```
skills/my-skill/
├── SKILL.md           # Instructions the AI agent follows
├── manifest.yaml      # Metadata, triggers, dependencies
├── resources/         # Reference materials (cheat sheets, style guides)
├── examples/          # Sample interactions showing expected behavior
├── templates/         # Output templates
├── tests/cases/       # Validation test cases
└── overrides/         # Platform-specific instruction overrides
```

## Step 1: manifest.yaml

The manifest declares everything about your skill except the instructions themselves:

```yaml
name: my-awesome-skill
version: 1.0.0
description: "What this skill does in one sentence"
author: your-name
license: MIT

platforms: [claude-code, copilot-cli, cursor, windsurf, antigravity]

tags: [domain, category, keywords]

triggers:
  keywords: ["exact phrase 1", "exact phrase 2"]
  patterns: ["pattern with * wildcards"]

priority: P2
```

### Trigger Design Tips

- **Be specific**: "create React component" is better than "create component"
- **Avoid conflicts**: Check existing skills' triggers before choosing yours
- **Use patterns**: `"review * code"` matches "review Python code", "review my code", etc.

## Step 2: SKILL.md

This is the instruction file the AI agent reads. Required sections:

### Identity

Who is this skill? What's its role and personality?

### When to Use

Trigger conditions, keywords, and anti-patterns (when NOT to use).

### Workflow

Step-by-step process the agent follows.

### Rules

DO and DON'T lists — guardrails for the agent.

### Output Format

What the skill produces, in what format, saved where.

### Handoff

What happens after the skill completes — next agent, artifact, user instruction.

## Step 3: Resources (Optional but Recommended)

Add reference materials the agent can consult:

- `resources/cheat-sheet.md` — Quick reference for the domain
- `resources/style-guide.md` — Standards the output should follow
- `resources/decision-tree.md` — Logic for complex decisions
- `resources/lookup-table.md` — Values the agent should look up, not guess

Declare them in `manifest.yaml`:

```yaml
resources:
  - path: resources/cheat-sheet.md
    type: cheat-sheet
    load: always
```

## Step 4: Tests

Add test cases in `tests/cases/`:

```yaml
# tests/cases/basic.yaml
name: "Basic skill test"
input: "User prompt that should trigger this skill"
expected:
  contains: ["expected output pattern"]
  not_contains: ["things that should NOT be in output"]
  sections: ["required output sections"]
```

## Step 5: Validate

```bash
python scripts/validate.py skills/my-awesome-skill
```

This checks:

- manifest.yaml completeness and schema compliance
- SKILL.md required sections present
- Trigger uniqueness (no conflicts with other skills)
- Resources exist and are accessible
- Tests are parseable

## Step 6: Platform Overrides (Optional)

If a skill needs different behavior on specific platforms:

```
overrides/cursor.md     — Cursor-specific instructions
overrides/windsurf.md   — Windsurf-specific instructions
```

These are merged with the base SKILL.md during adapter transformation.

## Self-Customization Skills

Archon includes AI-guided skills for creating new skills, bundles, and agents:

### The `add-skill` Skill

Instead of manually following these steps, tell your AI assistant:

> "Follow the add-skill skill to create a new skill for [domain]"

The `add-skill` skill provides:
- Interactive checklist guiding you through each step
- Validation checks at each stage
- Template generation
- Trigger conflict detection
- Automatic validation and installation

### Example Advanced Skills

See these skills as examples of advanced patterns:

- **`complexity-router`** — Classifies task complexity and routes to optimal model tier
- **`knowledge-sources`** — Integrates external knowledge repositories

## Generator Tool Pattern

For real-time status visualization, use the async generator pattern:

```python
async def process_task():
    yield {"status": "loading", "message": "Initializing..."}
    # Do work
    yield {"status": "processing", "message": "Analyzing code..."}
    # More work
    yield {"status": "done", "result": output}
```

This pattern enables the AI assistant to show live progress updates. See `skills/_template/resources/tool-pattern.md` for the full specification.
