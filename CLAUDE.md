# Archon — CLAUDE.md

Project-level context for Claude Code. Read this at the start of every session involving Archon code. Encodes verified facts, conventions, and hard-won lessons to prevent assumptions that cost work.

---

## What Archon Is

Archon is a **skills framework and cognitive harness for Claude Code**. It is NOT a guardrail system or a strict execution rail. The design philosophy:

> A harness, not a guardrail. Trust the AI to be smart enough. Help it manage knowledge, context, tools, and skills — don't dictate how to think.

Two surfaces:
1. **Runtime layer** (`hooks/claude/`) — Python scripts fired by Claude Code's hook system. Inject compact XML context into the prompt.
2. **Skill/Agent layer** (`skills/`, `agents/`, `synapses/`) — YAML-manifest components installed into `~/.claude/skills/`.

---

## Directory Map (source of truth)

```
omniskill/
├── src/archon/           # Core Python package (CLI + engine)
│   ├── cli.py            # Typer CLI entrypoint (python -m archon or archon)
│   ├── commands/         # One file per CLI command (install, validate, doctor, etc.)
│   ├── core/
│   │   ├── registry.py           # Parses archon.yaml → dataclasses (single source of truth)
│   │   ├── pipeline_engine.py    # Pipeline state machine executor
│   │   ├── pipeline_state.py     # Pipeline state persistence
│   │   ├── policy_engine.py      # Policy evaluation
│   │   ├── synapse_engine_v2.py  # Production synapse engine (v2 IS canon, v1 is legacy)
│   │   ├── synapse_router.py     # Auto-selects synapse config by tier/file_ext
│   │   ├── synapse_hardener.py   # CircuitBreaker + RetryPolicy + GracefulDegrader
│   │   ├── skill_mcp_schema.py   # skill → MCP tool descriptor conversion
│   │   ├── agent_cards.py        # A2A card generation
│   │   ├── installer.py          # Installs skills → ~/.claude/skills/
│   │   └── ...
│   └── synapses/         # Python implementations of each synapse check
├── sdk/archon.py         # Public SDK — ArchonSDK class, _validate_* methods
├── hooks/claude/         # Claude Code hook scripts (runtime injection layer)
│   ├── session_boot.py   # SessionStart: project/git state snapshot
│   ├── prompt_router.py  # UserPromptSubmit: classify + inject route XML
│   ├── guard_bash.py     # PreToolUse:Bash — dangerous command guard
│   ├── guard_write.py    # PreToolUse:Write|Edit|NotebookEdit — secret scanner
│   ├── quality_bash.py   # PostToolUse:Bash — exit code tracking into state
│   ├── quality_write.py  # PostToolUse:Write|Edit|NotebookEdit — file tracking
│   ├── completion_gate.py# Stop: blocks via sys.exit(2) if tests_passed=False
│   ├── agent_context.py  # SubagentStart: role-specific context slice
│   └── shared/
│       ├── classifier.py # Complexity tier + synapse activation (pure regex, no LLM)
│       ├── scanner.py    # Secret patterns + test/build command pattern lists
│       └── state.py      # Session state JSON load/save (~/.claude/archon-state.json)
├── skills/               # 99 skill directories (each: SKILL.md + manifest.yaml)
├── agents/               # 14 agent directories (each: manifest.yaml + agent.md)
├── synapses/             # 5 synapse dirs (each: SYNAPSE.md + manifest.yaml + resources/)
├── bundles/              # 16 bundle manifest dirs
├── pipelines/            # 9 pipeline YAML files
├── schemas/              # JSON/YAML schemas for all manifest types
├── tests/                # pytest suite — 583 passing as of 2026-04-25
├── archon.yaml           # Root manifest (DO NOT edit manually — use CLI)
└── pyproject.toml        # Python >=3.9, hatchling build, deps: typer pyyaml rich platformdirs
```

---

## Critical Data Types — Do Not Guess

### AgentCard (src/archon/core/registry.py)

AgentCard is a **dataclass**, not a dict. The attribute is `skills_provided` (snake_case).

WRONG (TypeError crash): `agent.card["skills-provided"]`
RIGHT: `agent.card.skills_provided`

All registry types (Skill, Agent, Bundle, Pipeline) are dataclasses — not dicts. Never subscript them.

### _validate_* return contract (sdk/archon.py)

Every _validate_* method MUST return exactly:

```python
{"valid": bool, "errors": list[str], "warnings": list[str]}
```

Missing "warnings" key breaks callers. This has been a silent regression before. Enforce it on any new validate method.

### _validate_bundle specifics

- Input path may be a directory — always do `p / "bundle.yaml"` if `p.is_dir()`
- Invalid skill refs → warnings (not errors)
- Missing file → valid=False
- Non-mapping YAML → valid=False

---

## Hook Injection Budget (measured, not guessed)

