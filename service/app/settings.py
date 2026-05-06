from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    public_export_dir: Path
    api_keys: tuple[str, ...]

    @classmethod
    def from_env(cls) -> "Settings":
        root = Path(__file__).resolve().parents[2]
        default_dir = root / "examples" / "public"
        raw_keys = os.environ.get("NEWSWIKI_API_KEYS", "dev-newswiki-key")
        api_keys = tuple(key.strip() for key in raw_keys.split(",") if key.strip())
        return cls(
            public_export_dir=Path(os.environ.get("NEWSWIKI_PUBLIC_EXPORT_DIR", default_dir)),
            api_keys=api_keys,
        )
