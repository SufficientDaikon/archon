# prompts-chat-expert

**Meta-Skill Coordinator for prompts.chat Architecture Patterns**

## Purpose

Orchestrates the 10 architecture patterns extracted from the prompts.chat codebase -- the world's largest open-source AI prompt library. These patterns cover the full spectrum of platform engineering: extensible plugin systems, fluent API builders, content quality enforcement, template engines, white-label configuration, Claude Code integration, YAML-driven prompt management, event-driven webhooks, content deduplication, and SDK-beside-app design.

## Architecture Pattern Categories

The patterns organize into three tiers:

```
PLATFORM CORE
  1. plugin-system           -> Extensible plugin architecture
  2. white-label-config      -> Self-hostable configuration
  3. sdk-beside-app          -> SDK alongside web application

CONTENT PIPELINE
  4. yaml-prompt-library     -> YAML-driven prompt management
  5. template-variables      -> Variable interpolation engine
  6. content-quality-gate    -> Quality enforcement pipeline
  7. content-deduplication   -> Duplicate detection and prevention

INTEGRATION LAYER
  8. fluent-builder          -> Fluent API construction
  9. event-webhooks          -> Event-driven webhook dispatch
 10. claude-plugin-archetype -> Claude Code plugin integration
```

---

## Routing Logic

### 1. Plugin Architecture -> **plugin-system**

**Trigger keywords:** plugin, extension, hook, extensibility, plugin registry, middleware chain, plugin lifecycle

**Use when:**
- Designing extensible plugin architectures
- Building plugin registries and discovery mechanisms
- Implementing hook-based extension points
- Managing plugin lifecycle (install, activate, deactivate)
- Creating plugin APIs and contracts

**Deliverable:** Plugin system architecture with registry, hooks, and lifecycle management

---

### 2. Fluent API Design -> **fluent-builder**

**Trigger keywords:** fluent API, builder pattern, method chaining, DSL, configuration builder, pipeline builder

**Use when:**
- Designing fluent/chainable APIs
- Building configuration or query builders
- Creating domain-specific languages via method chaining
- Implementing step-by-step builder patterns

**Deliverable:** Fluent builder implementation with typed method chains

---

### 3. Content Quality Enforcement -> **content-quality-gate**

**Trigger keywords:** quality gate, content validation, approval pipeline, review workflow, quality score, content standards

**Use when:**
- Building content approval pipelines
- Implementing quality scoring systems
- Enforcing content standards before publication
- Creating review workflows with pass/fail gates

**Deliverable:** Quality gate pipeline with configurable rules and scoring

---

### 4. Template Variable Engine -> **template-variables**

**Trigger keywords:** template, variable interpolation, placeholder, mustache, handlebars, dynamic content, variable resolution

**Use when:**
- Building template engines with variable interpolation
- Implementing placeholder resolution systems
- Creating dynamic content with user-supplied variables
- Designing template syntax and parsing

**Deliverable:** Template variable engine with parsing and interpolation

---

### 5. White-Label Configuration -> **white-label-config**

**Trigger keywords:** white-label, self-hosted, branding, theming, tenant configuration, multi-tenant, customization

**Use when:**
- Making applications self-hostable with custom branding
- Building multi-tenant configuration systems
- Implementing theme and branding customization
- Creating environment-based configuration layers

**Deliverable:** White-label configuration system with branding and theming

---

### 6. Claude Code Plugin -> **claude-plugin-archetype**

**Trigger keywords:** Claude plugin, Claude Code, MCP, tool integration, AI assistant plugin, Claude extension

**Use when:**
- Building plugins for Claude Code
- Integrating with Claude's tool system
- Creating AI assistant extensions
- Designing MCP-compatible tools

**Deliverable:** Claude Code plugin following the archetype pattern

---

### 7. YAML Prompt Management -> **yaml-prompt-library**

**Trigger keywords:** YAML prompts, prompt library, prompt catalog, structured prompts, prompt management, prompt metadata

**Use when:**
- Organizing prompts in YAML format
- Building prompt libraries with metadata
- Managing prompt versions and categories
- Creating searchable prompt catalogs

**Deliverable:** YAML-based prompt library with metadata and categorization

---

### 8. Event-Driven Webhooks -> **event-webhooks**

**Trigger keywords:** webhook, event dispatch, HMAC, callback URL, event system, notification, SSRF prevention

**Use when:**
- Building webhook dispatch systems
- Implementing event-driven notifications
- Securing webhooks with HMAC signing
- Preventing SSRF in webhook URL validation

**Deliverable:** Webhook dispatch system with HMAC signing and SSRF prevention

---

### 9. Content Deduplication -> **content-deduplication**

**Trigger keywords:** deduplication, fingerprint, similarity detection, duplicate prevention, content hash, fuzzy matching

**Use when:**
- Preventing duplicate content in the platform
- Implementing content fingerprinting
- Building similarity detection pipelines
- Configuring dedup thresholds

**Deliverable:** Dedup pipeline with fingerprinting and threshold configuration

