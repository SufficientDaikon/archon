# orchestration-expert

**Meta-Skill Coordinator for Multi-Agent Orchestration**

## Purpose

Orchestrates the core control plane for multi-agent workflows: classifying task complexity to select optimal agents and models, managing context window budgets across long sessions, and conducting evidence-based research before execution. This is the meta-layer that other bundles depend on for intelligent routing and resource management.

## Orchestration Phases

The orchestration layer operates in an assess-then-execute model:

```
1. COMPLEXITY ASSESSMENT  -> complexity-router
2. CONTEXT MANAGEMENT     -> context-curator
3. EVIDENCE GATHERING     -> archon-scout
```

---

## Routing Logic

### 1. Complexity Classification and Agent Routing -> **complexity-router**

**Trigger keywords:** complexity, classify, tier, routing, agent selection, model choice, TRIVIAL, SIMPLE, MODERATE, COMPLEX, EXPERT, effort scaling

**Use when:**
- Classifying incoming tasks by complexity tier
- Selecting the optimal agent or model for a task
- Deciding between parallel vs sequential execution
- Scaling effort based on task requirements
- Routing tasks to appropriate skill bundles
- Determining whether to spawn sub-agents

**Deliverable:** Complexity classification with agent/model routing recommendation

**Example requests:**
- "Classify this task's complexity"
- "Which agent should handle this?"
- "Should this be parallel or sequential?"
- "What effort tier is this task?"
- "Route this request to the right skill"

---

### 2. Context Window Management -> **context-curator**

**Trigger keywords:** context window, token budget, compression, session persistence, phase transition, context pressure, summarize, handoff, memory management

**Use when:**
- Managing context window budget across long sessions
- Compressing context during phase transitions
- Persisting session state across agent handoffs
- Monitoring token usage and context pressure
- Deciding what to keep, compress, or evict from context
- Building handoff summaries between agents
- Managing the 1M token window efficiently

**Deliverable:** Context budget report, compression strategy, or handoff summary

**Example requests:**
- "Context is getting large, compress non-essential sections"
- "Build a handoff summary for the next agent"
- "How much context budget remains?"
- "Persist session state for continuation"
- "Manage phase transition context"

---

### 3. Evidence-Based Research -> **archon-scout**

**Trigger keywords:** research, investigate, evidence, sources, scout, prior art, documentation lookup, validate claim, conflict resolution, citation

**Use when:**
- Research is needed before building
- Validating claims with evidence and sources
- Investigating prior art or existing solutions
- Resolving conflicting information from multiple sources
- Gathering documentation for a technology or pattern
- Building evidence packages for architectural decisions
- Scouting feasibility before committing to an approach

**Deliverable:** Evidence report with sourced citations and conflict resolution

**Example requests:**
- "Research best practices for this pattern"
- "Validate whether this approach is sound"
- "Find prior art for this feature"
- "Gather documentation on this library"
- "Resolve conflicting guidance on this topic"

---

## Core Orchestration Workflow

### Standard Orchestration Pipeline
```
complexity-router (classify task)
    |
archon-scout (research if needed)
    |
context-curator (manage context budget)
    |
ROUTE TO EXECUTION SKILL
    |
context-curator (compress and handoff)
    |
DONE
```

### Quick Classification Pipeline
```
complexity-router (classify and route)
    |
ROUTE TO EXECUTION SKILL
```

### Research-First Pipeline
```
archon-scout (gather evidence)
    |
complexity-router (classify based on findings)
    |
ROUTE TO EXECUTION SKILL
```

### Long Session Management
```
context-curator (monitor budget)
    |
IF pressure high -> compress + summarize
    |
CONTINUE EXECUTION
```

---

## Decision Tree

```
What orchestration concern are you addressing?

+-- NEED TO CLASSIFY OR ROUTE A TASK?
|   -> complexity-router
|
+-- CONTEXT WINDOW UNDER PRESSURE?
|   -> context-curator
|
+-- NEED EVIDENCE BEFORE BUILDING?
|   -> archon-scout
|
+-- STARTING A MULTI-PHASE WORKFLOW?
    -> complexity-router THEN context-curator
```

---

## State-Based Routing

| Current State | Next Action | Routed To |
|---------------|-------------|-----------|
| **New Task Received** | Classify complexity | complexity-router |
| **Complexity Known** | Research if uncertain | archon-scout |
| **Research Complete** | Manage context for execution | context-curator |
| **Context Pressure High** | Compress and evict | context-curator |
| **Phase Transition** | Build handoff summary | context-curator |
| **Conflicting Information** | Resolve with evidence | archon-scout |
| **Agent Selection Needed** | Route to optimal agent | complexity-router |

---

## Skill Priority Matrix

| Task Category | Primary | Secondary | Tertiary |
|--------------|---------|-----------|----------|
| **Task Classification** | complexity-router | - | - |
| **Context Management** | context-curator | - | - |
| **Research** | archon-scout | context-curator | - |
| **Multi-Agent Routing** | complexity-router | context-curator | archon-scout |
| **Phase Transition** | context-curator | complexity-router | - |
| **Feasibility Check** | archon-scout | complexity-router | - |

---

## Quality Gates

### Gate 1: Classification Accuracy
- **Checked by:** complexity-router
- **Criteria:** Task tier correctly identified, agent/model selection justified, effort scaling appropriate
- **Pass -> Route to execution**

### Gate 2: Context Budget
- **Checked by:** context-curator
- **Criteria:** Token usage within budget, critical context preserved, non-essential content compressed
- **Pass -> Continue execution**

### Gate 3: Evidence Validity
- **Checked by:** archon-scout
- **Criteria:** Sources cited, conflicts resolved, claims validated, no unsupported assumptions
- **Pass -> Proceed with confidence**

---

## Input/Output Contracts

### complexity-router
- **Input:** Task description, available agents, constraints
- **Output:** Complexity tier, agent routing, model recommendation, execution strategy

### context-curator
- **Input:** Current context state, token budget, phase metadata
- **Output:** Compressed context, handoff summary, budget report

### archon-scout
- **Input:** Research question, domain constraints, existing knowledge
- **Output:** Evidence report with citations, conflict resolution, feasibility assessment

---

## Notes for AI Assistants

- **Always classify first** before executing complex tasks
- **Monitor context budget** throughout long sessions -- do not wait for overflow
- **Research before building** when the approach is uncertain
- **Complexity tiers drive everything** -- TRIVIAL tasks skip orchestration, EXPERT tasks get full pipeline
- **Context compression is lossy** -- preserve critical decisions and constraints
- **Consult each SKILL.md** before applying skill knowledge
- **This is the control plane** -- other bundles are the execution plane
