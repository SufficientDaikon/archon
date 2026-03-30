# 🔄 Archon Batch SDD — Auto-Continue Prompt
#
# HOW TO USE:
# 1. Start a new Copilot CLI session (or Claude Code, Cursor, etc.)
# 2. Paste this entire file as your first message
# 3. The agent will automatically:
#    - Read the state file to find the next pending plan
#    - Run the full SDD pipeline on it (spec → implement → review)
#    - Update state, commit to git, and generate a handoff if needed
# 4. When it finishes or runs low on context, start a new session and paste again
#
# That's it. Just keep pasting this prompt in new sessions until all 12 plans are done.

---

## Instructions

You are executing the **Archon Batch SDD Pipeline**. Your job is to find the next unfinished improvement plan and run the full Spec-Driven Development pipeline on it.

### Step 0: Read State

Read the batch state file:
```
/path/to/archon\batch-runs\google-adk-improvements\state.yaml
```

Find the first plan with `status: pending` or `status: in-progress` (resume if interrupted).
Note which sprint it belongs to.

### Step 1: Read the Plan

Read the plan file from:
```
~/.copilot\ideas\google-adk-ideas\{plan-file}
```

Also read the master roadmap for context:
```
~/.copilot\ideas\google-adk-ideas\00-master-roadmap.md
```

**Update state.yaml**: Set the plan's `status: in-progress`, `current_step: specify`, `started_at: <now>`.

### Step 2: Specification (spec-writer)

Use the **spec-writer** agent (or invoke the `spec-writer` skill) to transform the plan into a comprehensive implementation specification.

**Input**: The plan file content + Archon repo context at `/path/to/archon\`
**Output**: Full spec saved to `~/.copilot/sdd/specs/archon-<plan-id>/spec.md`

The spec must include:
- Functional requirements (numbered FRs)
- User stories with acceptance criteria
- Non-functional requirements
- File-by-file implementation map
- Edge cases and error handling

**Update state.yaml**: Set `current_step: implement`, `spec_path: <path>`.

### Step 3: Implementation (implementer)

Use the **implementer** agent (or invoke the `implementer` skill) to build everything from the spec.

**Input**: The spec from Step 2 + Archon codebase
**Output**: All files created/modified in `/path/to/archon\`

Implementation rules:
- Follow the spec section by section
- Write tests if the spec calls for them
- Update CLI, VS Code extension, webapp, and docs if the spec includes them
- Ensure backward compatibility with existing Archon components

**Update state.yaml**: Set `current_step: review`.

### Step 4: Review (reviewer)

Use the **reviewer** agent (or invoke the `reviewer` skill) to verify implementation against spec.

**Input**: Spec + implemented code
**Output**: Compliance report saved to `~/.copilot/sdd/reports/archon-<plan-id>/review.md`

If review score < 80%: Loop back to Step 3 with reviewer feedback (max 3 iterations).
If review score >= 80%: Proceed to Step 5.

### Step 5: Commit & Update State

1. **Git commit** all changes:
   ```bash
   cd /path/to/archon
   git add -A
   git commit -m "feat: implement <plan-name> (batch-sdd plan <plan-id>)"
   git push origin master
   ```

2. **Update state.yaml**:
   - Set plan `status: completed`
   - Set `completed_at: <now>`
   - Set `commit_hash: <hash>`
   - Set `report_path: <path>`
   - Increment batch `completed` count
   - Add session entry to `sessions` list

### Step 6: Next Plan or Handoff

**Check capacity**: If you still have context capacity and the session is responsive:
- Go back to Step 0 and process the next pending plan

**If running low on context** (you'll know — responses get slow, you're losing track):
- Generate a handoff summary
- Save it to `/path/to/archon\batch-runs\google-adk-improvements\handoff.md`
- Tell the user: "Session capacity reached. Start a new session and paste the auto-continue prompt again."

### Important Context

- **Archon repo**: `/path/to/archon\` (git remote: SufficientDaikon/archon)
- **Plans directory**: `~/.copilot\ideas\google-adk-ideas\`
- **State file**: `/path/to/archon\batch-runs\google-adk-improvements\state.yaml`
- **SDD specs go to**: `~/.copilot\sdd\specs\archon-<plan-id>\`
- **SDD reports go to**: `~/.copilot\sdd\reports\archon-<plan-id>\`
- **The framework has**: 61 skills, 8 agents, 1 synapse, 6 pipelines, 8 bundles
- **Existing components**: Python CLI, VS Code extension, Next.js webapp, GitHub Pages docs
- **Git branch**: master
- **Always push** after completing each plan

### Sprint Order (for reference)

| Sprint | Plans | Status |
|--------|-------|--------|
| Sprint 1: Quick Wins | 03 → 05 → 12 | Check state.yaml |
| Sprint 2: Core Power | 01 → 04 → 02 | Check state.yaml |
| Sprint 3: Production Polish | 08 → 06 | Check state.yaml |
| Sprint 4: UX & Scale | 10 → 11 → 09 → 07 | Check state.yaml |

Now begin. Read the state file and start processing.
