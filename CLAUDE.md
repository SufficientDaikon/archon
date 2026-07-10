# Archon — CLAUDE.md

Project-level context for Claude Code. Everything below is verified against the
code as of v1.1.0 (2026-07). If a claim here contradicts the code, the code
wins — then fix this file.

---

## What Archon Is

A **cognitive harness for Claude Code**: a runtime hook layer that injects
compact, tier-scaled discipline into every prompt, plus a skills/pipeline
engine behind an `archon` CLI.

> A harness, not a guardrail. Trust the model to be smart; manage its
> knowledge, context, and verification burden — don't dictate how to think.

Two enforcement surfaces share the same 5 synapse names but are different code:

1. **Hook synapses** (`hooks/claude/shared/classifier.py`) — *generative*:
   compact instructions injected into the prompt via UserPromptSubmit.
   The full `synapses/*/SYNAPSE.md` documents are the source material; the
   injected text is the tier-banded distillation in `SYNAPSE_INSTRUCTIONS`.
2. **Pipeline synapses** (`src/archon/synapses/*.py`) — *post-hoc validators*:
   `validate(context) -> dict` checks fired by the pipeline engine between
   steps via `synapse_engine_v2.build_default_engine()` (9 registered).

---

## Directory Map

```
archon/
├── src/archon/           # Python package (archon CLI + engine)
│   ├── cli.py            # Typer entrypoint
│   ├── commands/         # one module per CLI command
│   ├── core/
│   │   ├── registry.py            # archon.yaml -> dataclasses (NOT dicts)
│   │   ├── pipeline_engine.py     # step executor; on-failure policy inlined
│   │   ├── synapse_engine_v2.py   # THE synapse engine (v1 deleted in 1.1.0)
│   │   ├── synapse_router.py      # trigger x tier -> synapse ID routing
│   │   ├── skill_mcp_schema.py    # skill -> MCP tool descriptor
│   │   ├── agent_cards.py         # A2A card generation
│   │   └── installer.py           # installs skills -> ~/.claude/skills/
│   └── synapses/         # 9 dict-returning validate() modules (single impl)
├── hooks/claude/         # Claude Code hook scripts (the product)
│   └── shared/           # classifier.py, scanner.py, state.py
├── skills/               # 97 skills (SKILL.md frontmatter + manifest.yaml)
├── agents/               # 14 agents ├── synapses/  # 5 synapse docs
├── bundles/              # 14 kits   ├── pipelines/ # 9 pipeline YAMLs
├── schemas/              # manifest schemas
├── tests/                # pytest — 603 passing as of 2026-07-10
├── archon.yaml           # root manifest — validate enforces sync with skills/
└── scripts/              # validate.py (CI), normalize_skills.py (one-off)
```

Unaudited peripherals (present, not covered by the 1.1.0 modernization):
`vscode-extension/`, `webapp/`, `file-ops-rs/`, `virtuoso/`, `servers/`,
`catalog/`, `batch-runs/`.

---

## The Hook Layer (hooks/claude/ + .claude/settings.json)

| Event | Matcher | Script | Does |
|---|---|---|---|
| SessionStart | — | session_boot.py | project/git snapshot; `source`-aware: startup/clear reset the session, resume/compact PRESERVE it and inject `<archon-resume>` |
| UserPromptSubmit | — | prompt_router.py | tier classify + `<archon-route>` + tier-banded synapse instructions |
| PreToolUse | Bash | guard_bash.py | deny dangerous commands |
| PreToolUse | Write\|Edit\|MultiEdit\|NotebookEdit | guard_write.py | deny secrets in written content |
| PostToolUse | Write\|Edit\|MultiEdit\|NotebookEdit | quality_write.py | track modified files |
| PostToolUse | Bash | quality_bash.py | record tests/build pass/fail |
| PostToolUse | TodoWrite | todo_track.py | todo counts + pending titles |
| Stop | — | completion_gate.py | exit 2 if tests/build confirmed failed |
| SubagentStart | — | agent_context.py | role-scoped context slice |
| SubagentStop | — | agent_context.py | run telemetry |
| SessionEnd | — | session_end.py | archive session (covers /clear + exit) |
| PreCompact | — | pre_compact.py | flush state before compaction |

State lives at `~/.archon/archon-state.json` (`ARCHON_HOME` overrides; tests
use this for isolation). All hooks are `python3 "$CLAUDE_PROJECT_DIR/..."`.

