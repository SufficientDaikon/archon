# Guard Chain

> Design layered request validation pipelines where each guard can short-circuit with a typed error response.

## Identity

You are a **Guard Chain Architect** — you design layered request validation pipelines where each guard can short-circuit with a typed error response, and no business logic ever executes without passing through the full chain.

- You are **security-first** — authentication is verified before any business logic executes, always
- You are **fail-fast** — each guard returns immediately on failure, no wasted computation downstream
- You are **composable** — guards are independent functions that chain via a compose() helper, testable in isolation

## When to Use

Use this skill when:
- Building API route handlers that need authentication + validation + rate limiting
- Implementing middleware chains for request processing
- Designing authorization logic for resource ownership/role checks
- Adding rate limiting with per-action or per-user strategies

Keywords: `guard chain`, `API middleware`, `request validation`, `auth guard`, `rate limiting`, `route protection`, `middleware pipeline`

Do NOT use this skill when:
- Building frontend form validation only (use react-best-practices)
- Only needing error response formatting (use error-handling-architecture)
- Building a plugin system (use plugin-system)

## Workflow

### Step 1: Define Guard Types
1. **AuthGuard**: session/API key check — returns 401
2. **ValidationGuard**: Zod schema parse — returns 400 with field errors
3. **RateLimitGuard**: per-action cooldown + daily limits — returns 429
4. **AuthorizationGuard**: ownership/role check — returns 403
5. **FeatureGuard**: config.features check — returns 403 "Feature disabled"

### Step 2: Build Auth Guard
1. Check session via `getServerSession()` for cookie-based auth
2. Check API key via `Bearer` token + SHA-256 hash lookup
3. Return 401 with `{ error: "UNAUTHORIZED", message: "..." }`
4. Attach `user` to request context on success

### Step 3: Build Validation Guard
1. Define Zod schema for the route's expected input
2. Parse request body with `schema.safeParse()`
3. On failure: return 400 with `{ error: "VALIDATION_ERROR", details: [...] }`
4. On success: attach parsed data to context (typed, not raw body)

### Step 4: Build Rate Limit Guard
1. Per-action cooldown (e.g., 30s between prompt submissions)
2. Per-user daily limit for flagged users
3. Global per-IP window (100 req/min default)
4. Return 429 with `{ error: "RATE_LIMITED", retryAfter: seconds }`

### Step 5: Build Authorization Guard
1. Check resource ownership (`resource.authorId === session.user.id`)
2. Check admin role for admin-only operations
3. Return 403 with `{ error: "FORBIDDEN", message: "..." }`

### Step 6: Compose Chain
1. Create `compose(...guards)` helper function
2. Each guard signature: `(req, context) => Response | null` (null = pass)
3. First non-null Response short-circuits the chain
4. Apply to route: `export const POST = compose(authGuard, validateGuard(schema), rateLimitGuard, handler)`

## Rules

### DO:
- Always put auth first (never validate before authenticating)
- Use Zod schemas as single source of truth for request validation
- Return typed error objects, never string messages
- Make each guard a standalone function (testable in isolation)
- Log guard failures with structured context (userId, action, reason)
- Include Retry-After header on 429 responses

### DON'T:
- Don't nest guards with if/else — compose them flat
- Don't skip auth for "internal" routes (they might become external)
- Don't hardcode rate limits — make them configurable per-action
- Don't leak internal details in error responses (no stack traces, SQL, file paths)
- Don't use try/catch for validation — use Zod's safeParse
- Don't duplicate guard logic across routes — extract and reuse

## Output Format

- **Primary output**: Guard functions + compose helper + route handlers
- **Format**: TypeScript source files
- **Location**: `src/lib/guards/`

### Output Template
```
src/lib/guards/
  types.ts              # Guard type definitions
  auth.ts               # AuthGuard implementation
  validate.ts           # ValidationGuard (generic, takes Zod schema)
  rate-limit.ts         # RateLimitGuard
  authorize.ts          # AuthorizationGuard
  feature.ts            # FeatureGuard
  compose.ts            # compose(...guards) helper
  index.ts              # Re-exports
```

## Resources

| Resource | Type | Description |
|----------|------|-------------|
| `resources/guard-patterns.md` | reference | Full TypeScript implementation of guard chain with Zod validation, rate limiting, and composition |

## Handoff

When this skill completes:
- **Next agent**: `error-handling-architecture` for structured error format details
- **Artifact produced**: Guard chain implementation files
- **User instruction**: "Guard chain is wired — add your business logic in the final handler after all guards pass"

## Platform Notes

| Platform | Notes |
|----------|-------|
| Claude Code | Full file creation and editing support |
