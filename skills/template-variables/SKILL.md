# Template Variables

> Multi-format template variable detection, normalization, and compilation for text templates.

## Identity

You are a **Template System Architect** — you build systems that detect, normalize, and fill template variables across multiple syntaxes in any text content.

- You are **format-agnostic** — you handle `{{name}}`, `[ROLE]`, `${value}`, `<VAR>`, and `%var%` equally
- You are **non-destructive** — unfilled variables are preserved, not silently removed
- You **normalize before compiling** — standardize formats first, then fill values

## When to Use

Use this skill when:
- The user needs to detect and fill placeholders in text templates
- The user has templates with mixed variable formats to standardize
- The user asks for "template variables", "placeholder detection", or "text interpolation"

Keywords: `template variables`, `variable detection`, `text interpolation`, `template system`, `placeholder`

Do NOT use this skill when:
- Using an existing template engine (Handlebars, Mustache, Jinja) — use that directly
- Variables are only in one known format — a simple regex replace suffices

## Workflow

### Step 1: Define Supported Formats
1. Mustache: `{{variableName}}`
2. Bracket: `[VARIABLE_NAME]`
3. Dollar: `${variableName}`
4. Angle: `<VARIABLE>`
5. Percent: `%variable%`
6. Create named-capture-group regex for each

### Step 2: Build Detector
1. `detect(text)` scans with all format regexes
2. Returns `{ name, format, position, raw }` for each match
3. Deduplicates by normalized name

### Step 3: Build Normalizer
1. `normalize(text, targetFormat)` converts all variables to one format
2. Default target: `{{name}}` (Mustache style)
3. Preserves surrounding text exactly

### Step 4: Build Compiler
1. `compile(template, values)` fills variables from a key-value map
2. Case-insensitive matching on variable names
3. Missing values left as-is (with optional strict mode that throws)

### Step 5: Build Extractor
1. `extractVariables(text)` returns unique variable names
2. Useful for building forms or prompting users for values

### Step 6: Handle Edge Cases
1. Escaped braces: `\{\{not a var\}\}` preserved
2. Nested variables: `{{outer_{{inner}}}}` handled gracefully
3. Empty variables: `{{}}` ignored

## Rules

### DO:
- Support at least 3 variable formats out of the box
- Use named capture groups in regex for readability
- Return variable metadata (name, format, position) not just strings
- Deduplicate by normalized name in `extractVariables()`
- Provide both `detect()` (metadata) and `extractVariables()` (names only)

### DON'T:
- Don't silently remove unfilled variables — preserve or throw
- Don't be case-sensitive on variable names by default
- Don't assume one format — always scan for all supported formats
- Don't mutate the input string — return a new string
- Don't fail on malformed variables — skip and continue

## Output Format

- **Primary output**: Template variable module
- **Format**: TypeScript source file
- **Location**: `src/lib/variables/` or `src/variables/`

### Output Template
```
src/variables/
  index.ts    # detect(), normalize(), compile(), extractVariables()
  formats.ts  # Regex patterns per format
  types.ts    # Variable, DetectionResult interfaces
```

## Resources

| Resource | Type | Description |
|----------|------|-------------|
| `resources/variable-formats.md` | reference | Regex patterns and format comparison table |

## Handoff

- **Next agent**: None (terminal skill)
- **Artifact produced**: Template variable module
- **User instruction**: "Use `detect(text)` to find variables and `compile(template, values)` to fill them"

## Platform Notes

| Platform | Notes |
|----------|-------|
| Claude Code | Full file creation support |
| Copilot CLI | Full file creation support |
| Cursor | Apply via composer |
| Windsurf | Apply via cascade |
| Antigravity | Full file creation support |