---

### 10. SDK-Beside-App Architecture -> **sdk-beside-app**

**Trigger keywords:** SDK, client library, monorepo, API client, SDK design, library alongside app, package extraction

**Use when:**
- Designing SDKs that live alongside the web application
- Extracting shared logic into publishable packages
- Building typed API clients from application routes
- Structuring monorepos with app + SDK

**Deliverable:** SDK architecture with shared types and co-located packages

---

## Core Workflow Patterns

### New Platform Build
```
plugin-system (extensibility foundation)
    |
white-label-config (customization layer)
    |
template-variables (content engine)
    |
content-quality-gate (enforcement)
    |
sdk-beside-app (client library)
    |
DONE
```

### Content Pipeline Build
```
yaml-prompt-library (structured content)
    |
template-variables (interpolation)
    |
content-deduplication (integrity)
    |
content-quality-gate (enforcement)
    |
DONE
```

### Integration Build
```
event-webhooks (event dispatch)
    |
claude-plugin-archetype (AI integration)
    |
fluent-builder (API surface)
    |
DONE
```

---

## Decision Tree

```
What platform concern are you addressing?

+-- EXTENSIBILITY?
|   -> plugin-system
|
+-- SELF-HOSTING / BRANDING?
|   -> white-label-config
|
+-- CLIENT LIBRARY?
|   -> sdk-beside-app
|
+-- PROMPT MANAGEMENT?
|   -> yaml-prompt-library
|
+-- DYNAMIC CONTENT?
|   -> template-variables
|
+-- CONTENT QUALITY?
|   -> content-quality-gate
|
+-- DUPLICATE PREVENTION?
|   -> content-deduplication
|
+-- API DESIGN (FLUENT)?
|   -> fluent-builder
|
+-- EVENT NOTIFICATIONS?
|   -> event-webhooks
|
+-- CLAUDE CODE INTEGRATION?
    -> claude-plugin-archetype
```

---

## Skill Priority Matrix

| Task Category | Primary | Secondary | Tertiary |
|--------------|---------|-----------|----------|
| **Platform Foundation** | plugin-system | white-label-config | sdk-beside-app |
| **Content Pipeline** | yaml-prompt-library | template-variables | content-quality-gate |
| **Content Integrity** | content-deduplication | content-quality-gate | - |
| **API Design** | fluent-builder | sdk-beside-app | - |
| **AI Integration** | claude-plugin-archetype | plugin-system | - |
| **Event System** | event-webhooks | plugin-system | - |
| **Customization** | white-label-config | template-variables | - |

---

## Quality Gates

### Gate 1: Plugin Contract Stability
- **Checked by:** plugin-system
- **Criteria:** Plugin API versioned, lifecycle hooks defined, backwards compatibility maintained
- **Pass -> Plugins safe to build against**

### Gate 2: Content Quality
- **Checked by:** content-quality-gate + content-deduplication
- **Criteria:** Content passes scoring threshold, no duplicates, templates resolve correctly
- **Pass -> Content ready for publication**

### Gate 3: SDK Compatibility
- **Checked by:** sdk-beside-app
- **Criteria:** Types shared correctly, API client matches routes, package publishable
- **Pass -> SDK ready for distribution**

---

## Input/Output Contracts

### plugin-system
- **Input:** Extension requirements, hook points
- **Output:** Plugin architecture with registry and lifecycle

### fluent-builder
- **Input:** API surface requirements, configuration schema
- **Output:** Typed fluent builder with method chains

### content-quality-gate
- **Input:** Content, quality rules, scoring thresholds
- **Output:** Quality report with pass/fail and score

### template-variables
- **Input:** Template string, variable context
- **Output:** Resolved content with interpolated variables

### white-label-config
- **Input:** Branding requirements, tenant context
- **Output:** Configuration system with theming

### claude-plugin-archetype
- **Input:** Tool requirements, Claude Code integration needs
- **Output:** Claude-compatible plugin package

### yaml-prompt-library
- **Input:** Prompt content, metadata, categories
- **Output:** Structured YAML prompt catalog

### event-webhooks
- **Input:** Event types, subscriber URLs, security requirements
- **Output:** Webhook dispatch system with HMAC and SSRF protection

### content-deduplication
- **Input:** Content stream, similarity thresholds
- **Output:** Dedup pipeline with fingerprinting

### sdk-beside-app
- **Input:** App routes, shared types, distribution requirements
- **Output:** Co-located SDK package with typed client

---

## Notes for AI Assistants

- **These are architecture patterns**, not a sequential pipeline -- compose as needed
- **plugin-system is foundational** -- build it first if extensibility is a requirement
- **content-quality-gate and content-deduplication often pair together** in content pipelines
- **white-label-config is essential** for any self-hostable application
- **claude-plugin-archetype** follows specific Claude Code conventions -- consult its SKILL.md
- **sdk-beside-app** is a monorepo pattern -- ensure build tooling supports it
- **Consult each SKILL.md** before applying skill knowledge
