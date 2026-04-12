# Probe Vectors — Quick Reference

Quick-scan checklist for each PV. Use the full SKILL.md for detailed signals.

## PV-VISION: Vision Alignment
- [ ] Does this component improve agent behavior measurably?
- [ ] Would baseline Claude (no Archon) handle this fine alone?
- [ ] Is there a model-floor tag?
- [ ] Is the token cost justified by the quality gain?

## PV-HOOK: Hook Architecture
- [ ] Latency within budget? (SessionStart <5s, others <2s)
- [ ] No archon core imports? (shared/ only)
- [ ] No LLM calls? (pure heuristic/regex)
- [ ] Output matches Claude Code schema?
- [ ] Graceful degradation on error?
- [ ] Atomic state writes?

## PV-SYNAPSE: Synapse Effectiveness
- [ ] Instructions specific enough to be actionable?
- [ ] Fires at correct tier?
- [ ] No overlap with other synapses?
- [ ] Enforced by hooks, not just suggested?

## PV-CLASSIFY: Classification Accuracy
- [ ] 20+ real prompts tested?
- [ ] No over-escalation (everything → COMPLEX)?
- [ ] No under-escalation (real complexity missed)?
- [ ] Skill matching returns relevant results?

## PV-STATE: State Management
- [ ] Bounded growth?
- [ ] No stale data in new sessions?
- [ ] No race conditions?
- [ ] Schema migration path?

## PV-GUARD: Guardrail Precision
- [ ] Low false positive rate on common operations?
- [ ] No missed dangerous patterns?
- [ ] Allowlists cover test/example files?

## PV-PERF: Token Economy
- [ ] additionalContext is compressed?
- [ ] No redundant injection across hooks?
- [ ] Boot time <2s cold?

## PV-EVOLVE: Evolution Readiness
- [ ] Can be stripped when model improves?
- [ ] Components are independently evolvable?
- [ ] Extension points exist?

## PV-COHERENCE: Framework Coherence
- [ ] archon.yaml matches file tree?
- [ ] Naming is consistent?
- [ ] Hooks and virtuoso.xml don't contradict?
