from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_ENABLED_LAYERS = (
    "newswiki_hosted",
    "newswiki_curated",
    "recommended_template",
)


@dataclass(frozen=True)
class LayerConfig:
    enabled: tuple[str, ...] = DEFAULT_ENABLED_LAYERS

    @classmethod
    def from_env(cls) -> "LayerConfig":
        raw = os.environ.get("NEWSWIKI_ENABLED_LAYERS")
        if not raw:
            return cls()
        return cls(tuple(layer.strip() for layer in raw.split(",") if layer.strip()))

    def allows(self, source_type: str) -> bool:
        return source_type in self.enabled


@dataclass(frozen=True)
class Settings:
    public_export_dir: Path
    api_keys: tuple[str, ...]
    layers: LayerConfig = LayerConfig()
    user_memory_dir: Path | None = None
    local_capability_dir: Path | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        root = Path(__file__).resolve().parents[2]
        default_dir = root / "examples" / "public"
        raw_keys = os.environ.get("NEWSWIKI_API_KEYS", "dev-newswiki-key")
        api_keys = tuple(key.strip() for key in raw_keys.split(",") if key.strip())
        user_memory_dir = optional_path("NEWSWIKI_USER_MEMORY_DIR")
        local_capability_dir = optional_path("NEWSWIKI_LOCAL_CAPABILITY_DIR")
        return cls(
            public_export_dir=Path(os.environ.get("NEWSWIKI_PUBLIC_EXPORT_DIR", default_dir)),
            api_keys=api_keys,
            layers=LayerConfig.from_env(),
            user_memory_dir=user_memory_dir,
            local_capability_dir=local_capability_dir,
        )


def optional_path(env_name: str) -> Path | None:
    value = os.environ.get(env_name)
    if not value:
        return None
    return Path(value)
