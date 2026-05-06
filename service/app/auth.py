from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status

from service.app.settings import Settings


def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    settings = Settings.from_env()
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing API key")
    for allowed in settings.api_keys:
        if secrets.compare_digest(x_api_key, allowed):
            return x_api_key
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid API key")
