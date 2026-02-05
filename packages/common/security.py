from __future__ import annotations

import hashlib


def token_fingerprint(token: str) -> str:
    token = (token or "").strip()
    if not token:
        return ""
    return hashlib.sha256(token.encode()).hexdigest()


def is_token_match(token: str, fingerprint: str) -> bool:
    if not fingerprint:
        return False
    return token_fingerprint(token) == fingerprint
