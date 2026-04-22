from __future__ import annotations
import re
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from typing import Any, Callable, Optional


class SynapseAction(str, Enum):
    """Actions a synapse can return."""
    ALLOW = "allow"
    WARN = "warn"
    HALT = "halt"


@dataclass
class SynapseDecision:
    """Decision artifact from synapse evaluation."""
    synapse_name: str
    hook_name: str
    action: SynapseAction
    message: str
    evidence: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    context_snapshot: dict[str, Any] = field(default_factory=dict)

    @property
    def is_blocking(self) -> bool:
        return self.action == SynapseAction.HALT


class SynapseHook:
    """Single trigger point with validator."""
    def __init__(self, name: str, trigger: str, validator: Callable, description: str = ""):
        self.name = name
        self.trigger = trigger
        self.validator = validator
        self.description = description
        self.firing_count = 0


class Synapse:
    """Executable cognitive layer."""
    def __init__(self, name: str, synapse_type: str = "core"):
        self.name = name
        self.synapse_type = synapse_type
        self.hooks: dict[str, SynapseHook] = {}
        self.firing_log: list[SynapseDecision] = []
        self.enabled = True

    def register_hook(self, hook: SynapseHook) -> None:
        self.hooks[hook.trigger] = hook


class SynapseEngine:
    """Orchestrates all synapses."""
    def __init__(self):
        self.synapses: dict[str, Synapse] = {}
        self.firing_log: list[SynapseDecision] = []
        self.enabled = True

    def register_synapse(self, synapse: Synapse) -> None:
        self.synapses[synapse.name] = synapse

    def get_blocking_decisions(self) -> list[SynapseDecision]:
        return [d for d in self.firing_log if d.action == SynapseAction.HALT]


# Built-in Iron Laws
IRON_LAWS = [
    ("should", "Replace with: 'I verified this by [METHOD]'"),
    ("probably", "Remove or provide evidence"),
    ("close enough", "Exact or not done"),
    ("simple enough to skip", "Complexity doesn't excuse steps"),
    ("just a", "Size doesn't predict impact"),
    ("will add later", "Technical debt — do now"),
]


async def anti_rationalization_validator(context: dict[str, Any]) -> SynapseDecision:
    """Detect forbidden phrases in reasoning."""
    text = (context.get("reasoning", "") + " " + context.get("task", "")).lower()
    violations = [rule for phrase, rule in IRON_LAWS if phrase in text]
    
    if violations:
        return SynapseDecision(
            synapse_name="anti-rationalization",
            hook_name="detect-forbidden-phrases",
            action=SynapseAction.HALT,
            message=f"Rationalization detected: {len(violations)} Iron Law violation(s)",
            evidence=violations,
        )
    return SynapseDecision(
        synapse_name="anti-rationalization",
        hook_name="detect-forbidden-phrases",
        action=SynapseAction.ALLOW,
        message="No rationalization detected",
        evidence=[],
    )


async def security_awareness_validator(context: dict[str, Any]) -> SynapseDecision:
    """Scan code for OWASP vulnerabilities."""
    code = context.get("code", "")
    vulns = []
    
    if re.search(r"exec\(|eval\(", code):
        vulns.append("CRITICAL: exec/eval detected")
    if re.search(r"innerHTML\s*=", code):
        vulns.append("HIGH: innerHTML assignment (XSS)")
    if re.search(r"password\s*=\s*['\"]", code, re.IGNORECASE):
        vulns.append("CRITICAL: Hardcoded password")
    
    if vulns:
        return SynapseDecision(
            synapse_name="security-awareness",
            hook_name="scan-owasp",
            action=SynapseAction.HALT,
            message=f"Security vulnerabilities: {len(vulns)}",
            evidence=vulns,
        )
    return SynapseDecision(
        synapse_name="security-awareness",
        hook_name="scan-owasp",
        action=SynapseAction.ALLOW,
        message="No vulnerabilities detected",
        evidence=[],
    )


def create_default_synapses() -> dict[str, Synapse]:
    """Create the 5 default synapses."""
    synapses = {}
    
    # Anti-Rationalization
    ar = Synapse("anti-rationalization", synapse_type="core")
    ar.register_hook(SynapseHook(
        name="detect-forbidden-phrases",
        trigger="pre-execution",
        validator=anti_rationalization_validator,
        description="Detect rationalization patterns",
    ))
    synapses["anti-rationalization"] = ar
    
    # Security Awareness
    sec = Synapse("security-awareness", synapse_type="core")
    sec.register_hook(SynapseHook(
        name="scan-owasp",
        trigger="post-build",
        validator=security_awareness_validator,
        description="Scan for OWASP Top 10",
    ))
    synapses["security-awareness"] = sec
    
    return synapses


