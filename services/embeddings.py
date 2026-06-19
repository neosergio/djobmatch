"""Embedding provider abstraction.

Embeddings are the CHEAP half of the system: they power the numeric match score via
cosine distance, with no LLM involved. Same pattern as `llm.py` — depend on the
`EmbeddingProvider` interface and `get_embedder()`, never on a concrete SDK.
"""

from __future__ import annotations

import abc

from django.conf import settings


class EmbeddingError(RuntimeError):
    """Raised when the embedding provider fails."""


class EmbeddingProvider(abc.ABC):
    @property
    @abc.abstractmethod
    def dimensions(self) -> int:
        """Vector length produced by this provider (must match the DB column)."""
        raise NotImplementedError

    @abc.abstractmethod
    def embed(self, text: str) -> list[float]:
        """Return the embedding vector for a single piece of text."""
        raise NotImplementedError


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Default concrete provider, backed by text-embedding-3-small."""

    def __init__(self, *, api_key: str | None = None, model: str | None = None) -> None:
        from openai import OpenAI

        self._model = model or settings.OPENAI_EMBEDDING_MODEL
        self._client = OpenAI(api_key=api_key or settings.OPENAI_API_KEY)

    @property
    def dimensions(self) -> int:
        return settings.EMBEDDING_DIM

    def embed(self, text: str) -> list[float]:
        try:
            response = self._client.embeddings.create(model=self._model, input=text)
        except Exception as exc:
            raise EmbeddingError(f"OpenAI embedding request failed: {exc}") from exc
        return response.data[0].embedding


def get_embedder() -> EmbeddingProvider:
    """Factory: returns the configured embedding provider."""
    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider == "openai":
        return OpenAIEmbeddingProvider()
    # Plug in VoyageEmbeddingProvider here when needed.
    raise EmbeddingError(f"Unknown EMBEDDING_PROVIDER: {settings.EMBEDDING_PROVIDER!r}")
