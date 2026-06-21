# Wakeel — CLAUDE.md

## What this is

Wakeel is a **discipline kernel** (not an agent loop) inside the Archon monorepo.
All code lives under `wakeel/`. The CLAUDE.md in the repo root governs Archon core —
this file governs Wakeel specifically.

## Hard constraints

- Changes ONLY under `wakeel/`. Zero edits to `src/archon/`, `virtuoso/`, `skills/`, `agents/`, `servers/`.
- No secrets in code. BYOK via env vars only. `.env.example` is allowlisted by the secret scanner.
- All providers use one `OpenAICompatClient` — never a per-provider SDK.

## Running tests

```bash
# From repo root
python -m pytest wakeel/tests -q
```

## Scaffold check

```bash
pip install -e wakeel/
python -c "import wakeel; print('ok')"
```

## Key invariants

- `build_system_prompt()` MUST contain "VERIFY, DON'T TRUST" — tested in `test_composer.py`.
- DRAFT failure → Arabic fallback reply, never silence.
- VERIFY failure → return DRAFT unmodified.
- Skill load failure → proceed synapses-only, no crash.
- POST /webhook returns 200 + empty TwiML immediately; reply happens in BackgroundTask.
