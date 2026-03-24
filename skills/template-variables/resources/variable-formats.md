# Variable Formats Reference

> Extracted from prompts.chat `packages/prompts.chat/src/variables/index.ts`.

## Format Detection Patterns

| Format | Syntax | Regex | Example |
|--------|--------|-------|---------|
| Mustache | `{{name}}` | `/\{\{(\w+)\}\}/g` | `{{role}}` |
| Bracket | `[NAME]` | `/\[([A-Z_]+)\]/g` | `[TOPIC]` |
| Dollar | `${name}` | `/\$\{(\w+)\}/g` | `${userName}` |
| Angle | `<NAME>` | `/\<([A-Z_]+)\>/g` | `<SUBJECT>` |
| Percent | `%name%` | `/\%(\w+)\%/g` | `%language%` |

## Implementation

```typescript
// formats.ts
export const VARIABLE_PATTERNS = {
  mustache: { regex: /\{\{(\w+)\}\}/g,   wrap: (n: string) => `{{${n}}}` },
  bracket:  { regex: /\[([A-Z_]+)\]/g,   wrap: (n: string) => `[${n}]` },
  dollar:   { regex: /\$\{(\w+)\}/g,     wrap: (n: string) => `\${${n}}` },
  angle:    { regex: /<([A-Z_]+)>/g,      wrap: (n: string) => `<${n}>` },
  percent:  { regex: /%(\w+)%/g,          wrap: (n: string) => `%${n}%` },
} as const;

export type VariableFormat = keyof typeof VARIABLE_PATTERNS;

// types.ts
export interface DetectedVariable {
  name: string;
  format: VariableFormat;
  raw: string;       // original match including delimiters
  position: number;  // character index in source text
}

// index.ts
export function detect(text: string): DetectedVariable[] {
  const results: DetectedVariable[] = [];
  for (const [format, { regex }] of Object.entries(VARIABLE_PATTERNS)) {
    const pattern = new RegExp(regex.source, regex.flags);
    let match: RegExpExecArray | null;
    while ((match = pattern.exec(text)) !== null) {
      results.push({
        name: match[1],
        format: format as VariableFormat,
        raw: match[0],
        position: match.index,
      });
    }
  }
  return results.sort((a, b) => a.position - b.position);
}

export function extractVariables(text: string): string[] {
  const vars = detect(text);
  const unique = new Set(vars.map((v) => v.name.toLowerCase()));
  return [...unique];
}

export function normalize(text: string, target: VariableFormat = "mustache"): string {
  const wrap = VARIABLE_PATTERNS[target].wrap;
  let result = text;
  for (const [format, { regex }] of Object.entries(VARIABLE_PATTERNS)) {
    if (format === target) continue;
    result = result.replace(new RegExp(regex.source, regex.flags), (_, name) => wrap(name));
  }
  return result;
}

export function compile(
  template: string,
  values: Record<string, string>,
  options?: { strict?: boolean }
): string {
  let result = template;
  const lowerValues: Record<string, string> = {};
  for (const [k, v] of Object.entries(values)) {
    lowerValues[k.toLowerCase()] = v;
  }

  for (const { regex } of Object.values(VARIABLE_PATTERNS)) {
    result = result.replace(new RegExp(regex.source, regex.flags), (match, name) => {
      const value = lowerValues[name.toLowerCase()];
      if (value !== undefined) return value;
      if (options?.strict) throw new Error(`Missing variable: ${name}`);
      return match; // preserve unfilled
    });
  }
  return result;
}
```

## Usage Examples

```typescript
const text = "Hello {{name}}, your role is [ROLE] and topic is ${topic}";

// Detect all variables
detect(text);
// → [{ name: "name", format: "mustache" }, { name: "ROLE", format: "bracket" }, { name: "topic", format: "dollar" }]

// Extract unique names
extractVariables(text);
// → ["name", "role", "topic"]

// Normalize to one format
normalize(text, "mustache");
// → "Hello {{name}}, your role is {{ROLE}} and topic is {{topic}}"

// Fill values
compile(text, { name: "Alice", role: "Engineer", topic: "AI" });
// → "Hello Alice, your role is Engineer and topic is AI"
```
