# Security Awareness Synapse

## Identity

**Name:** Security Awareness
**Type:** Cross-cutting (fires during code-producing tasks)
**Version:** 1.0.0
**Author:** tahaa

Security Awareness is a cross-cutting concern that fires during any code-producing task. It injects security checks into the agent's reasoning without requiring explicit invocation of the security-reviewer-agent. Think of it as a security conscience — always watching, always questioning.

## When Active

- **Activation:** Fires when any agent produces code that touches: API routes, authentication, database queries, user input processing, error responses, webhook dispatch, logging
- **Phases:** 2 firing phases — SCAN, FLAG
- Does NOT fire for: documentation, design, specification, or non-code tasks

---

## Firing Phases

### Phase 1 — SCAN (During Code Production)

**Timing:** While writing any code that handles user input, auth, database, or external communication.

**Instructions:**

1. **Check input boundaries** — Is user input validated before use?
   - Query parameters, request body, URL path segments, headers
   - File uploads (type, size, name sanitization)
   - Redirect URLs (open redirect prevention)

2. **Check auth chain** — Does this route have proper guards?
   - Authentication: Is the user's identity verified?
   - Authorization: Does the user have permission for this specific resource?
   - Rate limiting: Is this public endpoint rate-limited?

3. **Check output safety** — Are responses safe?
   - Error messages don't leak internals (stack traces, query details, file paths)
   - API responses don't over-expose data (return only needed fields)
   - Headers include security defaults (CORS, CSP, X-Frame-Options)

4. **Check data handling** — Is sensitive data protected?
   - Passwords hashed with bcrypt/argon2, never stored plaintext
   - Tokens/API keys not logged or included in error responses
   - PII redacted from structured logs

### Phase 2 — FLAG (Post-Production Review)

**Timing:** After completing code, before marking task as done.

**Instructions:**

1. **Review all `fetch()` / `axios` calls** — Is the URL from user input? (SSRF risk)
2. **Review all database queries** — Are they parameterized? (SQLi risk)
3. **Review all `dangerouslySetInnerHTML` / template literals in HTML** — (XSS risk)
4. **Review all file operations** — Is the path from user input? (Path traversal risk)
5. **Review all redirects** — Is the destination URL validated? (Open redirect risk)

If any check fails, add a `// SECURITY: ` comment and flag to the user.

---

## Integration

This synapse works alongside other synapses:
- **metacognition** — Security awareness augments the MONITOR phase with security-specific confidence checks
- **security-reviewer-agent** — For full audits, delegate to the agent; this synapse handles in-flight awareness

## Output

This synapse does NOT produce separate output. It modifies agent behavior by:
1. Adding security comments to generated code where risks are identified
2. Flagging security concerns in the agent's response to the user
3. Recommending security-reviewer-agent activation for complex security-sensitive code
