# data-layer-expert

**Meta-Skill Coordinator for Data Layer Architecture**

## Purpose

Orchestrates the complete data layer lifecycle from database schema design through ORM patterns, connection management, content integrity enforcement, and API construction. Ensures each layer is built bottom-up with proper foundations before higher-level concerns.

## Data Layer Phases

The data layer follows a bottom-up construction workflow:

```
1. SCHEMA DESIGN       -> prisma-orm-patterns
2. CONNECTION MGMT     -> singleton-patterns
3. CONTENT INTEGRITY   -> content-deduplication
4. API CONSTRUCTION    -> backend-development
```

---

## Routing Logic

### 1. Schema Design and Query Patterns -> **prisma-orm-patterns**

**Trigger keywords:** schema, model, migration, query, relation, Prisma, database design, index, compound key, findMany, upsert

**Use when:**
- Designing database schemas and relations
- Writing Prisma models with proper indexes
- Optimizing database queries
- Setting up migrations
- Designing compound unique constraints
- Choosing between query strategies (findMany vs raw SQL)
- Modeling many-to-many or polymorphic relations

**Deliverable:** Prisma schema, migration files, typed query patterns

**Example requests:**
- "Design the database schema for this feature"
- "Optimize this slow Prisma query"
- "Add a compound index for these fields"
- "Model user-to-organization many-to-many"
- "Set up cascade deletes for this relation"

---

### 2. Connection and Instance Management -> **singleton-patterns**

**Trigger keywords:** singleton, connection pool, globalThis, hot reload, PrismaClient instance, connection exhaustion, serverless

**Use when:**
- Setting up database client singletons
- Preventing connection exhaustion in development (hot reload)
- Managing global instances in serverless environments
- Configuring connection pool sizes
- Handling PrismaClient lifecycle in Next.js

**Deliverable:** Singleton implementation with globalThis pattern

**Example requests:**
- "Set up PrismaClient singleton for Next.js"
- "Fix connection exhaustion in development"
- "Configure connection pooling for serverless"
- "Implement globalThis singleton pattern"

---

### 3. Content Integrity and Deduplication -> **content-deduplication**

**Trigger keywords:** deduplication, fingerprint, similarity, content hash, duplicate detection, fuzzy matching, threshold

**Use when:**
- Implementing content fingerprinting
- Detecting duplicate or near-duplicate content
- Configuring similarity thresholds
- Building content pipelines with integrity checks
- Choosing between exact-match and fuzzy dedup strategies

**Deliverable:** Deduplication pipeline with configurable thresholds

**Example requests:**
- "Add content deduplication to the ingestion pipeline"
- "Implement fingerprinting for uploaded documents"
- "Detect near-duplicate entries in the database"
- "Configure similarity threshold for content matching"

---

### 4. API Layer Construction -> **backend-development**

**Trigger keywords:** API route, endpoint, guard chain, REST, request validation, middleware, API contract, route handler

**Use when:**
- Building API endpoints on top of the data layer
- Designing REST API contracts
- Implementing guard chains (auth, validation, rate limiting)
- Structuring route handlers with proper error boundaries
- Connecting API layer to Prisma queries

**Deliverable:** Production API routes with guard chains and typed contracts

**Example requests:**
- "Build CRUD endpoints for this resource"
- "Add guard chain to this API route"
- "Design the REST API contract for user management"
- "Implement pagination for this list endpoint"
- "Add request validation to this route"

---

## Core Data Layer Workflow (Bottom-Up)

### Standard Data Layer Pipeline
```
prisma-orm-patterns (design schema)
    |
singleton-patterns (connection management)
    |
content-deduplication (integrity layer)
    |
backend-development (API surface)
    |
DONE
```

### Schema-Only Pipeline
```
prisma-orm-patterns (design + migrate)
    |
singleton-patterns (connection setup)
    |
DONE
```

### API Feature Pipeline
```
prisma-orm-patterns (add/update models)
    |
backend-development (build endpoints)
    |
DONE
```

---

## Decision Tree

```
What layer are you working on?

+-- NEED SCHEMA OR QUERY DESIGN?
|   -> prisma-orm-patterns
|
+-- NEED CONNECTION MANAGEMENT?
|   -> singleton-patterns
|
+-- NEED CONTENT INTEGRITY?
|   -> content-deduplication
|
+-- NEED API ENDPOINTS?
    -> backend-development
```

---

## State-Based Routing

| Current State | Next Action | Routed To |
|---------------|-------------|-----------|
| **Greenfield** | Design schema | prisma-orm-patterns |
| **Schema Ready** | Set up connections | singleton-patterns |
| **Connections Managed** | Add integrity checks | content-deduplication |
| **Data Layer Complete** | Build API surface | backend-development |
| **Query Performance Issue** | Optimize queries | prisma-orm-patterns |
| **Connection Exhaustion** | Fix singleton | singleton-patterns |
| **Duplicate Content** | Add dedup pipeline | content-deduplication |

---

## Skill Priority Matrix

| Task Category | Primary | Secondary | Tertiary |
|--------------|---------|-----------|----------|
| **New Feature** | prisma-orm-patterns | backend-development | singleton-patterns |
| **Performance** | prisma-orm-patterns | singleton-patterns | - |
| **Data Quality** | content-deduplication | prisma-orm-patterns | - |
| **API Development** | backend-development | prisma-orm-patterns | - |
| **Infrastructure** | singleton-patterns | prisma-orm-patterns | - |

---

## Quality Gates

### Gate 1: Schema Correctness
- **Checked by:** prisma-orm-patterns
- **Criteria:** Relations valid, indexes defined, migrations clean, no N+1 patterns
- **Pass -> Proceed to singleton-patterns or backend-development**

### Gate 2: Connection Safety
- **Checked by:** singleton-patterns
- **Criteria:** No connection leaks, globalThis pattern in place, pool sized correctly
- **Pass -> Proceed to next layer**

### Gate 3: Content Integrity
- **Checked by:** content-deduplication
- **Criteria:** Fingerprinting active, thresholds configured, dedup pipeline tested
- **Pass -> Proceed to API layer**

---

## Input/Output Contracts

### prisma-orm-patterns
- **Input:** Feature requirements, data relationships
- **Output:** Prisma schema, migrations, typed query patterns

### singleton-patterns
- **Input:** Runtime environment (serverless, long-running, dev)
- **Output:** Singleton implementation with proper lifecycle

### content-deduplication
- **Input:** Content stream, similarity requirements
- **Output:** Dedup pipeline with fingerprinting and threshold config

### backend-development
- **Input:** Data models, API contract requirements
- **Output:** Route handlers with guard chains and validation

---

## Notes for AI Assistants

- **Always start with prisma-orm-patterns** when building from scratch
- **Never skip singleton-patterns** for database-connected services
- **Layer bottom-up** -- schema first, then connections, then integrity, then API
- **Check for N+1 queries** when designing data access patterns
- **Use guard chains** from backend-development for all API routes
- **Consult each SKILL.md** before applying skill knowledge
- **Connection pooling differs** between serverless and long-running -- check environment
