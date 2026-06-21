# Wakeel

A **discipline kernel** — not an agent loop. Wakeel wraps any OpenAI-compatible LLM in a
deterministic draft → verify pipeline that enforces Archon's cognitive discipline
(Virtuoso synapses + 10 Iron Laws) on every response.

## What it is

```
Harness.respond(session_id, text) → str
  1. TF-IDF router   — selects a relevant Archon skill (or None)
  2. Composer        — builds system prompt: persona + synapses + Iron Laws (+ skill)
  3. Draft           — DRAFT_PROVIDER generates a response          [retry + fallback]
  4. Verify          — VERIFY_PROVIDER audits draft vs Iron Law #7  [degrades to draft]
```

It is **not** a tool-loop, planning agent, or iterative executor. It is a
disciplined single-pass completion pipeline with a verification second pass.

## Quick start

```bash
# Install
cd wakeel
pip install -e .

# Configure
cp .env.example .env
# Fill in GEMINI_API_KEY, GROQ_API_KEY

# CLI REPL
python -m wakeel.chat

# WhatsApp webhook
uvicorn wakeel.channels.whatsapp.app:app --reload
```

## Configuration

All config is environment-only (12-factor). See `.env.example` for all vars.

To swap the draft model: `DRAFT_PROVIDER=openrouter` — no code change needed.

## Docker

Build from the **repo root** (not from `wakeel/`):

```bash
docker build -f wakeel/Dockerfile -t wakeel .
docker run -p 8000:8000 --env-file wakeel/.env wakeel
```

## Architecture

| Component | File | Role |
|---|---|---|
| Kernel | `kernel/harness.py` | Orchestrates the 4-step pipeline |
| Router | `kernel/router/` | TF-IDF skill selection |
| Composer | `kernel/composer/` | Assembles system prompt from virtuoso.xml |
| Provider | `kernel/provider/client.py` | Single OpenAI-compat client for all providers |
| Verifier | `kernel/verify/verifier.py` | Second-pass Iron Law audit |
| Sessions | `kernel/sessions.py` | In-memory conversation history |
| WhatsApp | `channels/whatsapp/` | Twilio webhook surface |
| CLI | `chat.py` | Local REPL surface |
