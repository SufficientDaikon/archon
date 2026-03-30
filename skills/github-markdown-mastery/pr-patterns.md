# PR Body Patterns — Templates and Real-World Examples

## Anatomy of a Great PR Body

```markdown
# PR Summary

One-line description of what this PR does and why.

> [!NOTE]
> Any critical context (WG approval, breaking change, etc.)

### What Changed

| File | Change |
|------|--------|
| `file.cs` | Description of change |
| `file.Tests.ps1` | Added regression test |

### Tests

- **N/N suite pass** (X existing + Y new)
- **Smoke test**: `command` returns expected

<details>
<summary>Before / After</summary>

` ` `diff
- old code
+ new code
` ` `

</details>

---

## PR Context

Why this change is needed. Link to issue, WG decision, prior art.

---

## PR Checklist

- [x] Meaningful title
- [x] Changes summarized
- [ ] Breaking changes: description if applicable
- [x] Tests added
```

## Pattern: One-Line Fix

For minimal changes (1-3 lines). Keep proportional — don't over-document.

```markdown
# PR Summary

Changes `NewThing()` to `BetterThing()` per WG decision in #1234.

### What Changed

| File | Change |
|------|--------|
| `Command.cs` | `OldMethod()` → `NewMethod()` |
| `Command.Tests.ps1` | Added verification test |

### Tests

- **9/9 Pester tests pass** (8 existing + 1 new)

---

## PR Context

The Working Group approved this change in [#1234](link) — see [@maintainer's comment](link).

---

## PR Checklist
...
```

## Pattern: Bug Fix with Before/After

```markdown
# PR Summary

Fixes `Get-Thing -Switch:$false` incorrectly triggering the switch-true code path.

Fixes #5678.

> [!WARNING]
> This is a behavior change: `-Switch:$false` now correctly returns the default result instead of the switch result.

### The Bug

| Input | Before (wrong) | After (correct) |
|-------|----------------|-----------------|
| `Get-Thing -Switch:$false` | Returns all items | Returns current item |

### What Changed

| File | Change |
|------|--------|
| `ThingCommand.cs` | Guard `SwitchParameterSet` with `if (Switch)` |
| `Thing.Tests.ps1` | Added `-Switch:$false` regression test |

<details>
<summary>Code diff</summary>

` ` `diff
  case SwitchParameterSet:
-     foreach (var item in GetAll())
-         WriteObject(item);
+     if (Switch)
+     {
+         foreach (var item in GetAll())
+             WriteObject(item);
+     }
+     else
+     {
+         WriteObject(GetCurrent());
+     }
      break;
` ` `

</details>

### Tests

- **12/12 Pester pass** (11 existing + 1 new)
```

## Pattern: Multi-File Feature

For larger changes. Use progressive disclosure heavily.

```markdown
# PR Summary

Adds timeout support to the hosting API, preventing indefinite hangs when hosts embed PowerShell.

> [!IMPORTANT]
> New public API surface — RFC required before merge.

### What Changed

| File | Lines | Change |
|------|-------|--------|
| `PowerShell.cs` | +91/-5 | `Stop(TimeSpan)`, `PSInvocationSettings.Timeout` |
| `ConnectionBase.cs` | +37/-5 | 30s runspace-open wait, parallel StopPipelines |
| `LocalConnection.cs` | +28/-2 | 30s close/job waits, Dispose → Broken state |
| `LocalPipeline.cs` | +6/-1 | 30s PipelineFinishedEvent wait |

<details>
<summary>New API surface</summary>

| Member | Type | Description |
|--------|------|-------------|
| `PowerShell.Stop(TimeSpan)` | Method | Bounded stop with timeout |
| `PSInvocationSettings.Timeout` | Property | Per-invocation timeout |

</details>

<details>
<summary>Flow diagram</summary>

` ` `mermaid
flowchart TD
    A[Invoke] --> B{Timeout set?}
    B -->|No| C[Original path]
    B -->|Yes| D[Task.Run + Wait]
    D --> E{Completed?}
    E -->|Yes| F[Return results]
    E -->|Timeout| G[CoreStop + TimeoutException]
