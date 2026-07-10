<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/ARCHON-The_Virtuoso_Engine-00F0FF?style=for-the-badge&labelColor=0e0e0e">
  <source media="(prefers-color-scheme: light)" srcset="https://img.shields.io/badge/ARCHON-The_Virtuoso_Engine-0969DA?style=for-the-badge&labelColor=f6f8fa">
  <img alt="Archon" src="https://img.shields.io/badge/ARCHON-The_Virtuoso_Engine-00F0FF?style=for-the-badge&labelColor=0e0e0e">
</picture>

<br><br>

**A cognitive harness for Claude Code.**

<br>

[![MIT License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/v1.2.0-stable-brightgreen?style=flat-square)]()
[![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)]()
![Skills](https://img.shields.io/badge/skills-97-blue?style=flat-square)
![Agents](https://img.shields.io/badge/agents-14-orange?style=flat-square)
![Synapses](https://img.shields.io/badge/synapses-5-blueviolet?style=flat-square)
![Pipelines](https://img.shields.io/badge/pipelines-9-red?style=flat-square)
![Bundles](https://img.shields.io/badge/bundles-14-teal?style=flat-square)
![Tests](https://img.shields.io/badge/tests-655-success?style=flat-square)

</div>

---

Archon makes Claude Code output measurably more disciplined. It hooks into the
session lifecycle and injects a small, tier-scaled amount of cognitive
scaffolding — plan-before-executing, no-unverified-claims, escape hatches for
stuck loops — exactly when a task is complex enough to need it, and stays out
of the way when it isn't.

> A harness, not a guardrail. Trust the model to be smart; manage its
> knowledge, context, and verification burden — don't dictate how to think.

## How it improves output quality

Every prompt is classified into a complexity tier (pure regex, <50ms, no LLM
call). Pasted logs, tracebacks, and code blocks are stripped first, so a terse
hard task classifies by its actual request — not its noise. The tier decides
how much discipline gets injected:

| Tier | Injected | Budget |
|------|----------|--------|
| TRIVIAL / SIMPLE | nothing (security scan only if keywords match) | ~0 |
| MODERATE | plan + knowledge inventory, no-unverified-claims | ~130 tokens |
| COMPLEX | + 3-attempt escape hatch, iron laws, step decomposition | ~330 tokens |
| EXPERT | + stuck-loop detection | ~450 tokens |

Example injection for a COMPLEX task:

```xml
<archon-route tier="COMPLEX" mode="orchestrator" skills="systematic-debugging" synapses="...">
  <metacognition>PLAN before executing: rate complexity 1-5; list Know / Don't
  Know / Assuming; define exit criteria. ... ESCAPE HATCH: after 3 failed
  attempts at the same subtask with the same approach, STOP.</metacognition>
  <anti-rationalization>NO UNVERIFIED CLAIMS: never say 'should work',
  'probably fine'. Replace with evidence: 'verified by [test/output]'. ...</anti-rationalization>
</archon-route>
```

Beyond injection, the hooks close the loop:

- **State survives compaction.** Files modified, test status, and pending
  todos are re-injected after auto-compact — the session doesn't forget what
  it touched.
- **A completion gate** blocks "done" (Stop hook, exit 2) when tests or the
  build are *confirmed* failing — with loop protection so it can never trap a
  session.
- **Guards** deny dangerous bash (force-push to main, `rm -rf /`) and secrets
  in written files before they happen.

## The operational layer

Borrowed from the Google Cloud SDK and ADK, adapted to a single-user harness:

- **Properties** — every knob is a `section/name` property with gcloud's
  precedence chain (`ARCHON_GATE_MAX_BLOCKS` env var > project
  `.archon/config` > user `~/.archon/config` > default). `archon config list`
  shows each value *with its source*:

  ```bash
  archon config set classifier/trivial_max_words 20
  archon config set gate/enabled false --project    # per-repo override
  ARCHON_INJECTION_ENABLED=false claude              # per-invocation
  ```

- **Per-project state** — session state lives at
  `~/.archon/projects/<slug>/state.json`, so concurrent Claude Code sessions
  in different repos are fully isolated (one repo's failing tests can never
  block another repo's completion gate).

- **Invocation logs** — every hook firing appends a fail-open JSONL record
  (`~/.archon/logs/hooks-YYYY.MM.DD.jsonl`): what tier was classified, which
  synapses fired, what the guards denied, what the gate decided.

- **Diagnostics** — `archon info` prints the resolved environment (paths,
  properties with sources, hook registrations); `archon doctor --hooks`
  drives all 11 hooks live with synthetic payloads and reports 17 PASS/FAIL
  checks.

- **Evaluation** — `archon eval classifier` reports tier distribution and
  synapse activation from your real usage, and (with
  `logging/log_prompts=true`) replays stored prompts through the current
  classifier so you can measure a threshold tuning before trusting it.

- **Live-state injections** — instructions adapt to the session:
  when tests are recorded failing, the anti-rationalization band literally
  says *"Tests are recorded FAILING this session — fix and re-run before
  claiming anything is done."*

## Quickstart

```bash
git clone https://github.com/SufficientDaikon/archon && cd archon
pip install -e ".[dev]"

archon install         # install skills to ~/.claude/skills/
archon doctor          # health check
```

The hooks activate automatically for sessions in this repo via
`.claude/settings.json`. To use them in another project, copy that file's
`hooks` block and the `hooks/claude/` directory (they're self-contained —
stdlib only).

## Architecture

```
prompt ──► UserPromptSubmit ──► classifier (tier + skills + synapses)
                                    │
              <archon-route> + tier-banded instructions
                                    ▼
tools  ──► PreToolUse guards (bash danger / secrets)
       ──► PostToolUse trackers (files, tests, builds, todos)
                                    ▼
stop   ──► completion gate (exit 2 if tests/build confirmed failed)
lifecycle ► SessionStart/End, PreCompact — state snapshot + re-injection
```

Three layers:

1. **Runtime hooks** (`hooks/claude/`) — the product. 11 stdlib-only Python
   scripts registered in `.claude/settings.json`, per-project state in
   `~/.archon/projects/<slug>/state.json`, invocation logs in
   `~/.archon/logs/`.
2. **Engine** (`src/archon/`) — `archon` CLI: registry, installer, validator,
   pipeline executor with post-hoc synapse validators
   (`synapse_engine_v2.build_default_engine()`, 9 checks).
3. **Content** (`skills/`, `agents/`, `synapses/`, `bundles/`, `pipelines/`)
   — 97 skills with a normalized SKILL.md + manifest format, 14 agents,
   5 synapse documents (the source material for the injected instructions),
   14 bundles, 9 pipelines. `archon.yaml` is the registry and is enforced to
   stay in sync with the filesystem.

## Development

```bash
python3 -m pytest tests/ -q        # 655 tests
python3 scripts/validate.py --all  # manifests + registry sync + hook layer
ruff check . && ruff format --check .
```

CI runs all three on every push/PR to `main`.

## License

MIT © [Ahmed Taha](https://github.com/SufficientDaikon)
