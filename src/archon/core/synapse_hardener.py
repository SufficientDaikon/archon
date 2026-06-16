"""
Phase 7: Hardening — Circuit Breaker + Retry Logic for Archon Synapses

Prevents cascading failures when synapses malfunction.
Architecture:
  - CircuitBreaker: Open circuit after N consecutive failures
  - RetryPolicy: Exponential backoff for transient errors
  - GracefulDegrader: Fallback decisions when synapse is unavailable
"""

from __future__ import annotations
import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


# ── Circuit Breaker ──────────────────────────────────────────────────────────

class CircuitState(str, Enum):
    CLOSED    = "closed"     # Normal operation
    OPEN      = "open"       # Failure threshold exceeded, blocking calls
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int   = 3     # Trips after N consecutive failures
    recovery_timeout:  float = 30.0  # Seconds before entering HALF_OPEN
    success_threshold: int   = 2     # Successes needed to close from HALF_OPEN


class CircuitBreaker:
    """
    Per-synapse circuit breaker.

    State machine:
        CLOSED -> OPEN on failure_threshold consecutive failures
        OPEN   -> HALF_OPEN after recovery_timeout seconds
        HALF_OPEN -> CLOSED on success_threshold consecutive successes
        HALF_OPEN -> OPEN on any failure
    """

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.cfg = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self._failures = 0
        self._successes = 0
        self._tripped_at: Optional[float] = None

    def is_open(self) -> bool:
        if self.state == CircuitState.OPEN:
            if time.monotonic() - (self._tripped_at or 0) >= self.cfg.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self._successes = 0
                logger.info(f"Circuit {self.name}: OPEN -> HALF_OPEN")
                return False
            return True
        return False

    def record_success(self) -> None:
        self._failures = 0
        if self.state == CircuitState.HALF_OPEN:
            self._successes += 1
            if self._successes >= self.cfg.success_threshold:
                self.state = CircuitState.CLOSED
                logger.info(f"Circuit {self.name}: HALF_OPEN -> CLOSED")
        elif self.state == CircuitState.CLOSED:
            pass  # Normal path

    def record_failure(self) -> None:
        self._failures += 1
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self._tripped_at = time.monotonic()
            logger.warning(f"Circuit {self.name}: HALF_OPEN -> OPEN (recovery failed)")
        elif self._failures >= self.cfg.failure_threshold:
            self.state = CircuitState.OPEN
            self._tripped_at = time.monotonic()
            logger.warning(f"Circuit {self.name}: CLOSED -> OPEN (failures={self._failures})")

    def status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "failures": self._failures,
            "successes": self._successes,
        }


# ── Retry Policy ─────────────────────────────────────────────────────────────

@dataclass
class RetryPolicy:
    max_retries:  int   = 2
    base_delay:   float = 0.1   # seconds
    max_delay:    float = 2.0   # cap on exponential backoff
    backoff_factor: float = 2.0


class RetryError(Exception):
    """Raised when all retries are exhausted."""
    def __init__(self, synapse_id: str, attempts: int, last_error: Exception):
        super().__init__(f"Synapse {synapse_id} failed after {attempts} attempts: {last_error}")
        self.synapse_id = synapse_id
        self.attempts = attempts
        self.last_error = last_error


# ── Graceful Degrader ────────────────────────────────────────────────────────

class GracefulDegrader:
    """
    Produces fallback SynapseDecisions when a synapse is unavailable.

    Strategy:
    - WARN by default (don't block execution when validator is down)
    - Log event for audit trail
    - Record skip for health dashboard
    """

    def __init__(self):
        self._skip_counts: Dict[str, int] = {}

    def fallback(self, synapse_id: str, trigger: str, reason: str) -> Dict[str, Any]:
        self._skip_counts[synapse_id] = self._skip_counts.get(synapse_id, 0) + 1
        logger.warning(f"Synapse {synapse_id} unavailable on {trigger}: {reason}")
        return {
            "action": "warn",
            "message": f"Synapse {synapse_id} unavailable (circuit open): {reason}",
            "degraded": True,
            "synapse_id": synapse_id,
        }

    def skip_counts(self) -> Dict[str, int]:
        return dict(self._skip_counts)


# ── Composite Hardening Context ──────────────────────────────────────────────

class SynapseHardener:
    """
    Combines circuit breaker, retry, and graceful degradation
    for a single synapse.
    """

    def __init__(
        self,
        synapse_id: str,
        circuit_config: Optional[CircuitBreakerConfig] = None,
        retry_policy: Optional[RetryPolicy] = None,
    ):
        self.synapse_id = synapse_id
        self.circuit = CircuitBreaker(synapse_id, circuit_config)
        self.retry = retry_policy or RetryPolicy()
        self.degrader = GracefulDegrader()

    def execute(self, validator: Callable, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validator with circuit breaker + retry protection."""
        # Circuit open -> fallback immediately
        if self.circuit.is_open():
            return self.degrader.fallback(
                self.synapse_id, "unknown", "circuit open"
            )

        delay = self.retry.base_delay
        last_err: Optional[Exception] = None

        for attempt in range(self.retry.max_retries + 1):
            try:
                result = validator(context)
                self.circuit.record_success()
                return result
            except Exception as exc:
                last_err = exc
                self.circuit.record_failure()
                logger.error(
                    f"Synapse {self.synapse_id} attempt {attempt + 1} failed: {exc}"
                )
                if attempt < self.retry.max_retries:
                    time.sleep(min(delay, self.retry.max_delay))
                    delay *= self.retry.backoff_factor

        # All retries exhausted -> graceful degrade
        return self.degrader.fallback(
            self.synapse_id, "unknown", str(last_err)
        )

    def status(self) -> Dict[str, Any]:
        return {
            "synapse_id": self.synapse_id,
            "circuit": self.circuit.status(),
            "skip_counts": self.degrader.skip_counts(),
        }
