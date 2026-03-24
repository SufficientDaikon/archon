# Shared Prompt Utilities

Reusable prompt components for consistent formatting, error handling, and common patterns.

## Response Formatting

### Standard Headers

Use these headers for different response types:

**Skill Activation**:

```markdown
## 🎯 Activating: [Skill Name]

**Purpose**: [brief description]
**Workflow**: [number] steps
**Resources**: [list if applicable]
```

**Task Completion**:

```markdown
## ✅ Task Complete: [Task Name]

**Deliverable**: [what was produced]
**Location**: [file paths or outputs]
**Next Steps**: [what user should do next]
```

**Error/Issue**:

```markdown
## ⚠️ Issue Detected: [Issue Type]

**Problem**: [what went wrong]
**Cause**: [why it happened]
**Solution**: [how to fix]
```

**Pipeline Phase**:

```markdown
## 🔄 Pipeline Phase: [Phase Name]

**Agent**: [agent handling this phase]
**Input**: [artifact from previous phase]
**Output**: [artifact to produce]
**Progress**: [X of Y steps]
```

## Citation Format

When referencing Archon components:

**Skills**:

```markdown
> Source: `skill-name` skill ([path/to/SKILL.md](path/to/SKILL.md))
```

**Bundles**:

```markdown
> Bundle: `bundle-name-kit` (N skills: skill1, skill2, skill3)
```

**Agents**:

```markdown
> Agent: `agent-name-agent` specializing in [domain]
```

**Resources**:

```markdown
> Reference: `resource-name.md` from `skill-name` skill
```

**External Knowledge**:

```markdown
> Source: `source-id` knowledge source
> Cached: [timestamp]
> Original: [URL or path]
```

## Code Block Standards

### Always Include Language

```markdown
\`\`\`python

# Python code

\`\`\`

\`\`\`javascript
// JavaScript code
\`\`\`

\`\`\`bash

# Shell commands

\`\`\`
```

### Command Output Format

Show prompt and output:

```markdown
\`\`\`bash
$ command --with-args
Output line 1
Output line 2
<exited with code 0>
\`\`\`
```

### File Content

Include filename as comment:

```markdown
\`\`\`python

# file: src/main.py

def main():
pass
\`\`\`
```

## Error Handling Patterns

### Graceful Degradation

```markdown
Attempted: [action]
Result: [failure]
Fallback: [alternative approach]
Proceeding with: [fallback action]
```

### Validation Errors

```markdown
❌ Validation failed: [what was validated]

Errors found:

1. [Error 1]: [description]
2. [Error 2]: [description]

Fix these issues and retry.
```

### Missing Dependencies

```markdown
⚠️ Missing: [dependency name]

Required for: [why it's needed]
Install with: \`[installation command]\`
```

## Progress Indicators

### Multi-Step Tasks

```markdown
Progress: Step 3 of 7

✅ Step 1: [completed]
✅ Step 2: [completed]
🔄 Step 3: [current - in progress]
⏳ Step 4: [pending]
⏳ Step 5: [pending]
```

### Checklist Format

```markdown
## Task Checklist

- [x] Item 1 completed
- [x] Item 2 completed
- [ ] Item 3 in progress
- [ ] Item 4 pending
- [ ] Item 5 pending
```

## Table Formatting

### Skills/Bundles Listing

```markdown
| Skill/Bundle | Description        | Tags       |
| ------------ | ------------------ | ---------- |
| skill-name   | Brief description  | tag1, tag2 |
| bundle-kit   | Bundle description | tag1, tag2 |
```

### Comparison Tables

```markdown
| Feature | Option A | Option B | Recommended |
| ------- | -------- | -------- | ----------- |
| Speed   | Fast     | Slow     | Option A    |
| Quality | Good     | Better   | Option B    |
```

### Resource Tables

```markdown
| Resource | Type      | Load   | Description      |
| -------- | --------- | ------ | ---------------- |
| file.md  | reference | always | What it contains |
```

## File Operation Patterns

### Creating Files

```markdown
Creating: `path/to/file.ext`
Content:
\`\`\`[language]
[file content]
\`\`\`
✅ Created successfully
```

### Editing Files

```markdown
Editing: `path/to/file.ext`

Change:

- Old: \`[old content]\`
- New: \`[new content]\`

✅ Updated successfully
```

### Viewing Files

```markdown
Viewing: `path/to/file.ext` (lines [start]-[end])

\`\`\`[language]
[file content excerpt]
\`\`\`
```

## Decision Documentation

When making routing/complexity decisions:

```markdown
### Decision: [What was decided]

**Options considered**:

1. Option A: [pros/cons]
2. Option B: [pros/cons]
3. Option C: [pros/cons]

**Selected**: Option [X]

**Reasoning**: [1-2 sentences explaining why]

**Trade-offs**: [What was sacrificed, what was gained]
```

## Workflow Documentation

When executing multi-step workflows:

```markdown
## Workflow: [Workflow Name]

### Phase 1: [Phase Name]

**Goal**: [What this phase achieves]
**Actions**:

1. [Action 1]
2. [Action 2]

**Output**: [What is produced]

### Phase 2: [Phase Name]

[repeat pattern]
```

## Agent Handoff Format

When passing between agents in pipeline:

```markdown
---
## 🔄 Agent Handoff

**From**: [source-agent]
**To**: [target-agent]

**Artifact**: [artifact-name]
**Format**: [format]
**Location**: [path]

**Quality Gate Results**:
- ✅ [Gate 1]: Passed
- ✅ [Gate 2]: Passed
- ✅ [Gate 3]: Passed

**Context for next agent**:
[Brief context or instructions]

---
```

## Confirmation Requests

For actions requiring user confirmation:

```markdown
## ⚠️ Confirmation Required

**Action**: [What will be done]
**Impact**: [What will change]
**Reversible**: [Yes/No]

**Risk Level**: [Low/Medium/High]

Please confirm to proceed:

- Type "yes" to continue
- Type "no" to cancel
- Type "alt" for alternative approach
```

## Summary Format

At end of complex operations:

```markdown
## 📋 Summary

**Task**: [What was requested]
**Approach**: [How it was handled]
**Result**: [What was delivered]

**Artifacts Created**:

- \`path/to/file1\`
- \`path/to/file2\`

**Next Steps**:

1. [Next action user should take]
2. [Optional follow-up]

**Verification**:
\`\`\`bash

# Commands to verify the work

\`\`\`
```

## Inline Annotations

Use these consistently:

- ✅ Success/Completed
- ❌ Failed/Error
- ⚠️ Warning/Caution
- 🔄 In Progress/Processing
- ⏳ Pending/Waiting
- 🎯 Goal/Target
- 📋 Summary/List
- 🔍 Search/Analysis
- 💡 Insight/Tip
- 📁 File/Directory
- 🔗 Link/Reference
- 🚀 Deployment/Launch

## Variable Placeholders

Use angle brackets for user-replaceable values:

- `<skill-name>` — replace with actual skill name
- `<bundle-name>-kit` — replace with bundle name
- `<agent-name>-agent` — replace with agent name
- `<your-value>` — replace with user-specific value
- `[optional-param]` — square brackets for optional parameters

---

**Use these patterns consistently across all responses to maintain professional, readable output.**
