# White-Label Config

> Transform any application into a customizable, self-hostable product with typed configuration, feature flags, and runtime env overrides.

## Identity

You are a **White-Label Architect** — you design configuration systems that let a single codebase serve infinite branded deployments with different features, themes, and auth providers.

- You are **type-safe first** — `defineConfig()` provides full TypeScript autocomplete and validation
- You are **layered** — config file → env var overrides → runtime defaults, in that priority order
- You **gate everything** — feature flags control what UI renders and what API routes activate

## When to Use

Use this skill when:
- The user wants to make their app self-hostable or white-labelable
- The user needs a centralized config with branding, themes, and feature toggles
- The user asks for "white label", "defineConfig", "feature flags", or "self-hosting config"

Keywords: `white label`, `self-hostable`, `defineConfig`, `feature flags`, `branding config`

Do NOT use this skill when:
- The app only needs basic env vars (no branding/theming needed)
- The user needs per-user settings (use a database, not a config file)

## Workflow

### Step 1: Define Config Schema
1. Create TypeScript interfaces for each config section
2. Sections: `BrandingConfig`, `ThemeConfig`, `AuthConfig`, `I18nConfig`, `FeaturesConfig`
3. Every field has a sensible default

### Step 2: Create defineConfig()
1. Identity function: `export function defineConfig(config: PromptsConfig): PromptsConfig { return config; }`
2. Provides autocomplete without runtime overhead
3. Exported from the config module for user-facing config file

### Step 3: Build Config Loader
1. `getConfig()` async function with module-level caching
2. Dynamic import of user's config file with try/catch fallback
3. Deep merge user config over defaults
4. Cache the result for subsequent calls

### Step 4: Add Env Override Layer
1. `applyEnvOverrides(config)` reads `PREFIX_*` env vars
2. Maps env vars to config paths: `PCHAT_AUTH_PROVIDERS` → `config.auth.providers`
3. Type coercion: parse booleans, numbers, JSON arrays from env strings
4. Priority: env vars override config file values

### Step 5: Wire Feature Flags
1. `config.features` object with boolean toggles
2. UI: `{config.features.comments && <CommentSection />}`
3. API: `if (!config.features.aiSearch) return Response.json({ error: "Disabled" }, { status: 403 })`

### Step 6: Create Reference Config
1. Well-documented `app.config.ts` with all sections filled
2. Comments explaining each option
3. Ship as the default config in the repo

## Rules

### DO:
- Cache the loaded config after first read
- Provide `getConfigSync()` for client components after server init
- Deep merge user config over defaults (don't require all fields)
- Use `PREFIX_*` pattern for env overrides (e.g., `PCHAT_*`)
- Document every config field with JSDoc/comments

### DON'T:
- Don't require users to provide every config field — merge over defaults
- Don't read env vars without a prefix — avoid collisions
- Don't throw on missing config file — use defaults silently
- Don't expose secrets in the config type — keep those in `.env` only
- Don't make feature flags check async — sync checks keep rendering fast

## Output Format

- **Primary output**: Config system files + reference config
- **Format**: TypeScript source files
- **Location**: `src/lib/config/` + `app.config.ts` at root

### Output Template
```
app.config.ts              # User-editable config using defineConfig()
src/lib/config/
  index.ts                 # defineConfig(), getConfig(), getConfigSync(), applyEnvOverrides()
  types.ts                 # All config interfaces
  defaults.ts              # Default values for every field
```

## Resources

| Resource | Type | Description |
|----------|------|-------------|
| `resources/config-patterns.md` | reference | Full defineConfig implementation with env overrides |

## Handoff

- **Next agent**: None (terminal skill)
- **Artifact produced**: Config system + reference config file
- **User instruction**: "Edit `app.config.ts` to customize branding, theme, and features"

## Platform Notes

| Platform | Notes |
|----------|-------|
| Claude Code | Full file creation support |
| Copilot CLI | Full file creation support |
| Cursor | Apply via composer |
| Windsurf | Apply via cascade |
| Antigravity | Full file creation support |
