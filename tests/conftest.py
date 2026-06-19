"""Shared test fixtures.

The LLM and embedding providers are ALWAYS mocked here — no test ever makes a real
API call. Fixtures return fakes that also record their call counts so tests can assert
the caching behaviour (a cached request must not call the provider again).
"""

from __future__ import annotations

import pytest
from django.conf import settings
from ninja.testing import TestClient

from config.api import api
from services.embeddings import EmbeddingProvider
from services.llm import LLMProvider


class FakeLLM(LLMProvider):
    """Records calls and returns a canned JSON object."""

    def __init__(self, response: dict) -> None:
        self.response = response
        self.calls: list[tuple[str, str]] = []

    def complete_json(self, system_prompt: str, user_content: str) -> dict:
        self.calls.append((system_prompt, user_content))
        return self.response


class FakeEmbedder(EmbeddingProvider):
    """Records calls and returns a fixed-length deterministic vector."""

    def __init__(self, vector: list[float] | None = None) -> None:
        self._vector = vector or ([0.1] * settings.EMBEDDING_DIM)
        self.calls: list[str] = []

    @property
    def dimensions(self) -> int:
        return settings.EMBEDDING_DIM

    def embed(self, text: str) -> list[float]:
        self.calls.append(text)
        return list(self._vector)


@pytest.fixture
def client() -> TestClient:
    """Ninja test client bound to the real root API (routers + schemas exercised)."""
    return TestClient(api)


@pytest.fixture
def job_extraction() -> dict:
    return {
        "hard_skills": ["python", "django", "postgres"],
        "soft_skills": ["communication"],
        "seniority": "senior",
        "salary_min": 90000,
        "salary_max": 120000,
        "salary_currency": "USD",
        "red_flags": ["vague scope"],
    }


@pytest.fixture
def resume_extraction() -> dict:
    return {
        "hard_skills": ["python", "django"],
        "soft_skills": ["communication"],
        "seniority": "senior",
        "years_experience": 7,
        "titles": ["Backend Engineer"],
    }


@pytest.fixture
def fake_llm(job_extraction: dict) -> FakeLLM:
    return FakeLLM(job_extraction)


@pytest.fixture
def fake_embedder() -> FakeEmbedder:
    return FakeEmbedder()
