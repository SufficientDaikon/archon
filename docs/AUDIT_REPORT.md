# ARCHON SYNAPSE ENGINE — ADVERSARIAL CODE AUDIT

**Reviewer:** Hostile Maintainer (Treating as Codex-written code)  
**Target:** synapse_engine.py + policy_engine integration  
**Date:** 2026-04-20  
**Verdict:** BLOCKER issues found. NOT PRODUCTION READY.

---

## STRIKE PROTOCOL FINDINGS

### S — SAFETY (Thread Safety)

#### [BLOCKER] S-001: Race Condition on SynapseEngine.firing_log
- Issue: Plain list appended to without synchronization
- Impact: Multi-threaded agents will corrupt audit log
- Fix: Use threading.RLock() for all mutable state

#### [BLOCKER] S-002: Race Condition on Synapse.firing_log  
- Same as S-001 but at synapse level
- Fix: Add lock to Synapse class

#### [MAJOR] S-003: Dict mutation race on synapses
- register_synapse() writes, fire_trigger() reads, no synchronization
- Fix: Protect dict access with same lock

---

### T — TYPES (API Design)

#### [MAJOR] T-001: Type Mismatch on validator
- validators typed as Callable but code shows async def
- In policy_engine: async validators are SILENTLY SKIPPED
- Fix: Use Union[Callable, Awaitable] or make consistent

#### [MAJOR] T-002: Silent overwrites on register_synapse()
- Calling register_synapse twice with same name silently loses first one
- No error, no warning
- Fix: Raise ValueError if synapse already registered

#### [MAJOR] T-003: No validation of trigger names  
- trigger is plain string, accepts invalid trigger names
- Hooks registered with bad triggers will never fire
- Fix: Use SynapseTrigger enum with validation

---

### R — RESOURCES (Cleanup)

#### [MINOR] R-001: No cleanup API
- SynapseEngine has no cleanup mechanism
- If validators hold resources (files, connections), never closed
- Fix: Add __enter__/__exit__ context manager

---

### I — INVARIANTS (Behavior)

#### [MAJOR] I-001: Confusing is_blocking semantics  
- is_blocking only checks for HALT, not WARN
- But WARN also stops execution (right?)
- Documentation unclear
- Fix: Clarify or rename property

---

### K — KOVER (Test Coverage)

#### [MAJOR] K-001: No concurrency tests
- No test for concurrent register_synapse() or fire_trigger()
- Race conditions won't be caught
- Fix: Add ThreadPool stress test

#### [MAJOR] K-002: No test for async validators in sync context
- Validators are async but policy_engine is sync
- This integration is completely untested
- Fix: Test that PolicyEngine calls synapses correctly

---

### E — EFFICIENCY

#### [MINOR] E-001: Redundant list comprehension every call
- anti_rationalization rebuilds violations list every invocation
- IRON_LAWS is constant but never cached
- Fix: Pre-compute as frozenset

#### [MINOR] E-002: Regex compiled on every call
- security_awareness_validator compiles regexes 3x per call
- Fix: Use module-level compiled patterns

---

### 7 — ERROR HANDLING

#### [BLOCKER] 7-001: Silent exception swallowing
- policy_engine._fire_synapses() catches Exception and silently passes
- If a security synapse crashes, code goes through unchecked
- Fix: Log and return HALT when validator fails

#### [MAJOR] 7-002: Return type mismatch
- synapse_engine expects SynapseDecision but modules return dict
- Integration is broken
- Fix: Pick one approach and stick to it

#### [MAJOR] 7-003: No validation of callable
- SynapseHook accepts non-callable validators
- Error doesn't surface until fire-time
- Fix: Check callable(validator) in __init__

---

### 8 — DOCUMENTATION

#### [MAJOR] 8-001: Threading model not documented
- Code is NOT thread-safe but this isn't stated anywhere
- Callers don't know to add locks
- Fix: Bold warning in module docstring

#### [MINOR] 8-002: Incomplete docstrings
- firing_count tracked but never documented (for monitoring?)
- context_snapshot optional but when to use?
- register_synapse() doesn't warn about overwrites
- Fix: Add comprehensive docstrings

---

### 9 — EDGE CASES

#### [MAJOR] 9-001: Null context not handled
- Validators assume context is dict with .get()
- If context=None passed, will crash
- Fix: Validate context upfront

#### [MAJOR] 9-002: Empty code string in security validator
- If code="" passed, returns ALLOW with no vulns (correct but implicit)
- Fix: Make explicit and test boundary

---

### 10 — BLAST RADIUS (Integration)

#### [BLOCKER] 10-001: BROKEN integration with PolicyEngine
- synapse_engine defines async validators
- policy_engine calls them synchronously
- Line checking hasattr(result, '__await__'), then SKIPS THEM
- Result: Synapses NEVER FIRE in policy context
- This defeats the entire purpose of synapses
- Fix: Make _fire_synapses() async OR convert validators to sync

#### [MAJOR] 10-002: No integration tests
- No test validates that synapses actually block policy decisions
- The main use case is completely untested
- Fix: Add end-to-end test

---

## SUMMARY

**BLOCKER (Ship Stoppers):** 4
- S-001, S-002: Thread-safety races
- 7-001: Silent exception swallowing  
- 10-001: Broken PolicyEngine integration

**MAJOR (Should Fix):** 9
- T-001, T-002, T-003, I-001, K-001, K-002, 7-002, 7-003, 9-001, 9-002

**MINOR (Nice-to-Have):** 4
- R-001, E-001, E-002, 8-001, 8-002, K-003

**Total: 17 issues found**

---

## VERDICT

**NOT PRODUCTION READY**

This code has:
1. Critical thread-safety bugs (BLOCKER)
2. Broken async/sync integration (BLOCKER)
3. Silent error swallowing (BLOCKER)
4. Zero integration tests

Before deployment:
- Fix all 4 BLOCKER issues (2-3 days)
- Add integration test suite
- Add concurrency stress tests
- Document threading model aggressively

**Grade: C+** (Good foundation, serious flaws)
