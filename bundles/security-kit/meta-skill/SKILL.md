# security-expert

**Meta-Skill Coordinator for Defense-in-Depth Security**

## Purpose

Orchestrates a layered security architecture covering request-level guard chains, webhook dispatch security with SSRF prevention, comprehensive error handling with proper boundaries, and structured logging for security observability. Every layer reinforces the others -- defense in depth means no single point of failure.

## Security Layers

The security model follows a defense-in-depth strategy:

```
1. REQUEST GUARDS     -> guard-chain
2. WEBHOOK SECURITY   -> event-webhooks
3. ERROR BOUNDARIES   -> error-handling-architecture
4. SECURITY LOGGING   -> structured-logging
```

---

## Routing Logic

### 1. Request Guard Pipeline -> **guard-chain**

**Trigger keywords:** guard chain, auth middleware, validation, rate limiting, API protection, request pipeline, composable guards, authorization

**Use when:**
- Building API routes with authentication and validation
- Composing guard chains (auth + validation + rate limiting)
- Implementing role-based or permission-based access control
- Adding rate limiting to endpoints
- Designing reusable guard middleware
- Building request validation pipelines

**Deliverable:** Composable guard chain with auth, validation, and rate limiting

**Example requests:**
- "Add guard chain to this API route"
- "Implement auth + validation + rate limiting"
- "Build role-based access control middleware"
- "Design a reusable guard pipeline"
- "Protect this endpoint with composable guards"

---

### 2. Webhook Dispatch Security -> **event-webhooks**

**Trigger keywords:** webhook, SSRF, HMAC, callback URL validation, webhook signing, IP allowlist, URL validation, outbound request security

**Use when:**
- Securing webhook dispatch systems
- Preventing SSRF attacks in callback URLs
- Implementing HMAC signature verification
- Validating outbound request targets
- Building secure event notification systems
- Configuring IP allowlists for webhook targets

**Deliverable:** Secure webhook system with SSRF prevention and HMAC signing

**Example requests:**
- "Secure this webhook dispatch against SSRF"
- "Add HMAC signing to webhook payloads"
- "Validate callback URLs before dispatching"
- "Build a secure event notification system"
- "Implement webhook signature verification"

---

### 3. Error Handling Architecture -> **error-handling-architecture**

**Trigger keywords:** error handling, error boundary, error taxonomy, graceful degradation, error response, exception strategy, error codes, fault tolerance

**Use when:**
- Designing comprehensive error handling strategies
- Building error taxonomies (operational vs programmer errors)
- Implementing error boundaries that prevent cascade failures
- Creating consistent error response formats
- Adding graceful degradation to critical paths
- Designing error codes and client-facing error messages

**Deliverable:** Error handling architecture with taxonomy, boundaries, and response formats

**Example requests:**
- "Design error handling for this service"
- "Implement error boundaries for this API"
- "Create an error taxonomy for the application"
- "Add graceful degradation to this critical path"
- "Standardize error response format across endpoints"

---

### 4. Security Observability -> **structured-logging**

**Trigger keywords:** security logging, audit trail, request correlation, anomaly detection, log sanitization, PII redaction, security events, forensics

**Use when:**
- Setting up security event logging
- Building audit trails for sensitive operations
- Adding request correlation for security forensics
- Sanitizing logs to prevent sensitive data exposure
- Implementing PII redaction in log output
- Creating security-specific log channels

**Deliverable:** Security-aware structured logging with audit trails and PII redaction

**Example requests:**
- "Set up security event logging"
- "Add audit trail for admin operations"
- "Implement PII redaction in logs"
- "Configure security logging with request correlation"
- "Build forensics-ready logging for auth events"

---

## Core Security Workflow (Layered)

### Full Defense-in-Depth Pipeline
```
guard-chain (protect request entry)
    |
event-webhooks (secure outbound dispatch)
    |
error-handling-architecture (contain failures)
    |
structured-logging (observe everything)
    |
DONE -- all layers secured
```

