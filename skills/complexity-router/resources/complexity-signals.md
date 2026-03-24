# Complexity Signal Detection Reference

This document defines the signals used to assess task complexity and their detection patterns.

## Signal 1: Token Count

**What it measures**: Input length as proxy for information density and scope.

| Range | Classification Bias | Notes |
|-------|-------------------|-------|
| 0-50 | Trivial | Short questions, simple commands |
| 51-200 | Simple | Single focused task with clear scope |
| 201-1000 | Moderate | Detailed requirements, context provided |
| 1001-3000 | Complex | Multi-faceted task, extensive context |
| 3000+ | Expert | Comprehensive specifications, deep analysis needed |

**Detection pattern**: Count input tokens (approximate with `len(text.split()) * 1.3`)

---

## Signal 2: Domain Specificity

**What it measures**: Specialized knowledge or expertise required.

### Indicators of HIGH specificity:
- Technical jargon (e.g., "implement Merkle tree with BLAKE3 hashing")
- Framework/library-specific terminology (e.g., "GDScript autoload singleton pattern")
- Domain-specific concepts (e.g., "double-entry bookkeeping", "OAuth2 PKCE flow")
- Precise technical constraints (e.g., "sub-100ms p99 latency", "WCAG 2.1 AA compliance")

### Indicators of LOW specificity:
- General knowledge questions (e.g., "how to sort a list")
- Common patterns (e.g., "create a login form")
- Well-documented concepts (e.g., "explain HTTP methods")

**Classification impact**: High specificity → upgrade one level (Simple → Moderate, Moderate → Complex)

---

## Signal 3: Multi-Step Reasoning

**What it measures**: Whether task requires sequential operations or synthesis across steps.

### Single-step tasks (bias toward Simple):
- Direct transformations: "format this code", "translate this text"
- Lookups: "what is the capital of X"
- Simple operations: "run this test", "check syntax"

### Multi-step tasks (bias toward Moderate/Complex):
- Conditional logic: "if X then Y, otherwise Z"
- Synthesis: "compare A and B, then recommend C"
- Sequential phases: "analyze → design → implement"
- Iteration: "try X, if that fails try Y"

**Detection patterns**:
- Presence of: "then", "after that", "followed by", "if/else", "compare and"
- Multiple verbs: "analyze, synthesize, and recommend"
- Explicit step numbering: "1) First... 2) Then... 3) Finally..."

**Classification impact**: 
- 2-3 steps → Moderate minimum
- 4-6 steps → Complex minimum
- 7+ steps or recursion → Expert minimum

---

## Signal 4: Ambiguity Level

**What it measures**: Clarity of requirements and how many unknowns exist.

### LOW ambiguity (no upgrade):
- Specific deliverable defined: "write a Python function that..."
- Clear acceptance criteria: "must pass these tests"
- Concrete examples provided: "like this example..."
- Explicit constraints: "use React hooks, TypeScript, no libraries"

### MEDIUM ambiguity (upgrade one level):
- Vague scope: "improve the performance"
- Implicit requirements: "make it production-ready"
- Multiple valid interpretations: "design a better UX"

### HIGH ambiguity (upgrade two levels):
- Open-ended: "build something for X"
- Conflicting constraints: "fast, cheap, and perfect"
- Undefined success criteria: "make it good"

**Detection patterns**:
- Vague adjectives without metrics: "better", "faster", "cleaner"
- Missing context: references undefined entities
- Questions instead of specs: "what should this do?"

---

## Signal 5: Resource Requirements

**What it measures**: External knowledge, tools, or data access needed.

### No external resources (no upgrade):
- Self-contained in request
- Common knowledge only
- No tool execution needed

### Moderate resources (upgrade to Moderate minimum):
- Single external source (docs, API, file)
- Standard tool usage (grep, file operations)
- Reference to existing codebase

### Heavy resources (upgrade to Complex minimum):
- Multiple knowledge sources
- Cross-referencing required
- External API calls needed
- Large codebase analysis
- Database queries

### Specialized resources (upgrade to Expert):
- Custom tool creation needed
- Multi-system integration
- Research from multiple domains
- Real-time data streams

**Detection patterns**:
- "search for", "find all", "analyze the codebase"
- "integrate with X", "connect to Y"
- "research", "investigate", "comprehensive analysis"

---

## Signal 6: Time Sensitivity vs. Quality

**What it measures**: Whether fast response or thorough analysis is more valuable.

### Time-sensitive (bias toward faster models):
- "quick", "briefly", "tldr"
- Interactive debugging sessions
- Follow-up clarifications
- Real-time assistance

### Quality-critical (bias toward premium models):
- "comprehensive", "thorough", "detailed"
- Production code
- Architecture decisions
- Security-sensitive
- Public-facing content

**Detection patterns**:
- Urgency indicators: "quick", "fast", "asap", "now"
- Quality indicators: "production", "comprehensive", "detailed", "enterprise-grade"
- Risk indicators: "security", "financial", "compliance", "legal"

---

## Combined Signal Scoring

Classify based on cumulative signal strength:

1. Start with token count base classification
2. Apply domain specificity modifier (+0 to +2 levels)
3. Apply multi-step modifier (+0 to +2 levels)
4. Apply ambiguity modifier (+0 to +2 levels)
5. Apply resource modifier (+0 to +2 levels)
6. Apply time/quality bias (faster or premium model within level)

**Final classification**: 
- Sum of modifiers 0-1 → Keep base
- Sum of modifiers 2-4 → Upgrade one level
- Sum of modifiers 5-7 → Upgrade two levels
- Sum of modifiers 8+ → Expert (cap)

---

## Cost Tier Reference

| Model Tier | Example Models | Relative Cost | Use For |
|------------|---------------|---------------|---------|
| Fast | Claude Haiku 4.5, GPT-5-mini, Gemini-Flash | 1x | Trivial, Simple |
| Standard | Claude Sonnet 4.6, GPT-5.1, Gemini-Pro | 10x | Moderate, Complex |
| Premium | Claude Opus 4.6, GPT-5.3, Gemini-Ultra | 30x | Complex, Expert |

**Cost optimization principle**: Use the fastest model that can reliably complete the task. Premium models should be reserved for tasks where their advanced reasoning genuinely adds value.
