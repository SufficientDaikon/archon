# SDK Scaffold Reference

> Extracted from prompts.chat `packages/prompts.chat/` architecture.

## 1. Package.json

```json
{
  "name": "my-sdk",
  "version": "0.1.0",
  "description": "Developer toolkit for my platform",
  "type": "module",
  "main": "dist/index.cjs",
  "module": "dist/index.js",
  "types": "dist/index.d.ts",
  "exports": {
    ".": {
      "import": { "types": "./dist/index.d.ts", "default": "./dist/index.js" },
      "require": { "types": "./dist/index.d.cts", "default": "./dist/index.cjs" }
    },
    "./builder": {
      "import": { "types": "./dist/builder/index.d.ts", "default": "./dist/builder/index.js" },
      "require": { "types": "./dist/builder/index.d.cts", "default": "./dist/builder/index.cjs" }
    },
    "./parser": {
      "import": { "types": "./dist/parser/index.d.ts", "default": "./dist/parser/index.js" },
      "require": { "types": "./dist/parser/index.d.cts", "default": "./dist/parser/index.cjs" }
    },
    "./quality": {
      "import": { "types": "./dist/quality/index.d.ts", "default": "./dist/quality/index.js" },
      "require": { "types": "./dist/quality/index.d.cts", "default": "./dist/quality/index.cjs" }
    },
    "./variables": {
      "import": { "types": "./dist/variables/index.d.ts", "default": "./dist/variables/index.js" },
      "require": { "types": "./dist/variables/index.d.cts", "default": "./dist/variables/index.cjs" }
    }
  },
  "bin": {
    "my-sdk": "bin/cli.js"
  },
  "files": ["dist", "bin"],
  "scripts": {
    "build": "tsup",
    "dev": "tsup --watch",
    "test": "vitest run",
    "prepublishOnly": "npm run build"
  },
  "dependencies": {
    "meow": "^13.0.0",
    "clipboardy": "^4.0.0"
  },
  "devDependencies": {
    "tsup": "^8.0.0",
    "typescript": "^5.0.0",
    "vitest": "^2.0.0"
  },
  "engines": {
    "node": ">=18"
  }
}
```

## 2. tsup.config.ts

```typescript
import { defineConfig } from "tsup";

export default defineConfig([
  // Library build
  {
    entry: {
      index: "src/index.ts",
      "builder/index": "src/builder/index.ts",
      "parser/index": "src/parser/index.ts",
      "quality/index": "src/quality/index.ts",
      "variables/index": "src/variables/index.ts",
    },
    format: ["cjs", "esm"],
    dts: true,
    sourcemap: true,
    clean: true,
    splitting: false,
    external: ["ink", "react"],
  },
  // CLI build (separate)
  {
    entry: { cli: "src/cli/index.tsx" },
    format: ["esm"],
    dts: false,
    sourcemap: false,
    banner: { js: "#!/usr/bin/env node" },
    external: ["ink", "react", "ink-text-input", "ink-spinner", "ink-select-input"],
  },
]);
```

## 3. tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
```

## 4. Barrel Export (src/index.ts)

```typescript
// Re-export all public APIs
export { builder, fromPrompt, templates } from "./builder";
export type { BuiltPrompt, PromptBuilder } from "./builder";

export { parse, toYaml, toJson, interpolate } from "./parser";
export type { ParsedPrompt } from "./parser";

export { check, validate, isValid, getSuggestions } from "./quality";
export type { QualityResult, Issue } from "./quality";

export { detect, normalize, compile, extractVariables } from "./variables";
export type { DetectedVariable } from "./variables";
```

## 5. Self-Consumption Pattern

In the web app's `package.json`:
```json
{
  "dependencies": {
    "my-sdk": "^0.1.0"
  }
}
```

In the web app's source code:
```typescript
// Import from the published package, not relative paths
import { builder } from "my-sdk/builder";
import { check } from "my-sdk/quality";
import { detect } from "my-sdk/variables";

// This proves the SDK API is complete and correct
const prompt = builder().role("Expert").task("Analyze code").build();
const quality = check(prompt.task);
const vars = detect(someTemplate);
```

## 6. CLI with Ink (Optional)

```tsx
// src/cli/index.tsx
import React from "react";
import { render } from "ink";
import meow from "meow";
import { SearchView } from "./views/SearchView";
import { DetailView } from "./views/DetailView";

const cli = meow(`
  Usage
    $ my-sdk <command> [options]

  Commands
    search <query>    Search for items
    get <id>          Get item details
    list              List all items

  Options
    --limit, -l       Max results (default: 10)
    --format, -f      Output format (json|table)
`, {
  importMeta: import.meta,
  flags: {
    limit: { type: "number", shortFlag: "l", default: 10 },
    format: { type: "string", shortFlag: "f", default: "table" },
  },
});

const [command, ...args] = cli.input;
switch (command) {
  case "search":
    render(<SearchView query={args.join(" ")} limit={cli.flags.limit} />);
    break;
  case "get":
    render(<DetailView id={args[0]} />);
    break;
  default:
    cli.showHelp();
}
```

## 7. Auto-Generated API Docs Script

```typescript
// scripts/generate-docs.ts
import ts from "typescript";
import fs from "fs";

function generateApiDocs(entryFile: string): string {
  const program = ts.createProgram([entryFile], { declaration: true });
  const sourceFile = program.getSourceFile(entryFile);
  const checker = program.getTypeChecker();
  let docs = "# API Reference\n\n";

  ts.forEachChild(sourceFile!, (node) => {
    if (ts.isExportDeclaration(node) || ts.isFunctionDeclaration(node)) {
      const symbol = checker.getSymbolAtLocation(node.name || node);
      if (symbol) {
        const type = checker.getTypeOfSymbolAtLocation(symbol, node);
        docs += `## ${symbol.getName()}\n\n`;
        docs += `\`\`\`typescript\n${checker.typeToString(type)}\n\`\`\`\n\n`;
      }
    }
  });

  return docs;
}

fs.writeFileSync("API.md", generateApiDocs("src/index.ts"));
```