import threading
import asyncio
import logging
logger = logging.getLogger(__name__)


class SynapseTrigger(str, Enum):
    PRE_EXECUTION = 'pre-execution'
    POST_BUILD = 'post-build'
    POST_HANDOFF = 'post-handoff'
    POST_CYCLE = 'post-cycle'


class SynapseEngineV2(SynapseEngine):
    """Production-hardened SynapseEngine with thread-safety, metrics, and async support."""

    def __init__(self):
        super().__init__()
        self._lock = threading.RLock()
        self._metrics = {
            'total': 0,
            'blocks': 0,
            'by_synapse': {},
            'by_trigger': {},
        }

    def register_synapse(self, synapse):
        with self._lock:
            if synapse.name in self.synapses:
                raise ValueError(f"Synapse '{synapse.name}' already registered")
            self.synapses[synapse.name] = synapse

    async def fire_trigger(self, trigger, context):
        if not context or not isinstance(context, dict):
            return []
        decisions = []
        with self._lock:
            synapses_copy = list(self.synapses.values())
        for synapse in synapses_copy:
            hook = synapse.hooks.get(trigger)
            if not hook:
                continue
            try:
                hook.firing_count += 1
                result = hook.validator(context)
                if asyncio.iscoroutine(result):
                    result = await result
                if not isinstance(result, SynapseDecision):
                    raise TypeError(f"{synapse.name} validator must return SynapseDecision")
                decisions.append(result)
                with self._lock:
                    self.firing_log.append(result)
                    self._metrics['total'] += 1
                    self._metrics['by_synapse'][synapse.name] = (
                        self._metrics['by_synapse'].get(synapse.name, 0) + 1
                    )
                    self._metrics['by_trigger'][trigger] = (
                        self._metrics['by_trigger'].get(trigger, 0) + 1
                    )
                    if result.is_blocking:
                        self._metrics['blocks'] += 1
                if result.is_blocking:
                    break
            except Exception as e:
                logger.error(f"Synapse {synapse.name} failed: {e}", exc_info=True)
                halt = SynapseDecision(
                    synapse_name=synapse.name,
                    hook_name=getattr(hook, 'name', 'unknown'),
                    action=SynapseAction.HALT,
                    message=str(e),
                )
                decisions.append(halt)
                break
        return decisions

    def get_metrics(self):
        with self._lock:
            total = self._metrics['total']
            blocks = self._metrics['blocks']
            return {
                'total': total,
                'blocks': blocks,
                'rate': blocks / max(1, total),
                'by_synapse': dict(self._metrics['by_synapse']),
                'by_trigger': dict(self._metrics['by_trigger']),
            }


class SynapseEngineWithRouter(SynapseEngineV2):
    """SynapseEngineV2 extended with auto-selection via SynapseRouter."""

    def __init__(self, router=None):
        super().__init__()
        from archon.core.synapse_router import SynapseRouter
        self._router = router or SynapseRouter()

    async def fire_trigger_auto(self, trigger, context, complexity='SIMPLE', file_path=None):
        """Fire synapses auto-selected by the router based on complexity + file type."""
        selected_ids = self._router.route(
            trigger=trigger,
            complexity=complexity,
            file_path=file_path,
            context=context,
        )
        if not selected_ids:
            return []
        decisions = []
        with self._lock:
            synapses_to_fire = [self.synapses[sid] for sid in selected_ids if sid in self.synapses]
        for synapse in synapses_to_fire:
            hook = synapse.hooks.get(trigger)
            if not hook:
                continue
            try:
                hook.firing_count += 1
                result = hook.validator(context)
                if asyncio.iscoroutine(result):
                    result = await result
                if not isinstance(result, SynapseDecision):
                    raise TypeError(f"{synapse.name} must return SynapseDecision")
                decisions.append(result)
                with self._lock:
                    self.firing_log.append(result)
                    self._router.record(synapse.name, result.is_blocking)
                if result.is_blocking:
                    break
            except Exception as e:
                logger.error(f"Synapse {synapse.name} failed: {e}", exc_info=True)
                halt = SynapseDecision(synapse.name, getattr(hook, 'name', 'unknown'), SynapseAction.HALT, str(e))
                decisions.append(halt)
                break
        return decisions

    def router_health(self):
        """Return router health and adaptive stats."""
        return self._router.health()
