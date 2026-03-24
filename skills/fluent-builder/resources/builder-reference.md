# Fluent Builder Reference

> Extracted from prompts.chat `packages/prompts.chat/src/builder/index.ts`.

## Complete Builder Template

```typescript
// types.ts
export interface BuiltPrompt {
  role: string;
  task: string;
  constraints: string[];
  steps: string[];
  format: string;
  examples: Array<{ input: string; output: string }>;
  context?: string;
}

// builder.ts
export class PromptBuilder {
  private state: Partial<BuiltPrompt> = {};

  role(role: string): this {
    this.state.role = role;
    return this;
  }

  task(task: string): this {
    this.state.task = task;
    return this;
  }

  constraints(constraints: string[]): this {
    this.state.constraints = constraints;
    return this;
  }

  addConstraint(constraint: string): this {
    if (!this.state.constraints) this.state.constraints = [];
    this.state.constraints.push(constraint);
    return this;
  }

  steps(steps: string[]): this {
    this.state.steps = steps;
    return this;
  }

  format(format: string): this {
    this.state.format = format;
    return this;
  }

  examples(examples: Array<{ input: string; output: string }>): this {
    this.state.examples = examples;
    return this;
  }

  context(context: string): this {
    this.state.context = context;
    return this;
  }

  reset(): this {
    this.state = {};
    return this;
  }

  build(): BuiltPrompt {
    if (!this.state.role) throw new Error("role() is required");
    if (!this.state.task) throw new Error("task() is required");

    return Object.freeze({
      role: this.state.role,
      task: this.state.task,
      constraints: this.state.constraints ?? [],
      steps: this.state.steps ?? [],
      format: this.state.format ?? "text",
      examples: this.state.examples ?? [],
      context: this.state.context,
    }) as BuiltPrompt;
  }
}

// Entry function
export function builder(): PromptBuilder {
  return new PromptBuilder();
}

// Reverse parser
export function fromPrompt(text: string): PromptBuilder {
  const b = new PromptBuilder();
  // Parse role from "Act as..." or "You are..."
  const roleMatch = text.match(/(?:act as|you are)\s+(?:a|an)?\s*(.+?)[\.\n]/i);
  if (roleMatch) b.role(roleMatch[1].trim());
  // Parse task from imperative sentences
  const taskMatch = text.match(/(?:your task is to|please|help me)\s+(.+?)[\.\n]/i);
  if (taskMatch) b.task(taskMatch[1].trim());
  return b;
}
```

## Presets Pattern

```typescript
// templates.ts
export const templates = {
  technical: () =>
    builder()
      .role("Senior Software Engineer")
      .format("markdown with code blocks")
      .addConstraint("Be precise and technical")
      .addConstraint("Include code examples"),

  creative: () =>
    builder()
      .role("Creative Writer")
      .format("prose")
      .addConstraint("Be imaginative and vivid")
      .addConstraint("Use sensory details"),

  analytical: () =>
    builder()
      .role("Data Analyst")
      .format("structured report with tables")
      .addConstraint("Use data-driven reasoning")
      .addConstraint("Include quantitative evidence"),
};

// Usage: templates.technical().task("Review this code").build()
```

## Multi-Type Builder Pattern

For projects needing multiple output types (like prompts.chat's text/video/audio/image builders):

```typescript
// Shared base
class BaseBuilder<T> {
  protected state: Partial<T> = {};
  // ... shared methods
}

// Specialized builders
export class VideoBuilder extends BaseBuilder<VideoPrompt> {
  duration(seconds: number): this { /* ... */ return this; }
  aspectRatio(ratio: string): this { /* ... */ return this; }
}

export class AudioBuilder extends BaseBuilder<AudioPrompt> {
  voice(voice: string): this { /* ... */ return this; }
  speed(wpm: number): this { /* ... */ return this; }
}

// Entry functions
export const video = () => new VideoBuilder();
export const audio = () => new AudioBuilder();
```
