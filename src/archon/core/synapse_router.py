"""SynapseRouter - Auto-Selection Engine for Archon Synapses."""
from __future__ import annotations
import hashlib, time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

COMPLEXITY_ORDER = ["TRIVIAL", "SIMPLE", "MODERATE", "COMPLEX", "EXPERT"]

def _tier_rank(tier):
    try: return COMPLEXITY_ORDER.index(tier.upper())
    except ValueError: return 1

ROUTING_TABLE = {
    "pre-execution": {
        "TRIVIAL":  [],
        "SIMPLE":   ["anti-rationalization"],
        "MODERATE": ["anti-rationalization", "metacognition", "trust-verification"],
        "COMPLEX":  ["anti-rationalization", "metacognition", "trust-verification", "sequential-thinking"],
        "EXPERT":   ["anti-rationalization", "metacognition", "trust-verification", "sequential-thinking", "pattern-recognition"],
    },
    "post-build": {
        "TRIVIAL":  [],
        "SIMPLE":   ["security-awareness"],
        "MODERATE": ["security-awareness", "code-quality"],
        "COMPLEX":  ["security-awareness", "code-quality", "completeness"],
        "EXPERT":   ["security-awareness", "code-quality", "completeness", "consistency"],
    },
    "post-handoff": {
        "TRIVIAL":  [],
        "SIMPLE":   ["completeness"],
        "MODERATE": ["completeness", "consistency"],
        "COMPLEX":  ["completeness", "consistency", "trust-verification"],
        "EXPERT":   ["completeness", "consistency", "trust-verification", "pattern-recognition"],
    },
    "post-cycle": {
        "TRIVIAL":  [],
        "SIMPLE":   [],
        "MODERATE": ["pattern-recognition"],
        "COMPLEX":  ["pattern-recognition", "metacognition"],
        "EXPERT":   ["pattern-recognition", "metacognition", "sequential-thinking"],
    },
}

FILE_TYPE_SYNAPSES = {
    ".py":   ["security-awareness", "code-quality"],
    ".js":   ["security-awareness"],
    ".ts":   ["security-awareness", "code-quality"],
    ".jsx":  ["security-awareness"],
    ".tsx":  ["security-awareness"],
}


@dataclass
class CachedDecision:
    synapses: list
    timestamp: float
    hit_count: int = 0


class DecisionCache:
    def __init__(self, ttl=60.0, max_size=512):
        self._cache = {}
        self._ttl = ttl
        self._max_size = max_size

    def _key(self, trigger, complexity, file_ext):
        raw = f"{trigger}:{complexity}:{file_ext}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]

    def get(self, trigger, complexity, file_ext):
        key = self._key(trigger, complexity, file_ext)
        entry = self._cache.get(key)
        if entry and (time.monotonic() - entry.timestamp) < self._ttl:
            entry.hit_count += 1
            return entry.synapses
        if entry: del self._cache[key]
        return None

    def put(self, trigger, complexity, file_ext, synapses):
        if len(self._cache) >= self._max_size:
            oldest = min(self._cache, key=lambda k: self._cache[k].timestamp)
            del self._cache[oldest]
        key = self._key(trigger, complexity, file_ext)
        self._cache[key] = CachedDecision(synapses=synapses, timestamp=time.monotonic())

    def stats(self):
        return {"size": len(self._cache), "hits": sum(e.hit_count for e in self._cache.values())}


class AdaptiveThresholds:
    def __init__(self):
        self._violations = {}
        self._firings = {}

    def record_firing(self, synapse_id, was_halt):
        self._firings[synapse_id] = self._firings.get(synapse_id, 0) + 1
        if was_halt:
            self._violations[synapse_id] = self._violations.get(synapse_id, 0) + 1

    def violation_rate(self, synapse_id):
        return self._violations.get(synapse_id, 0) / max(1, self._firings.get(synapse_id, 0))

    def should_relax(self, synapse_id, noise=0.8):
        return self.violation_rate(synapse_id) > noise

    def should_tighten(self, synapse_id, blind=0.05):
        return self._firings.get(synapse_id, 0) > 20 and self.violation_rate(synapse_id) < blind

    def all_rates(self):
        return {sid: self.violation_rate(sid) for sid in self._firings}


class SynapseRouter:
    def __init__(self, cache_ttl=60.0):
        self._cache = DecisionCache(ttl=cache_ttl)
        self._adaptive = AdaptiveThresholds()

    def route(self, trigger, complexity="SIMPLE", file_path=None, context=None):
        file_ext = Path(file_path).suffix.lower() if file_path else ""
        tier = complexity.upper()
        cached = self._cache.get(trigger, tier, file_ext)
        if cached is not None:
            return cached
        synapses = self._compute(trigger, tier, file_ext)
        self._cache.put(trigger, tier, file_ext, synapses)
        return synapses

    def _compute(self, trigger, tier, file_ext):
        tier_rank = _tier_rank(tier)
        trigger_routes = ROUTING_TABLE.get(trigger, {})
        selected = []
        for t in COMPLEXITY_ORDER[:tier_rank + 1]:
            for s in trigger_routes.get(t, []):
                if s not in selected:
                    selected.append(s)
        if file_ext in FILE_TYPE_SYNAPSES:
            for s in FILE_TYPE_SYNAPSES[file_ext]:
                if s not in selected:
                    selected.append(s)
        return selected

    def record(self, synapse_id, was_halt):
        self._adaptive.record_firing(synapse_id, was_halt)

    def health(self):
        return {
            "cache": self._cache.stats(),
            "violation_rates": self._adaptive.all_rates(),
            "noisy_synapses": [s for s in self._adaptive._firings if self._adaptive.should_relax(s)],
            "silent_synapses": [s for s in self._adaptive._firings if self._adaptive.should_tighten(s)],
        }
