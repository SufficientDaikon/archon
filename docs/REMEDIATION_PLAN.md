# Archon Synapse Engine — Remediation Plan

## BLOCKER Issues & Fixes

### BLOCKER 1: Thread-Safety Races (S-001, S-002, S-003)

**Status:** FIXED in proposed synapse_engine_fixed.py

**Changes:**
```python
import threading

class SynapseEngine:
    def __init__(self):
        self.synapses: dict[str, Synapse] = {}
        self.firing_log: list[SynapseDecision] = []
        self._lock = threading.RLock()  # ADD THIS

    async def fire_trigger(self, trigger, context):
        with self._lock:  # PROTECT ALL READS/WRITES
            for synapse in self.synapses.values():
                # ...

class Synapse:
    def __init__(self, name, synapse_type="core"):
        # ...
        self._lock = threading.RLock()  # ADD THIS
```

**Impact:** Audit log now thread-safe, dict mutations protected.

---

### BLOCKER 2: Silent Exception Swallowing (7-001)

**Status:** FIXED in proposed policy_engine_fixed.py

**Current (BAD):**
```python
try:
    result = hook.validator(context)
except Exception:
    pass  # SILENTLY SWALLOWS
```

**Fixed:**
```python
try:
    result = hook.validator(context)
except Exception as e:
    import logging
    logging.error(f"Synapse {synapse.name} failed: {e}")
    decisions.append({
        "action": "halt",  # HALT when validator fails
        "message": f"Hook execution failed: {str(e)}",
    })
    break
```

**Impact:** Validator failures now logged and halt execution.

---

### BLOCKER 3: Async/Sync Validator Mismatch (10-001)

**Status:** PARTIALLY FIXED

**Current (BROKEN):**
- synapse_engine defines `async def anti_rationalization_validator()`
- policy_engine calls it with `result = hook.validator(context)` (sync call)
- Code checks: `if hasattr(result, '__await__'): continue` → SKIPS ASYNC VALIDATORS

**Solution A (RECOMMENDED):** Make all validators support both sync/async

```python
class SynapseHook:
    def __init__(self, ..., validator, ...):
        self.is_async = hasattr(validator, "__call__") and asyncio.iscoroutinefunction(validator)

async def fire_trigger(self, trigger, context):
    result = hook.validator(context)
    if hasattr(result, "__await__"):
        result = await result
    # Now works for both
```

**Solution B (ALTERNATIVE):** Convert all validators to sync

```python
def anti_rationalization_validator(context):  # Removed async
    # Works synchronously
    return SynapseDecision(...)
```

**Impact:** Validators now fire reliably in both contexts.

---

### BLOCKER 4: Broken Integration (10-001 Integration Test)

**Status:** Test needed

**Test to add:**
```python
async def test_policy_engine_with_synapses_blocks():
    from archon.core.policy_engine import PolicyEngineWithSynapses
    from archon.core.synapse_engine import SynapseEngine, create_default_synapses
    
    engine = SynapseEngine()
    for synapse in create_default_synapses().values():
        engine.register_synapse(synapse)
    
    policy = PolicyEngineWithSynapses(rules=[], synapse_engine=engine)
    
    # This should HALT due to rationalization
    policy_dec, synapse_dec = policy.evaluate_with_synapses(
        tool_name="test",
        session_id="test",
        correlation_id="test",
        synapse_context={"reasoning": "this should work", "task": "test"},
    )
    
    assert policy_dec.action == "deny", "Policy should deny when synapse halts"
    assert len(synapse_dec) > 0, "Synapses should have fired"
```

---

## MAJOR Issues & Fixes

### MAJOR T-002: Silent Overwrites

**Fix:**
```python
def register_synapse(self, synapse):
    with self._lock:
        if synapse.name in self.synapses:
            raise ValueError(f"Synapse '{synapse.name}' already registered")
        self.synapses[synapse.name] = synapse
```

### MAJOR T-003: No Trigger Validation

**Fix:**
```python
class SynapseTrigger(str, Enum):
    PRE_EXECUTION = "pre-execution"
    MID_EXECUTION = "mid-execution"
    POST_BUILD = "post-build"

class SynapseHook:
    def __init__(self, ..., trigger: SynapseTrigger, ...):
        if not isinstance(trigger, SynapseTrigger):
            raise ValueError(f"Invalid trigger: {trigger}")
```

### MAJOR 7-003: No Validator Validation

**Fix:**
```python
class SynapseHook:
    def __init__(self, ..., validator, ...):
        if not callable(validator):
            raise TypeError(f"validator must be callable, got {type(validator)}")
```

### MAJOR 9-001: Null Context Not Handled

**Fix:**
```python
async def anti_rationalization_validator(context):
    if not context or not isinstance(context, dict):
        return SynapseDecision(
            action=SynapseAction.ALLOW,
            message="No context provided",
        )
    # ... proceed normally ...
```

---

## MINOR Issues & Fixes

### MINOR E-001/E-002: Performance

**Pre-compile patterns and IRON_LAWS:**
```python
EXEC_EVAL_PATTERN = re.compile(r"exec\(|eval\(")
INNERHTML_PATTERN = re.compile(r"innerHTML\s*=")
PASSWORD_PATTERN = re.compile(r"password\s*=\s*['\"]", re.IGNORECASE)

async def security_awareness_validator(context):
    code = context.get("code", "")
    vulns = []
    if EXEC_EVAL_PATTERN.search(code):
        vulns.append("CRITICAL: exec/eval detected")
    # ...
```

### MINOR 8-001: Document Threading

**Add to module docstring:**
```python
"""
Archon Synapse Engine — Executable cognitive synapses.

THREADING MODEL: This engine is thread-safe. All mutable state is protected
with RLocks. Safe to call fire_trigger() from multiple threads simultaneously.

However, validators themselves are NOT assumed to be thread-safe. If a
validator holds shared state, protect it.
"""
```

---

## Implementation Schedule

**Phase 1 (Immediate - BLOCKER):**
- [ ] Add threading.RLock to SynapseEngine and Synapse
- [ ] Fix exception swallowing in policy_engine
- [ ] Resolve async/sync mismatch (pick Solution A or B)
- [ ] Add integration test

**Phase 2 (Short-term - MAJOR):**
- [ ] Add trigger enum validation
- [ ] Add synapse name uniqueness check
- [ ] Add validator callability check
- [ ] Add context type validation

**Phase 3 (Polish - MINOR):**
- [ ] Pre-compile regex patterns
- [ ] Add comprehensive docstrings
- [ ] Add metrics API
- [ ] Add cleanup context manager

---

## Verification Checklist

Before deployment:

- [ ] All BLOCKER tests pass
- [ ] Concurrency stress test passes (100+ concurrent fires)
- [ ] Integration test passes (synapse blocks policy)
- [ ] No exceptions swallowed (logging captures all)
- [ ] Type hints are correct
- [ ] Threading model documented
- [ ] Code review passed

---

## Timeline

- **Fix BLOCKER issues:** 2 hours
- **Fix MAJOR issues:** 4 hours  
- **Fix MINOR issues:** 3 hours
- **Testing & validation:** 2 hours
- **Code review:** 1 hour

**Total: ~12 hours work**

---

**Next Step:** Approve fixes and proceed with implementation.
