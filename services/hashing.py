"""Small helpers for content-addressed caching of parsed text."""

from __future__ import annotations

import hashlib


def normalize(text: str) -> str:
    """Collapse whitespace so trivially different inputs cache to the same row."""
    return " ".join(text.split())


def content_hash(text: str) -> str:
    """SHA-256 of the normalized text — the cache key for a parsed Job/Resume."""
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()
