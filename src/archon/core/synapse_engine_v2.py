# Synapse Engine v2 - Production Hardened
import threading
import asyncio
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)

class SynapseAction(str, Enum):
    ALLOW = 'allow'
    WARN = 'warn'
    HALT = 'halt'

class SynapseTrigger(str, Enum):
    PRE_EXECUTION = 'pre-execution'
    POST_BUILD = 'post-build'

@dataclass
class SynapseDecision:
    synapse_name: str
    hook_name: str
    action: SynapseAction
    message: str
    evidence: list = field(default_factory=list)
    
    @property
    def is_halt(self) -> bool:
        return self.action == SynapseAction.HALT

class SynapseHook:
    def __init__(self, name, trigger, validator, description=''):
        if not callable(validator):
            raise TypeError('validator must be callable')
        self.name = name
        self.trigger = trigger
        self.validator = validator
        self.is_async = asyncio.iscoroutinefunction(validator)
        self.firing_count = 0

class Synapse:
    def __init__(self, name, synapse_type='core'):
        self.name = name
        self.synapse_type = synapse_type
        self.hooks = {}
        self._lock = threading.RLock()
    
    def register_hook(self, hook):
        with self._lock:
            self.hooks[hook.trigger] = hook

class SynapseEngine:
    def __init__(self):
        self.synapses = {}
        self.firing_log = []
        self._lock = threading.RLock()
    
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
                    raise TypeError('Must return SynapseDecision')
                decisions.append(result)
                with self._lock:
                    self.firing_log.append(result)
                if result.is_halt:
                    break
            except Exception as e:
                logger.error(f"Synapse {synapse.name} failed: {e}", exc_info=True)
                halt = SynapseDecision(synapse.name, hook.name, SynapseAction.HALT, str(e))
                decisions.append(halt)
                break
        return decisions
    
    def get_blocking_decisions(self):
        with self._lock:
            return [d for d in self.firing_log if d.is_halt]
    
    def get_metrics(self):
        with self._lock:
            total = len(self.firing_log)
            blocks = len(self.get_blocking_decisions())
            return {"total": total, "blocks": blocks, "rate": blocks / max(1, total)}
