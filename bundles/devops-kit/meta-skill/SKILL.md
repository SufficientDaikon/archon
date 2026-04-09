# devops-expert

**Meta-Skill Coordinator for Production Deployment**

## Purpose

Orchestrates the production deployment lifecycle covering containerization with hardened Docker builds and structured logging for runtime observability. Ensures applications are production-ready with proper build pipelines and operational visibility.

## Deployment Phases

The deployment workflow follows a build-then-observe pipeline:

```
1. CONTAINERIZATION  -> docker-production-build
2. OBSERVABILITY     -> structured-logging
```

---

## Routing Logic

### 1. Containerization and Production Builds -> **docker-production-build**

**Trigger keywords:** Docker, Dockerfile, container, multi-stage build, standalone output, production image, security hardening, distroless, alpine, build optimization

**Use when:**
- Creating production Docker images
- Designing multi-stage build pipelines
- Optimizing image size and build cache
- Hardening container security (non-root, read-only fs)
- Configuring standalone output for Next.js
- Setting up health checks and graceful shutdown
- Building CI/CD container pipelines

**Deliverable:** Production Dockerfile with multi-stage builds and security hardening

**Example requests:**
- "Create a production Dockerfile for this Next.js app"
- "Optimize Docker image size"
- "Add security hardening to the container"
- "Set up multi-stage build with standalone output"
- "Configure Docker health checks"

---

### 2. Structured Logging and Observability -> **structured-logging**

**Trigger keywords:** logging, Pino, JSON logs, request correlation, trace ID, log levels, observability, monitoring, structured output, error tracking

**Use when:**
- Setting up application logging infrastructure
- Implementing JSON structured logging with Pino
- Adding request correlation and trace IDs
- Configuring log levels per environment
- Building request/response logging middleware
- Integrating with log aggregation systems
- Setting up error tracking and alerting hooks

**Deliverable:** Pino-based structured logging setup with request correlation

**Example requests:**
- "Set up structured logging for this service"
- "Add request correlation to API routes"
- "Configure Pino with environment-aware log levels"
- "Implement request/response logging middleware"
- "Set up JSON logging for production"

---

## Core Deployment Workflow

### Full Production Pipeline
```
docker-production-build (containerize application)
    |
structured-logging (add observability)
    |
DONE -- production-ready deployment
```

### Container-Only Pipeline
```
docker-production-build (build + harden)
    |
DONE
```

### Observability-First Pipeline
```
structured-logging (instrument application)
    |
docker-production-build (containerize with logging)
    |
DONE
```

---

## Decision Tree

```
What deployment concern are you addressing?

+-- NEED CONTAINER OR BUILD PIPELINE?
|   -> docker-production-build
|
+-- NEED LOGGING OR OBSERVABILITY?
    -> structured-logging
```

---

## State-Based Routing

| Current State | Next Action | Routed To |
|---------------|-------------|-----------|
| **Application Ready** | Containerize | docker-production-build |
| **Container Built** | Add observability | structured-logging |
| **No Logging** | Instrument app | structured-logging |
| **Image Too Large** | Optimize build | docker-production-build |
| **No Correlation IDs** | Add request tracing | structured-logging |
| **Security Audit** | Harden container | docker-production-build |

---

## Skill Priority Matrix

| Task Category | Primary | Secondary |
|--------------|---------|-----------|
| **New Deployment** | docker-production-build | structured-logging |
| **Debugging Production** | structured-logging | docker-production-build |
| **Performance** | docker-production-build | structured-logging |
| **Security** | docker-production-build | structured-logging |
| **Monitoring** | structured-logging | - |

---

## Quality Gates

### Gate 1: Container Security
- **Checked by:** docker-production-build
- **Criteria:** Non-root user, minimal base image, no secrets in layers, health check defined, read-only filesystem where possible
- **Pass -> Deploy or proceed to observability**

### Gate 2: Observability Readiness
- **Checked by:** structured-logging
- **Criteria:** JSON structured output, request correlation in place, error tracking configured, log levels appropriate per environment
- **Pass -> Production ready**

---

## Input/Output Contracts

### docker-production-build
- **Input:** Application source, runtime requirements, deployment target
- **Output:** Production Dockerfile, build pipeline config, security hardening checklist

### structured-logging
- **Input:** Application framework, logging requirements, deployment environment
- **Output:** Pino logger config, request correlation middleware, log format specification

---

## Notes for AI Assistants

- **Always harden containers** -- non-root, minimal base, no build tools in final stage
- **Never log secrets** -- sanitize sensitive fields in structured logging
- **Pair containerization with observability** -- a deployed container without logging is a black box
- **Multi-stage builds are mandatory** -- never ship build dependencies to production
- **Log in JSON** -- human-readable logs are for development only
- **Consult each SKILL.md** before applying skill knowledge
