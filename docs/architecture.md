# OMNISKILL Architecture

> Inspired by [Vercel's Knowledge Agent Template](https://vercel.com/templates/ai) — extended with complexity routing, knowledge source integration, and self-customization capabilities.

## Design Principles

1. **Universal Format** — Write once, deploy everywhere
2. **Composability** — Skills compose into bundles; agents compose into pipelines
3. **Separation of Concerns** — Skills = knowledge, Agents = orchestration, Pipelines = workflow
4. **Self-Improvement** — The system uses its own tools to improve itself
5. **Platform Agnostic** — Adapters handle platform differences
6. **Intelligent Routing** — Complexity-based task classification and model selection

## Layer Architecture

```
                    USER REQUEST
                         ↓
         ┌───────────────────────────────┐
         │   COMPLEXITY ROUTER (P0)      │  ← Prompt Library
         │  (Task classification + model  │
         │   selection + routing logic)   │
         └───────────────────────────────┘
                         ↓
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
│               SKILLS                         │  ← Knowledge Sources
│  (Universal instructions + resources)        │     (GitHub, local,
├─────────────────────────────────────────────┤      URLs, APIs)
│              ADAPTERS                        │
│  (Platform-specific transformations)         │
├─────────────────────────────────────────────┤
│     Claude Code │ Copilot │ Cursor │ ...     │
└─────────────────────────────────────────────┘
                         ↓
                    SDK / CLI
```

## Data Flow

1. **User request** → **Complexity Router** classifies task
2. **Router decision**:
   - Complexity level: trivial → simple → moderate → complex → expert
   - Model tier: fast/cheap → standard → premium
   - Target: skill, agent, or pipeline
3. **Knowledge source lookup** (if needed) → fetches external docs/data
4. **Agent/Pipeline execution** → selects skill(s) based on trigger matching
5. **Skill execution** → provides instructions + resources + knowledge to the AI model
6. **Output** → formatted per skill's output contract
7. **Handoff** → passed to next agent in pipeline (if applicable)

## Cross-Cutting Concerns

### Prompt Library (`prompts/`)

Reusable prompt components used throughout the system:

- **`router.md`** — Complexity classification prompts
- **`system.md`** — Master OMNISKILL system prompt
- **`shared.md`** — Common formatting, citations, error handling
- **`personas/*.md`** — Persona-specific prompt templates

### Knowledge Sources (`skills/knowledge-sources/`)

External knowledge integration layer:

- **File-based search** — grep, find, cat (no vector DB required)
- **Content normalization** — keeps .md, .yaml, .json, .txt
- **Sync system** — keeps sources up to date
- **Config template** — `templates/source-config.yaml`

### SDK Access Layer (`sdk/omniskill.py`)

Programmatic interface to OMNISKILL:

```python
class OmniSkill:
    def list_skills() -> List[Skill]
    def list_bundles() -> List[Bundle]
    def get_skill(name: str) -> Skill
    def route(request: str) -> Route
    def install(platform: str, bundle: str)
    def validate() -> List[Error]
    def sync_sources()
    def health_check() -> Report
```

### Admin Dashboard (`scripts/admin.py`)

Operational tooling:

- `--stats` — Framework statistics
- `--errors` — Validation error report
- `--sources` — Knowledge source status
- `--sync` — Trigger source sync
- `--report` — Full health report

## Validation Chain

```
manifest.yaml  →  schema validation  →  SKILL.md section check
     ↓                                        ↓
trigger check  →  uniqueness across repo  →  resource existence
     ↓                                        ↓
composition  →  circular dependency check  →  PASS / FAIL
```
