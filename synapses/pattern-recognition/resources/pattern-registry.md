# Pattern Registry — Complete Signature Reference

This registry maps code signatures to Archon skills. Each entry defines the structural indicators that trigger a pattern detection.

---

## Plugin/Registry Pattern → `plugin-system`

**Signatures:**
- `new Map()` used as a registry with `set()` / `get()` / `has()` accessors
- `register(name, handler)` function that stores entries in a collection
- Plugin loader that dynamically imports from a directory
- `plugins.forEach(p => p.init())` initialization loops

**Example trigger:**
```typescript
const registry = new Map<string, Plugin>();
function register(name: string, plugin: Plugin) { registry.set(name, plugin); }
function get(name: string) { return registry.get(name); }
```

---

## Template Variables → `template-variables`

**Signatures:**
- `{{variableName}}` double-brace interpolation
- `.replace(/\{\{(\w+)\}\}/g, ...)` regex-based template replacement
- Template rendering functions that accept a `variables` or `context` object

**Example trigger:**
```typescript
const rendered = template.replace(/\{\{(\w+)\}\}/g, (_, key) => variables[key] ?? '');
```

---

## Fluent Builder → `fluent-builder`

**Signatures:**
- Method chaining returning `this` or a new builder instance
- `.builder()` / `.create()` static factory methods
- `.with*()` setter methods (e.g., `.withName()`, `.withConfig()`)
- `.build()` terminal method that produces the final object

**Example trigger:**
```typescript
const config = Config.builder()
  .withName('app')
  .withPort(3000)
  .withDebug(true)
  .build();
```

---

## Guard Chain / Middleware → `guard-chain`

**Signatures:**
- `middleware: []` array composition
- `(req, res, next) => { ... next(); }` handler signature
- `.use(handler)` registration method
- `auth → validate → rate-limit → authorize → execute` sequential processing

**Example trigger:**
```typescript
app.use(authenticate);
app.use(rateLimit({ windowMs: 15 * 60 * 1000 }));
router.post('/api/data', validate(schema), authorize('admin'), handler);
```

---

## Singleton → `singleton-patterns`

**Signatures:**
- `globalThis.__instanceName` global instance caching
- Module-scoped `let instance: T | null = null` with lazy initialization
- `getInstance()` accessor pattern
- `if (!global.__prisma) global.__prisma = new PrismaClient()`

**Example trigger:**
```typescript
const globalForPrisma = globalThis as unknown as { prisma: PrismaClient };
export const prisma = globalForPrisma.prisma ?? new PrismaClient();
if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;
```

---

## Async Side Effects → `async-side-effects`

**Signatures:**
- `Promise.allSettled([...])` for parallel fire-and-forget operations
- `void sendEmail(...)` fire-and-forget calls (no `await`)
- Background task queues or job dispatchers
- `setTimeout` / `setImmediate` for deferred work
- `AbortController` with timeout for bounded async operations

**Example trigger:**
```typescript
void Promise.allSettled([
  sendWelcomeEmail(user),
  trackSignupEvent(user),
  syncToAnalytics(user),
]);
```

---

## Prisma ORM → `prisma-orm-patterns`

**Signatures:**
- `prisma.model.findMany()` / `findUnique()` / `create()` / `update()`
- `include: { relation: true }` eager loading
- `prisma.$transaction([...])` transaction blocks
- `schema.prisma` model definitions

---

## Event Webhooks → `event-webhooks`

**Signatures:**
- `fetch(webhookUrl, { method: 'POST', body: JSON.stringify(payload) })`
- Event emitter patterns with `emit()` / `on()` / `off()`
- Webhook signature verification (`crypto.timingSafeEqual`)
- Retry logic with exponential backoff for delivery

---

## Lazy Import → `lazy-import-patterns`

**Signatures:**
- `const Component = dynamic(() => import('...'))` (Next.js)
- `React.lazy(() => import('...'))`
- `await import('module')` conditional dynamic imports
- Feature flag guards: `if (featureEnabled) { const mod = await import(...) }`

---

## Server Components → `server-component-patterns`

**Signatures:**
- `"use server"` directive
- `async function ComponentName()` (async React component = server component)
- `"use client"` boundary markers
- Server Actions: `async function action() { "use server"; ... }`

---

## Content Dedup → `content-deduplication`

**Signatures:**
- Hash generation: `crypto.createHash('sha256').update(content).digest('hex')`
- Similarity scoring / fuzzy matching
- Fingerprint comparison before insert
- `WHERE hash = ?` uniqueness checks

---

## Structured Logging → `structured-logging`

**Signatures:**
- `pino()` or `pino({ ... })` logger initialization
- `logger.info({ requestId, userId, ... }, 'message')` structured context
- Correlation ID propagation (`x-request-id` headers)
- Log level configuration by environment

---

## Docker Production → `docker-production-build`

**Signatures:**
- `FROM node:*-alpine AS builder` multi-stage builds
- `COPY --from=builder /app/.next/standalone ./`
- `RUN npm ci --only=production`
- `USER node` (non-root execution)

---

## Vitest Testing → `vitest-unit-patterns`

**Signatures:**
- `import { describe, it, expect, vi } from 'vitest'`
- `vi.mock('module')` / `vi.spyOn(obj, 'method')`
- `beforeEach(() => { vi.clearAllMocks() })`

---

## i18n → `i18n-strategy`

**Signatures:**
- `useTranslation()` / `t('key.path')` translation hooks
- `messages/{locale}.json` or `locales/{lang}/` directory structure
- `<IntlProvider>` or `next-intl` configuration
- Locale routing: `[locale]/page.tsx`

---

## Content Moderation → `content-moderation-pipeline`

**Signatures:**
- Content scoring functions with threshold checks
- Flag/approve/reject status enums
- Soft-delete patterns (`deletedAt` field, not hard delete)
- Moderation queue with review workflow

---

## White Label → `white-label-config`

**Signatures:**
- Tenant-specific configuration objects
- Theme/brand override systems
- `config.brandName` / `config.primaryColor` tenant theming
- Multi-tenant routing or subdomain-based switching

---

## YAML Prompts → `yaml-prompt-library`

**Signatures:**
- YAML files with `prompt:`, `variables:`, `model:` fields
- Prompt template loading from `.yaml` / `.yml` files
- Variable injection into prompt strings
- Prompt chaining with output piping

---

## SDK-beside-App → `sdk-beside-app`

**Signatures:**
- `packages/sdk/` or `libs/client/` alongside `apps/`
- Shared type definitions imported by both SDK and app
- Monorepo workspace references to client packages
- API client generation or hand-rolled SDK classes

---

## Error Architecture → `error-handling-architecture`

**Signatures:**
- Custom error classes extending `Error`
- Error boundary components (`componentDidCatch` or `ErrorBoundary`)
- Centralized error handler middleware
- Error code enums or maps

---

## E2E Testing → `e2e-testing-patterns`

**Signatures:**
- `import { test, expect } from '@playwright/test'`
- `cy.visit()` / `cy.get()` Cypress commands
- Page Object Model classes
- `data-testid` attribute selectors
