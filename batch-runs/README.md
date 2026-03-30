# 📦 Batch Runs

This directory contains batch SDD pipeline executions — automated processing of multiple feature plans through the full Spec-Driven Development pipeline.

## How It Works

1. **Plan files** live in a directory (e.g., `~/.copilot/ideas/google-adk-ideas/`)
2. **State tracking** (`state.yaml`) tracks which plans are done, in-progress, or pending
3. **Auto-continue prompt** (`continue.md`) — paste in any new session to auto-resume
4. **Handoff** — generated when a session runs low on context

## Usage

### Start a batch run
```
Read and follow the instructions at /path/to/archon\batch-runs\google-adk-improvements\continue.md
```

### Check progress
Open `state.yaml` in the batch run directory to see current status.

### Resume after session ends
Just start a new session and paste the same prompt. The agent reads `state.yaml` and picks up where it left off.

## Directory Structure

```
batch-runs/
  <batch-name>/
    state.yaml             # Progress tracking (source of truth)
    continue.md            # Auto-continue prompt (paste in new sessions)
    handoff.md             # Last session's handoff (auto-generated)
    handoff-template.md    # Template for generating handoffs
```

## Creating New Batch Runs

To create a new batch run for a different set of plans:

1. Create a directory under `batch-runs/`
2. Create a `state.yaml` with your plans listed in sprint order
3. Create a `continue.md` prompt pointing to your plans directory
4. Paste the prompt in a session and let it run