` ` `

</details>

### Tests

![xUnit](https://img.shields.io/badge/xUnit-19%2F19-brightgreen)
![Pester](https://img.shields.io/badge/Pester-15%2F15-brightgreen)

<details>
<summary>Test inventory</summary>

| Suite | Count | Covers |
|-------|-------|--------|
| xUnit C# | 19 | REQ-01 through REQ-10 |
| Pester | 15 | End-to-end scenarios |

</details>
```

## Pattern: Static Analysis / Batch Fixes

For multiple small unrelated fixes in one PR.

```markdown
# PR Summary

Fixes 6 static analyzer findings from #5289 — null dereferences, operator precedence, missing volatile.

### Fixed Items

| # | File | Bug | Severity | Fix |
|---|------|-----|----------|-----|
| 1 | `File.cs` | Null dereference | High | Added null guard |
| 2 | `Utils.cs` | Unsafe double-check | Low | Added `volatile` |
| 3 | `Host.cs` | Use before null check | High | Reordered checks |

<details>
<summary>Skipped items (4) — need maintainer guidance</summary>

| # | File | Why Skipped |
|---|------|------------|
| 4 | `AutoGen.cs` | Auto-generated — fix would be overwritten |
| 5 | `Command.cs` | Public API change — needs WG decision |

</details>

<details>
<summary>Item 1 — before/after</summary>

` ` `diff
- instance.Property.Value;
+ if (instance != null)
+     instance.Property.Value;
` ` `

</details>
```

## Pattern: CI / Infrastructure Fix

```markdown
# PR Summary

Fixes the weekly `Verify Markdown Links` workflow that has been failing every Sunday since October 2025.

Fixes #7091.

### The Problem

` ` `
Unsupported event type: schedule. Supported types: pull_request, push
` ` `

The `get-changed-files` action only handles `pull_request` and `push`, but the workflow uses `schedule`.

### The Fix

| File | Change |
|------|--------|
| `get-changed-files/action.yml` | Add `schedule` + `workflow_dispatch` handlers using Trees API |
| `markdownlinks/action.yml` | Update event-types list |

> [!TIP]
> **How to test:** Go to Actions → "Verify Markdown Links" → Run workflow → Select `master` branch.

### Design

For `schedule`/`workflow_dispatch` events there's no diff, so the new code uses `github.rest.git.getTree` with `recursive: true` to enumerate all blobs. The `pull_request` and `push` paths are untouched.
```

## Combining Features — Visual Communication Toolkit

### Status Row with Badges
```markdown
![tests](https://img.shields.io/badge/tests-14%2F14-brightgreen) ![build](https://img.shields.io/badge/build-passing-brightgreen) ![breaking](https://img.shields.io/badge/breaking-no-green)
```

### Alert + Collapsed Details
```markdown
> [!WARNING]
> Breaking change — see migration guide below.

<details>
<summary>Migration guide</summary>

Steps here...

</details>
```

### Mermaid in Collapsed Section
````markdown
<details>
<summary>Architecture diagram</summary>

```mermaid
flowchart LR
    A --> B --> C
```

</details>
````

### Centered Badge Row
```html
<div align="center">

![badge1](url) ![badge2](url) ![badge3](url)

</div>
```

### Footnotes for References
```markdown
This follows the pattern established by the Working Group[^1] and matches the .NET implementation[^2].

[^1]: [WG decision comment](url)
[^2]: [.NET API reference](url)
```

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Wall of text explaining every line | Table of changes + collapsible details |
| Screenshot of terminal output | Fenced code block with actual output |
| "See my docs site for details" | Put essential info in PR body, link site as supplementary |
| Badge for every possible metric | 2-3 badges max for key status indicators |
| Mermaid diagram for simple changes | Save diagrams for flow/architecture changes |
| Cross-referencing unrelated PRs | Only reference genuinely related work |
| 10 sequential alerts | Max 1-2 per section, use tables for multiple items |
| Huge inline images | `<img width="600">` or collapsible section |
