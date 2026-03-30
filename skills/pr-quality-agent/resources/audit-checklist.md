# PR Quality Audit Checklist

Run this against every PR body before shipping. Score each item PASS (P) or FAIL (F).

## Citation Audit
- [ ] Every `[SRC-N]` inline tag has a matching row in the Source Citations table
- [ ] Every Source Citations row is referenced ≥1 time in the body text
- [ ] All permalink URLs use full commit SHA (not branch name)
- [ ] All line ranges in URLs verified against actual source files
- [ ] No unsourced claims remain that a reviewer might question
- [ ] Citation index table has columns: Tag | File | What it proves

## Structure Audit
- [ ] One-line summary is the FIRST thing after badges
- [ ] shields.io badges ≤5 and each provides useful metadata
- [ ] Each significant change has numbered Before/After/Source HTML table
- [ ] Critical info (breaking changes, ordering constraints) is above fold, NOT in `<details>`
- [ ] No more than 2 consecutive `> [!ALERT]` blocks
- [ ] Scope and Limitations `<dl>` exists with ≥3 items (In scope + ≥1 Out of scope + ≥1 Not verified)
- [ ] PR checklist matches repo template format
- [ ] Document has clear `---` section dividers

## Accuracy Audit
- [ ] "Before" columns describe actual old behavior (verified against old code or docs)
- [ ] "After" columns describe actual new behavior (verified against diff)
- [ ] Behavior matrix entries are accurate (tested or code-traced)
- [ ] Test counts match actual test file (`grep -c 'It "' testfile.ps1`)
- [ ] File paths in Changes table are correct relative paths
- [ ] Mermaid diagram logic matches actual code flow

## Voice Audit
- [ ] Zero AI filler phrases ("Certainly!", "Great question!", "I'd be happy to")
- [ ] Zero marketing language ("revolutionary", "game-changing", "cutting-edge")
- [ ] Zero @mentions or GitHub usernames
- [ ] Zero first-person pronouns ("I", "we", "my")
- [ ] Reads like technical documentation, not a blog post
- [ ] Anticipates reviewer questions and answers them preemptively

## Markdown Audit
- [ ] HTML `<table>` elements use proper `<tr><th>/<td>` structure
- [ ] Mermaid code blocks are syntactically valid (test in mermaid.live)
- [ ] All `<details>` blocks have `<summary>` with `<b>` bold text
- [ ] `<dl>/<dt>/<dd>` usage is GitHub-compatible
- [ ] Zero inline `style=""` attributes (GitHub strips them)
- [ ] `<mark>`, `<ins>`, `<del>`, `<kbd>`, `<abbr>`, `<sup>` all in GitHub's 63 allowed tags
- [ ] shields.io URLs are valid and load correctly
- [ ] Mermaid `style` directives use hex colors (work in GitHub dark/light mode)

## Scoring

| Score | Action |
|-------|--------|
| 0 FAIL | Ship it |
| 1-3 FAIL | Fix and re-audit (quick fixes only) |
| 4-7 FAIL | Significant rewrite needed, re-run Phase 2→3 |
| 8+ FAIL | Start over from Phase 1 |
