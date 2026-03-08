# OMNISKILL Architecture

## Design Principles

1. **Universal Format** — Write once, deploy everywhere
2. **Composability** — Skills compose into bundles; agents compose into pipelines
3. **Separation of Concerns** — Skills = knowledge, Agents = orchestration, Pipelines = workflow
4. **Self-Improvement** — The system uses its own tools to improve itself
5. **Platform Agnostic** — Adapters handle platform differences

## Layer Architecture

```
┌─────────────────────────────────────────────┐
│                PIPELINES                     │
│  (Multi-agent workflows with branching)      │
├─────────────────────────────────────────────┤
│                AGENTS                        │
│  (Personas with skill bindings & handoffs)   │
├─────────────────────────────────────────────┤
│               BUNDLES                        │
│  (Domain kits with meta-skill routing)       │
├─────────────────────────────────────────────┤
│               SKILLS                         │
│  (Universal instructions + resources)        │
├─────────────────────────────────────────────┤
│              ADAPTERS                        │
│  (Platform-specific transformations)         │
├─────────────────────────────────────────────┤
│     Claude Code │ Copilot │ Cursor │ ...     │
└─────────────────────────────────────────────┘
```

## Data Flow

1. **User request** → matched to pipeline trigger or agent
2. **Agent** → selects skill(s) based on trigger matching
3. **Skill** → provides instructions + resources to the AI model
4. **Output** → formatted per skill's output contract
5. **Handoff** → passed to next agent in pipeline (if applicable)

## Validation Chain

```
manifest.yaml  →  schema validation  →  SKILL.md section check
     ↓                                        ↓
trigger check  →  uniqueness across repo  →  resource existence
     ↓                                        ↓
composition  →  circular dependency check  →  PASS / FAIL
```
