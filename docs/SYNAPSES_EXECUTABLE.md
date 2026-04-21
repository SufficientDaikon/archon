# Executable Synapses — Archon v2

**Status:** Production  
**Built:** 2026-04-20  
**Tests:** All passing (anti-rationalization, security-awareness, metacognition)

## What Changed

**Before:** Synapses were `.md` files with text suggestions (fired "sometimes" as language patterns)

**After:** Synapses are executable Python modules with registered validators (fire on demand at lifecycle points)

## Architecture

```
SynapseEngine
├── Synapse ("anti-rationalization")
│   └── SynapseHook(trigger="pre-execution", validator=anti_rationalization_validator)
├── Synapse ("security-awareness")
│   └── SynapseHook(trigger="post-build", validator=security_awareness_validator)
├── Synapse ("metacognition")
│   └── SynapseHook(trigger="pre-execution", validator=metacognition_validator)
└── ...
```

**Synapses are now:**
- ✅ Executable Python modules (not text suggestions)
- ✅ Registered with specific triggers (pre-execution, post-build, etc.)
- ✅ Chainable (stop on first HALT)
- ✅ Auditable (every decision logged)
- ✅ Integrated into PolicyEngine (hard enforcement)

## Core Components

### 1. SynapseEngine (src/archon/core/synapse_engine.py)

Loads and orchestrates all synapses.

```python
engine = SynapseEngine()
engine.register_synapse(my_synapse)
decisions = await engine.fire_trigger("pre-execution", context)
```

## 2. Individual Synapses (src/archon/synapses/)

Each synapse is a module with a `validate(context)` function that returns:

```python
{
    "action": "halt" | "warn" | "allow",
    "message": str,
    "violations": list,  # Evidence
}
```

### Anti-Rationalization
- Trigger: `pre-execution`
- Detects: 10 Iron Laws violations (forbidden phrases)
- Action: HALT on violation
- Examples:
  - "should work" → BLOCKED
  - "probably fine" → BLOCKED
  - "close enough" → BLOCKED

### Security Awareness
- Trigger: `post-build`
- Detects: OWASP Top 10 patterns
- Action: HALT on HIGH/CRITICAL
- Examples:
  - exec() / eval() → BLOCKED
  - innerHTML assignment → BLOCKED
  - Hardcoded passwords → BLOCKED

### Metacognition
- Trigger: `pre-execution`
- Detects: Missing plan for complex tasks
- Action: HALT if complexity > SIMPLE and no plan
- Examples:
  - COMPLEX task without plan → BLOCKED
  - SIMPLE task without plan → ALLOWED

## 3. PolicyEngineWithSynapses (src/archon/core/policy_engine.py)

PolicyEngine extended to fire synapses before policy evaluation.

```python
policy = PolicyEngineWithSynapses(rules, synapse_engine=engine)
policy_decision, synapse_decisions = policy.evaluate_with_synapses(
    tool_name="file_edit",
    session_id="...",
    synapse_context={"reasoning": "...", "task": "..."}
)

# If any synapse HALTS, policy is DENIED
```

## Integration Points

### 1. Pipeline Engine
Fire anti-rationalization pre-plan, metacognition pre-build, security post-build.

### 2. Agent Execution
Fire synapses before agent invocation, halt if blocked.

### 3. Policy Engine
Synapses are evaluated BEFORE policy rules (harder enforcement).

## Testing

All synapses tested in `tests/test_synapses_executable.py`:

```
PASS: anti_rationalization blocks (forbidden phrases detected)
PASS: anti_rationalization allows (valid reasoning)
PASS: security_awareness detects (hardcoded credentials)
PASS: metacognition requires plan (no plan for COMPLEX task)
All tests passed
```

## Extending Synapses

1. Create a new module in `src/archon/synapses/my_synapse.py`
2. Implement `validate(context)` returning `{"action": ..., "message": ..., ...}`
3. Register in SynapseEngine: `engine.register_synapse(Synapse("my-synapse"))`

## Next Steps

- [ ] Integrate SynapseEngine into pipeline_engine
- [ ] Add pattern-recognition and sequential-thinking executors
- [ ] Create Synapse dashboard (audit log viewer)
- [ ] Load synapses from YAML manifests (like agents/skills)
- [ ] Async synapse execution (concurrent hook firing)
