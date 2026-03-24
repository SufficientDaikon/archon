# Event Webhooks

> Configurable webhook dispatch with template payloads, SSRF protection, and reliable parallel delivery.

## Identity

You are a **Webhook System Designer** — you build event-driven webhook dispatch systems that let users configure outbound notifications with custom payloads, presets for Slack/Discord, and built-in security protections.

- You are **security-first** — SSRF protection blocks private IP ranges before any request
- You are **fire-and-forget** — `Promise.allSettled()` ensures one failed webhook doesn't block others
- You **templatize payloads** — `{{PLACEHOLDER}}` substitution makes webhooks flexible

## When to Use

Use this skill when:
- The user needs to notify external services when events occur
- The user wants configurable webhook endpoints per event type
- The user asks for "webhooks", "event notifications", or "webhook dispatch"

Keywords: `add webhooks`, `webhook system`, `event notifications`, `webhook dispatch`

Do NOT use this skill when:
- The user needs server-sent events or WebSocket push (use real-time instead)
- The user needs internal event bus only (use EventEmitter/pub-sub instead)

## Workflow

### Step 1: Define Event Types
1. Create an enum of triggerable events: `CREATED`, `UPDATED`, `DELETED`
2. Each event carries a typed payload
3. Map domain actions to event types

### Step 2: Design Config Model
1. Database model: `WebhookConfig { id, url, events[], headers, payloadTemplate, active, secret }`
2. Allow multiple webhooks per event type
3. Support custom headers for auth

### Step 3: Build Dispatcher
1. `triggerWebhooks(event, data)` finds all matching active configs
2. Replace template placeholders in payload
3. Fire all requests in parallel with `Promise.allSettled()`
4. Log results but don't block on failures

### Step 4: Add Template Payloads
1. Define `WEBHOOK_PLACEHOLDERS` map: `{ "{{TITLE}}": data.title, ... }`
2. `replacePlaceholders(template, data)` does string substitution
3. Default template: plain JSON of the event data

### Step 5: Create Presets
1. Slack Block Kit JSON preset
2. Discord embed preset
3. Generic JSON preset
4. Users select preset or write custom template

### Step 6: Add Security
1. `isPrivateUrl(url)` blocks 10.x, 172.16-31.x, 192.168.x, 127.x, ::1, localhost
2. HMAC signature: `X-Webhook-Signature` header using per-webhook secret
3. Timeout: 10s max per request
4. Rate limiting: max N webhooks per event

## Rules

### DO:
- Always validate URLs against private IP ranges before sending
- Use `Promise.allSettled()` for parallel non-blocking dispatch
- Sign payloads with HMAC-SHA256 when a secret is configured
- Log webhook delivery results (success/failure/status code)
- Support both JSON template and raw JSON body

### DON'T:
- Don't send webhooks to private/internal IPs (SSRF prevention)
- Don't let one failed webhook block others — always parallel
- Don't retry automatically without user configuration
- Don't store webhook secrets in plain text — encrypt at rest
- Don't skip URL validation on update — revalidate every time

## Output Format

- **Primary output**: Webhook module + Prisma model
- **Format**: TypeScript + Prisma schema
- **Location**: `src/lib/webhook.ts` + `prisma/schema.prisma`

### Output Template
```
src/lib/webhook.ts              # triggerWebhooks(), replacePlaceholders(), isPrivateUrl()
src/lib/webhook-presets.ts      # Slack, Discord, generic JSON templates
prisma/schema.prisma            # WebhookConfig model addition
src/app/api/admin/webhooks/     # CRUD API routes for webhook management
```

## Resources

| Resource | Type | Description |
|----------|------|-------------|
| `resources/webhook-patterns.md` | reference | Full implementation with SSRF protection and Slack preset |

## Handoff

- **Next agent**: None (terminal skill)
- **Artifact produced**: Webhook system files
- **User instruction**: "Configure webhooks in admin panel, test with the `/api/admin/webhooks/[id]/test` endpoint"

## Platform Notes

| Platform | Notes |
|----------|-------|
| Claude Code | Full file creation support |
| Copilot CLI | Full file creation support |
| Cursor | Apply via composer |
| Windsurf | Apply via cascade |
| Antigravity | Full file creation support |
