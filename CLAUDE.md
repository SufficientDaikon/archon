# Archon — CLAUDE.md

Project-level context for Claude Code. Everything below is verified against the
code as of v1.2.0 (2026-07). If a claim here contradicts the code, the code
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
├── tests/                # pytest — 655 passing as of 2026-07-10
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

State is **per project**: `<ARCHON_HOME>/projects/<slug>/state.json`, where
`slug = sanitized-basename[:40] + "-" + sha1(resolved path)[:8]`
(`state.project_slug`). Every hook threads the payload `cwd` into
`load_state`/`save_state` — concurrent sessions in different repos are fully
isolated (one repo's failing tests can never trip another repo's gate).
`ARCHON_HOME` overrides the root (tests use this). All hooks are
`python3 "$CLAUDE_PROJECT_DIR/..."`.

### Properties (gcloud-style config)

Every configurable hook knob is a `section/name` property registered in
`hooks/claude/shared/config.py` (stdlib-only; the CLI reuses it via
`core/hooks_bridge.py` — never duplicate the registry). Precedence:
`ARCHON_{SECTION}_{NAME}` env var > project `.archon/config` (INI) > user
`<ARCHON_HOME>/config` (INI) > registry default. Malformed values fall back
to defaults — config can never crash a hook. `archon config list` shows every
value **with its source**. Knobs: classifier tier ceilings + escalation cap,
per-synapse injection toggles + master switch, `gate/enabled` +
`gate/max_blocks`, `scanner/extra_allowlist`, `logging/*`.

### Hook logging

Every hook firing appends one JSONL record to
`<ARCHON_HOME>/logs/hooks-YYYY.MM.DD.jsonl` via `shared/hooklog.py`
(`write_record`). **IRON RULE: logging is fail-open** — nothing in hooklog
may ever change a hook's exit code or stdout (contract-tested with an
unwritable logs dir). completion_gate writes its record before `sys.exit(2)`.
Full stripped prompts are stored only with `logging/log_prompts=true`
(capped by `logging/prompt_max_chars`). Age cleanup (filename date,
`logging/max_log_days`) runs only in session_boot; foreign files in logs/
are never touched. `archon eval classifier` summarizes these records and
replays stored untruncated prompts against the current classifier to report
tier drift.

### State-templated instructions

Synapse instruction bands may carry `{state.<key>?}` placeholders (ADK-style)
resolved by `classifier.resolve_state_placeholders` from `_STATE_PROVIDERS`
lambdas. Resolution NEVER raises — unknown key, missing session, or provider
exception all render empty. Live providers: `tests_failing_notice`
(anti-rationalization complex band), `pending_todos_notice` (metacognition
base band).

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
python3 -m pytest tests/ -q      # 655 passing (2026-07-10)
python3 scripts/validate.py --all
ruff check . && ruff format --check .
archon install | validate | doctor | list skills | pipeline run <name>
archon config list|get|set|unset # properties with sources (env/project/user/default)
archon info                      # environment report; `archon info <name>` = component
archon doctor --hooks            # live hook diagnostics (17 checks, exit 1 on failure)
archon eval classifier           # tier distribution + drift replay from hook logs
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
   `ARCHON_HOME=tmpdir` — new hooks need contract tests there, plus a
   PASS/FAIL entry in `core/hook_diagnostics.CHECKS` (doctor --hooks;
   tests/test_hook_diagnostics.py enforces coverage of every hook).
6. Hook payloads must carry `cwd` — `run_hook()` in the test suite defaults
   it to the repo root; state helpers are slug-aware
   (`state_path(home, cwd)`).
7. The archon rich console binds its output file at import time — CLI tests
   assert on pure data functions (see eval_cmd.evaluate_classifier), not on
   captured console output.