### API Security Pipeline
```
guard-chain (auth + validation + rate limiting)
    |
error-handling-architecture (error boundaries)
    |
structured-logging (audit trail)
    |
DONE
```

### Webhook Security Pipeline
```
event-webhooks (SSRF prevention + HMAC)
    |
error-handling-architecture (dispatch failure handling)
    |
structured-logging (webhook event logging)
    |
DONE
```

---

## Decision Tree

```
What security concern are you addressing?

+-- PROTECTING API ROUTES?
|   -> guard-chain
|
+-- SECURING OUTBOUND WEBHOOKS?
|   -> event-webhooks
|
+-- HANDLING ERRORS SAFELY?
|   -> error-handling-architecture
|
+-- LOGGING SECURITY EVENTS?
|   -> structured-logging
|
+-- FULL SECURITY AUDIT?
    -> ALL SKILLS (layered review)
```

---

## State-Based Routing

| Current State | Next Action | Routed To |
|---------------|-------------|-----------|
| **Unprotected Endpoint** | Add guards | guard-chain |
| **Guards in Place** | Secure webhooks | event-webhooks |
| **Webhooks Secured** | Add error boundaries | error-handling-architecture |
| **Errors Handled** | Add security logging | structured-logging |
| **Security Incident** | Review logs | structured-logging |
| **SSRF Vulnerability** | Fix webhook validation | event-webhooks |
| **Error Cascade** | Add boundaries | error-handling-architecture |

---

## Skill Priority Matrix

| Task Category | Primary | Secondary | Tertiary |
|--------------|---------|-----------|----------|
| **API Security** | guard-chain | error-handling-architecture | structured-logging |
| **Webhook Security** | event-webhooks | structured-logging | error-handling-architecture |
| **Error Strategy** | error-handling-architecture | structured-logging | guard-chain |
| **Audit/Forensics** | structured-logging | guard-chain | - |
| **Full Security Review** | guard-chain | event-webhooks | error-handling-architecture |

---

## Quality Gates

### Gate 1: Request Protection
- **Checked by:** guard-chain
- **Criteria:** All endpoints guarded, auth required for protected routes, validation present, rate limits configured
- **Pass -> Requests are safe at the boundary**

### Gate 2: Outbound Security
- **Checked by:** event-webhooks
- **Criteria:** SSRF prevention active, HMAC signing enabled, callback URLs validated, no internal targets reachable
- **Pass -> Outbound dispatch is safe**

### Gate 3: Failure Containment
- **Checked by:** error-handling-architecture
- **Criteria:** Error boundaries prevent cascades, error responses sanitized (no stack traces to clients), graceful degradation configured
- **Pass -> Failures are contained**

### Gate 4: Observability
- **Checked by:** structured-logging
- **Criteria:** Security events logged, PII redacted, request correlation active, audit trail complete
- **Pass -> Security posture is observable**

---

## Input/Output Contracts

### guard-chain
- **Input:** Route handler, auth requirements, validation schema, rate limit config
- **Output:** Composable guard chain wrapping the route handler

### event-webhooks
- **Input:** Event type, subscriber URLs, payload, signing secret
- **Output:** Secure dispatch with SSRF checks and HMAC signatures

### error-handling-architecture
- **Input:** Error types, boundary definitions, degradation strategies
- **Output:** Error taxonomy, boundary implementations, response format specification

### structured-logging
- **Input:** Log events, security context, PII field list
- **Output:** Structured JSON logs with redaction, correlation, and audit metadata

---

## Notes for AI Assistants

- **Defense in depth means ALL layers** -- never rely on a single security measure
- **Guard chains are the first line** -- always start with request protection
- **Never expose stack traces** to clients -- use error-handling-architecture for safe responses
- **SSRF is critical** -- always validate webhook URLs against internal network ranges
- **Sanitize logs** -- structured-logging must redact PII and secrets
- **Security logging is not optional** -- every security-relevant operation must be logged
- **Consult each SKILL.md** before applying skill knowledge
- **Compose layers** -- guard-chain at the boundary, error-handling inside, logging everywhere
