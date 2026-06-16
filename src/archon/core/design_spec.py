"""DesignSpec — typed input validator for the Archon design agent.

Uses stdlib dataclasses only — no Pydantic dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


VALID_MODES = frozenset({"generate", "apply", "audit", "tokens", "adapt"})


@dataclass
class DesignSpec:
    """Validated input contract for design agent invocations."""

    component: str
    mode: str  # generate | apply | audit | tokens | adapt
    tokens: dict[str, Any] = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)
    target: str = ""  # CSS selector, file path, or component name to apply to
    theme: str = ""   # theme variant (light | dark | custom)

    def validate(self) -> list[str]:
        """Return a list of validation error strings. Empty = valid."""
        errors: list[str] = []
        if not self.component or not self.component.strip():
            errors.append("component is required and must be non-empty")
        if self.mode not in VALID_MODES:
            errors.append(
                f"invalid mode '{self.mode}' — must be one of: {', '.join(sorted(VALID_MODES))}"
            )
        if self.mode == "apply" and not self.target:
            errors.append("target is required when mode is 'apply'")
        if self.tokens and not isinstance(self.tokens, dict):
            errors.append("tokens must be a dict")
        if self.constraints and not isinstance(self.constraints, list):
            errors.append("constraints must be a list")
        return errors

    @property
    def is_valid(self) -> bool:
        return len(self.validate()) == 0


def load_design_spec(data: dict[str, Any]) -> tuple[DesignSpec, list[str]]:
    """Load a DesignSpec from a raw dict. Returns (spec, errors).

    Unknown keys in `data` are silently ignored.
    """
    known_fields = DesignSpec.__dataclass_fields__
    filtered = {k: v for k, v in data.items() if k in known_fields}
    spec = DesignSpec(**filtered)
    return spec, spec.validate()