| Hook | Trigger | Injected |
|------|---------|----------|
| session_boot.py | Session start (once) | ~120 tokens of project/git XML |
| prompt_router.py | Every prompt | 20 tokens (TRIVIAL) → 400 tokens (EXPERT) |
| guard_bash.py | Pre-Bash | 0 tokens — blocks or allows, no injection |
| guard_write.py | Pre-Write/Edit/NotebookEdit | 0 tokens — blocks on secrets |
| quality_bash.py | Post-Bash | Updates state.json; ~50 tokens on failure only |
| quality_write.py | Post-Write/Edit/NotebookEdit | ~30 tokens file tracking |
| completion_gate.py | Stop | ~50 tokens on success; sys.exit(2) on test failure |
| agent_context.py | Per subagent | ~120 tokens role-scoped slice |

Max total per EXPERT prompt: ~520 tokens. This is intentional.

Skills and SYNAPSE.md files are NOT passively injected. They load only on explicit Skill tool invocation. The _synapses/ prefix in ~/.claude/skills/ prevents auto-listing by Claude Code.

---

## Synapse Activation Matrix (classifier.py)

| Synapse | Activates at |
|---------|-------------|
| metacognition | MODERATE, COMPLEX, EXPERT |
| anti-rationalization | MODERATE, COMPLEX, EXPERT |
| sequential-thinking | COMPLEX, EXPERT |
| security-awareness | Any tier when security/auth/vuln keywords match |
| pattern-recognition | EXPERT only |

IMPORTANT: The SYNAPSE_INSTRUCTIONS dict in classifier.py contains the actual compact text injected (~35 tokens each). The full SYNAPSE.md files are documentation only — they are NOT what gets injected into the prompt.

---

## Pipeline Engine Rules (pipeline_engine.py)

- state_vars from PipelineDefinition are seeded into state.accumulated as defaults at execute() start. Existing keys are never overwritten.
- available-when is evaluated BEFORE every step in both execute() AND resume(). Unmet conditions → step recorded as SKIPPED.
- resume() fires pre-step hooks, available-when, and synapse checks — identical guardrail chain as execute(). It does not bypass anything.
- _fire_synapses() uses asyncio.run() in a daemon thread. Never use asyncio.get_event_loop() — deprecated in Python 3.10+, causes DeprecationWarning.

---

## MCP Schema Rules (skill_mcp_schema.py)

- Archon skills define triggers.keywords, not input-schema. MCP synthesis generates {"prompt": string} inputSchema from keywords.
- output-schema goes in annotations.outputSchema. NOT in inputSchema. (The inversion was a bug fixed in Phase 9.)
- Explicit input-schema in a manifest is honored with full JSON Schema passthrough.

---

## Synapse Engine Version

synapse_engine_v2.py is the production engine. synapse_engine.py (v1) exists for legacy/compatibility but is not wired to the active pipeline. Add features only to v2. The OWASP pattern list in v2 covers A1-A10 (13 patterns). CRITICAL tier → HALT, HIGH/MEDIUM tier → WARN.

---

## Security Scanner (scanner.py)

The secret allowlist is intentionally narrow — only fixture/mock/testdata directories are exempt. Test source files (.py, .ts) are NOT exempt. Real secrets in test files should always be flagged.

The hook matcher in .claude/settings.json is "Write|Edit|NotebookEdit" — the NotebookEdit is required. Do not simplify back to "Write|Edit".

---

## Test Suite

Run: python3 -m pytest tests/ -q
Count: 583 passing as of 2026-04-25
No tests exist for completion_gate.py sys.exit(2) path — be careful there.
Tests map 1:1 to components: test_pipeline_engine.py, test_synapse_*.py, test_hooks.py, etc.

---

## CLI Usage

```
archon install              # install all components to ~/.claude/skills/
archon validate             # validate all skills/agents/bundles
archon doctor               # health check (missing files, schema violations)
archon list skills          # list registered skills
archon list agents          # list registered agents
archon pipeline run <name>  # run a pipeline by name
```

---

## Known Gotchas

1. AgentCard is not subscriptable. agent.card["key"] crashes. Use agent.card.key.
2. available-when was a no-op before Phase 9. It is now wired. Old pipeline YAMLs that relied on it doing nothing will now skip steps.
3. quality_bash.py used to treat the word "error" in stdout as a test failure (false positive). Fixed 2026-04-25: only exit_code/exitCode field is trusted.
4. synapse_engine_v2.py is canon. synapse_engine.py (v1) still exists. Do not confuse them.
5. asyncio.get_event_loop() is deprecated Python 3.10+. Use asyncio.run() in a daemon thread.
6. validate() full scan covers skills + bundles + agents. Skills-only validation hides bundle/agent bugs.
7. Skills in archon.yaml are not automatically installed. Run archon install to sync to ~/.claude/skills/.
8. Platform install target is defined in archon.yaml platforms[]. Never hardcode ~/.claude/skills/ in Python code.

---

## Files That Are Sensitive — Change With Care

- hooks/claude/shared/scanner.py — SECRET_PATTERNS and the narrow allowlist are calibrated
- src/archon/core/synapse_engine_v2.py — OWASP tier mapping (CRITICAL→HALT, HIGH/MEDIUM→WARN)
- src/archon/core/pipeline_engine.py — resume() guardrail parity with execute() was hard-won; changes to execute() flow must mirror in resume()
- .claude/settings.json — hook registrations; wrong matchers cause silent failures
- hooks/claude/completion_gate.py — sys.exit(2) is intentional; only fires on confirmed test failure (tests_passed is False), not on "tests never ran"
