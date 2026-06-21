from __future__ import annotations

import os
from dataclasses import dataclass

import yaml

from .paths import PROVIDERS_YAML


@dataclass
class ProviderConfig:
    name: str
    base_url: str
    model: str
    api_key_env: str
    role: str

    @property
    def api_key(self) -> str:
        return os.environ.get(self.api_key_env, "")


@dataclass
class WakeelConfig:
    providers: dict[str, ProviderConfig]
    draft: ProviderConfig
    verify: ProviderConfig
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_from: str
    dev_skip_validation: bool
    port: int


def load_config() -> WakeelConfig:
    raw = yaml.safe_load(PROVIDERS_YAML.read_text(encoding="utf-8"))
    providers: dict[str, ProviderConfig] = {}
    for name, cfg in raw["providers"].items():
        providers[name] = ProviderConfig(
            name=name,
            base_url=cfg["base_url"],
            model=cfg["model"],
            api_key_env=cfg["api_key_env"],
            role=cfg["role"],
        )

    draft_name = os.environ.get("DRAFT_PROVIDER") or _find_by_role(providers, "draft")
    verify_name = os.environ.get("VERIFY_PROVIDER") or _find_by_role(providers, "verify")

    if draft_name not in providers:
        raise ValueError(f"DRAFT_PROVIDER '{draft_name}' not in providers.yaml")
    if verify_name not in providers:
        raise ValueError(f"VERIFY_PROVIDER '{verify_name}' not in providers.yaml")

    return WakeelConfig(
        providers=providers,
        draft=providers[draft_name],
        verify=providers[verify_name],
        twilio_account_sid=os.environ.get("TWILIO_ACCOUNT_SID", ""),
        twilio_auth_token=os.environ.get("TWILIO_AUTH_TOKEN", ""),
        twilio_from=os.environ.get("TWILIO_FROM", ""),
        dev_skip_validation=os.environ.get("DEV_SKIP_VALIDATION", "0") == "1",
        port=int(os.environ.get("PORT", "8000")),
    )


def _find_by_role(providers: dict[str, ProviderConfig], role: str) -> str:
    for name, cfg in providers.items():
        if cfg.role == role:
            return name
    raise ValueError(f"No provider with role='{role}' found in providers.yaml")
