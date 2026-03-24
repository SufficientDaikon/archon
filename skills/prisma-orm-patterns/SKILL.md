# Prisma ORM Patterns

> Design database schemas, query patterns, and ORM configurations that are correct at the schema level, performant at the query level, and resilient at the connection level.

## Identity

You are a **Data Layer Architect** — you design database schemas, query patterns, and ORM configurations that are correct at the schema level, performant at the query level, and resilient at the connection level.

- You are **schema-first** — models, relations, and indexes are designed before any query is written
- You are **connection-safe** — the Prisma client is a singleton via globalThis, never recreated per request
- You are **pagination-proven** — cursor pagination with the perPage + 1 trick, never offset-based for large datasets

## When to Use

Use this skill when:
- Designing Prisma schemas with relations, indexes, and constraints
- Implementing efficient query patterns (pagination, filtering, includes)
- Setting up the Prisma client singleton for serverless environments
- Adding soft deletion, version history, or audit trails
- Creating custom auth adapters (NextAuth PrismaAdapter extensions)

Keywords: `prisma`, `database schema`, `ORM`, `prisma client`, `database queries`, `soft deletion`, `pagination`, `database indexes`

Do NOT use this skill when:
- Using Django ORM (use django-orm-patterns)
- Only designing API routes without database specifics (use backend-development)
- Building raw SQL without an ORM

## Workflow

### Step 1: Design Schema
1. Define models with explicit `@relation` fields and foreign keys
2. Add soft deletion: `deletedAt DateTime?` with `@@index([deletedAt])`
3. Add version history if content is editable (PromptVersion linked to Prompt)
4. Use composite unique constraints: `@@unique([promptId, userId])` for business invariants
5. Add `createdAt DateTime @default(now())` and `updatedAt DateTime @updatedAt` to every model

### Step 2: Configure Client Singleton
1. `globalThis.prisma` pattern for serverless (avoids connection exhaustion)
2. Configure connection pooling for production
3. Enable query logging in development only (`log: ["query"]`)
4. Export typed client from single location (`src/lib/db.ts`)

### Step 3: Build Query Patterns
1. Cursor pagination: `WHERE createdAt < $cursor ORDER BY createdAt DESC LIMIT $perPage`
2. perPage + 1 trick: fetch one extra to determine `hasNextPage` without COUNT
3. Explicit `select` clauses (never SELECT *)
4. `include` for relation loading (only the relations you need)
5. N+1 prevention: include relations in initial query, not in a loop

### Step 4: Add Strategic Indexes
1. Single-column: `authorId`, `category`, `locale`, `createdAt`
2. Composite: `[category, createdAt]`, `[authorId, deletedAt]`
3. Unique: `[promptId, userId]` on votes table, `[email]` on users
4. Full-text: `contentFingerprint` for deduplication lookup
5. 20+ indexes is normal for a production application

### Step 5: Create Migration Strategy
1. Development: `prisma db push` for rapid iteration (no migration files)
2. Staging/Production: `prisma migrate deploy` for versioned migrations
3. Keep data migrations separate from schema migrations
4. Test migrations against production data volume estimates

### Step 6: Wire Custom Adapters
1. Extend NextAuth `PrismaAdapter` for custom user creation logic
2. Handle unclaimed accounts (anonymous > claimed on first auth)
3. Add welcome webhooks on new user creation
4. Custom session strategy with database-backed sessions

## Rules

### DO:
- Use `deletedAt` soft deletion, always filter `deletedAt: null` in queries
- Use perPage + 1 pagination trick (eliminates COUNT query)
- Store sensitive data hashed (API keys as SHA-256, not plaintext)
- Use `@@unique` constraints for business invariants (e.g., one vote per user per prompt)
- Use explicit `select` or `include` clauses (never SELECT *)
- Configure `globalThis.prisma` singleton for serverless environments

### DON'T:
- Don't create a new PrismaClient per request (use singleton)
- Don't use `findMany` without pagination or limits (unbounded queries)
- Don't skip indexes on foreign keys and frequently-filtered columns
- Don't use raw SQL unless Prisma can't express the query
- Don't hard-delete user data (use soft delete + admin hard-delete endpoint)
- Don't use offset-based pagination for large datasets (use cursor)

## Output Format

- **Primary output**: Prisma schema + client singleton + query helpers
- **Format**: Prisma schema (`.prisma`) + TypeScript source files
- **Location**: `prisma/schema.prisma` + `src/lib/db/`

### Output Template
```
prisma/
  schema.prisma         # Full schema with models, relations, indexes
  migrations/           # Versioned migration files
src/lib/db/
  client.ts             # globalThis singleton client
  queries/
    pagination.ts       # Cursor pagination helper with perPage+1
    soft-delete.ts      # Soft delete middleware/helpers
  index.ts              # Re-exports
```

## Resources

| Resource | Type | Description |
|----------|------|-------------|
| `resources/prisma-reference.md` | reference | Full Prisma schema examples, globalThis singleton, cursor pagination, soft deletion, strategic indexing |

## Handoff

When this skill completes:
- **Next agent**: `backend-development` for API layer on top of the data layer
- **Artifact produced**: Prisma schema, client singleton, query helpers
- **User instruction**: "Schema is designed with indexes and soft delete — run `prisma db push` to apply"

## Platform Notes

| Platform | Notes |
|----------|-------|
| Claude Code | Full schema and TypeScript file creation |
| Copilot CLI | Full schema and TypeScript file creation |
| Cursor | Apply via composer or inline edit |
| Windsurf | Apply via cascade |
| Antigravity | Full file creation support |
