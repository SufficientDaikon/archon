# YAML Prompt Schema Reference

> Extracted from prompts.chat `src/lib/ai/*.prompt.yml` + `load-prompt.ts`.

## Schema

```yaml
# <action>.prompt.yml
name: quality-check                    # Unique identifier
description: "Checks content quality"  # Human-readable description
model: gpt-4o-mini                     # Default model (overridable)
temperature: 0.3                       # Optional (0-2)
maxTokens: 1024                        # Optional

messages:
  - role: system
    content: |
      You are a quality evaluator. Assess the given content on:
      1. Clarity (0-10)
      2. Specificity (0-10)
      3. Structure (0-10)
      Return JSON: { scores: {...}, overall: number, suggestions: string[] }

  - role: user
    content: |
      Evaluate this content:

      {{content}}

      Context: {{context}}

testData:
  - description: "Basic quality check"
    variables:
      content: "Write a poem about nature"
      context: "User-submitted prompt"
    expectedFormat: "json"

  - description: "High quality input"
    variables:
      content: "Act as a senior Python developer. Review the following code for security vulnerabilities, focusing on SQL injection, XSS, and CSRF. For each issue found, provide the file path, line number, vulnerability type, severity (critical/high/medium/low), and a concrete fix with code."
      context: "Security review prompt"
    expectedFormat: "json"
```

## TypeScript Loader

```typescript
// load-prompt.ts
import fs from "fs";
import path from "path";
import yaml from "yaml";

export interface PromptTemplate {
  name: string;
  description?: string;
  model: string;
  temperature?: number;
  maxTokens?: number;
  messages: Array<{ role: "system" | "user" | "assistant"; content: string }>;
  testData?: Array<{
    description: string;
    variables: Record<string, string>;
    expectedFormat?: string;
  }>;
}

// Cache parsed prompts
const cache = new Map<string, PromptTemplate>();

export function loadPrompt(
  name: string,
  options?: { model?: string; dir?: string }
): PromptTemplate {
  if (cache.has(name) && !options?.model) return cache.get(name)!;

  const dir = options?.dir || path.join(process.cwd(), "src/lib/ai");
  const filePath = path.join(dir, `${name}.prompt.yml`);
  const raw = fs.readFileSync(filePath, "utf-8");
  const prompt = yaml.parse(raw) as PromptTemplate;

  // Validate required fields
  if (!prompt.name) throw new Error(`Prompt ${name}: missing 'name'`);
  if (!prompt.messages?.length) throw new Error(`Prompt ${name}: missing 'messages'`);

  // Apply overrides
  if (options?.model) prompt.model = options.model;
  if (process.env.PROMPT_MODEL_OVERRIDE) prompt.model = process.env.PROMPT_MODEL_OVERRIDE;

  cache.set(name, prompt);
  return prompt;
}

export function fillPrompt(
  prompt: PromptTemplate,
  variables: Record<string, string>,
  options?: { strict?: boolean }
): Array<{ role: string; content: string }> {
  return prompt.messages.map((msg) => ({
    role: msg.role,
    content: msg.content.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      if (key in variables) return variables[key];
      if (options?.strict) throw new Error(`Missing variable: {{${key}}}`);
      return match; // preserve unfilled
    }),
  }));
}
```

## Example Prompts

### Translation Prompt
```yaml
name: translate
model: gpt-4o-mini
messages:
  - role: system
    content: "You are a professional translator. Translate accurately while preserving tone and meaning."
  - role: user
    content: "Translate the following from {{source_language}} to {{target_language}}:\n\n{{text}}"
testData:
  - description: "English to Spanish"
    variables:
      source_language: "English"
      target_language: "Spanish"
      text: "Hello, how are you?"
```

### SQL Generation Prompt
```yaml
name: sql-generation
model: gpt-4o
temperature: 0.1
messages:
  - role: system
    content: |
      You are a SQL expert. Generate safe, parameterized SQL queries.
      Database: {{database_type}}
      Schema: {{schema}}
  - role: user
    content: "{{natural_language_query}}"
testData:
  - description: "Simple SELECT"
    variables:
      database_type: "PostgreSQL"
      schema: "users(id, name, email, created_at)"
      natural_language_query: "Find all users created in the last 7 days"
```

## Usage Pattern

```typescript
import { loadPrompt, fillPrompt } from "@/lib/ai/load-prompt";
import OpenAI from "openai";

const openai = new OpenAI();

async function checkQuality(content: string) {
  const prompt = loadPrompt("quality-check");
  const messages = fillPrompt(prompt, { content, context: "User submission" });

  const response = await openai.chat.completions.create({
    model: prompt.model,
    temperature: prompt.temperature,
    max_tokens: prompt.maxTokens,
    messages,
  });

  return JSON.parse(response.choices[0].message.content!);
}
```