Hard-won rules — do not regress:

- **quality_bash** trusts only `exit_code`/`exitCode`, then explicit runner
  summaries (`N failed`, `test result: ok/FAILED`, go `ok/FAIL`). A bare
  "error" in stdout must NEVER mark failure — passing runs print "0 errors".
  Unknown stays `None`, and `None` never blocks the gate.
- **completion_gate** blocks only on `tests_passed is False` or
  `build_passed is False`. It respects `stop_hook_active` and caps at 2
  blocks/session (`gate_blocks` in state) to avoid infinite stop loops.
  Stop hooks cannot inject context — the pass path prints `{}` and stays silent.
- **session_boot** must never reset the session on `source in (resume, compact)`
  — that wipes `files_modified`/`tests_passed` and silently disarms the gate.
- **SubagentStart is not a vanilla Claude Code CLI event.** It fires in some
  harnesses (e.g. remote/web); elsewhere the registration is inert. The
  payload field is `subagent_type` (with `agent_type` fallback).
- Classifier tiers come from **noise-stripped** word counts (`strip_noise`
  removes fenced code, tracebacks, timestamped logs, quotes). Questions
  de-escalate one tier; ≥3 file refs or numbered steps escalate one.
- Injection budget: TRIVIAL/SIMPLE ≈ 0 (security keyword only), MODERATE
  ≈ 130 tokens, COMPLEX ≈ 330, EXPERT ≈ 450. Keep it under 600.
- scanner.py's secret allowlist is deliberately narrow (fixtures/test files);
  the force-push/reset-hard patterns are branch-name safe (`fix-main-page`
  must not match) — extend with tests in tests/test_claude_hooks.py.

---

## Critical Data Types

- All registry types (Skill, Agent, AgentCard, Bundle, Pipeline, Synapse) in
  `registry.py` are **dataclasses, not dicts**: `agent.card.skills_provided`,
  never `agent.card["skills-provided"]`.
- Pipeline synapse validators return plain dicts
  (`{"action": "allow"|"warn"|"halt", "message": str, ...}`);
  `synapse_engine_v2._adapt_validator` lifts them into `SynapseDecision`.
  Absent context keys must not be judged (see metacognition's `confidence`).
- Step `on-failure` policy (halt/skip/retry/loop/escalate + 3-fix escape
  hatch) is implemented in `PipelineExecutor._handle_failure` — there is no
  external hook system for pipelines anymore.

## MCP Schema Rules (skill_mcp_schema.py)

- Skills define `triggers.keywords`; MCP synthesis generates a
  `{"prompt": string}` inputSchema from them.
- `output-schema` goes in `annotations.outputSchema`, NOT inputSchema.
- Explicit `input-schema` in a manifest is passed through as-is.

---

## Content Layer Rules

- SKILL.md must start with YAML frontmatter (`name`, `description`).
  **manifest.yaml owns `version`** — never add version to SKILL.md frontmatter.
- `archon.yaml` and `skills/` must agree exactly: `scripts/validate.py --all`
  fails on unregistered dirs, missing paths, placeholder descriptions
  (`Skill: <name>`), or `allowed-tools` leaked into a description string.
- `scripts/normalize_skills.py` is the idempotent format migrator; run it
  after bulk-adding skills.

---

## Commands

```
pip install -e ".[dev]"          # setup
python3 -m pytest tests/ -q      # 603 passing (2026-07-10)
python3 scripts/validate.py --all
ruff check . && ruff format --check .
archon install | validate | doctor | list skills | pipeline run <name>
```

CI (.github/workflows/ci.yml) runs on `main`: ruff + validate + pytest.

---

## Known Gotchas

1. Registry dataclasses are not subscriptable.
2. `asyncio.get_event_loop()` is banned — use `asyncio.get_running_loop()` /
   `asyncio.run()` (see `pipeline_engine._fire_synapses`).
3. Skills in archon.yaml are not auto-installed — `archon install` syncs to
   `~/.claude/skills/` (target defined in archon.yaml `platforms[]`, never
   hardcode the path in Python).
4. The `security` keyword activates the security-awareness *synapse*; it is
   not a skill — SKILL_MATCHERS entries must name real `skills/` dirs
   (tests enforce this).
5. tests/test_claude_hooks.py runs each hook as a subprocess with
   `ARCHON_HOME=tmpdir` — new hooks need contract tests there.
