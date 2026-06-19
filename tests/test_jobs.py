"""Tests for POST /jobs/parse — happy path, validation, and caching."""

from __future__ import annotations

import pytest

from jobs import services as jobs_services
from jobs.models import Job
from tests.conftest import FakeEmbedder, FakeLLM

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _patch_providers(monkeypatch, job_extraction):
    """Force the job service onto fakes so no real provider is ever hit."""
    llm = FakeLLM(job_extraction)
    embedder = FakeEmbedder()
    monkeypatch.setattr(jobs_services, "get_llm", lambda: llm)
    monkeypatch.setattr(jobs_services, "get_embedder", lambda: embedder)
    return llm, embedder


def test_parse_job_happy_path(client, _patch_providers):
    llm, embedder = _patch_providers
    resp = client.post("/jobs/parse", json={"raw_text": "Senior Django dev wanted"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["seniority"] == "senior"
    assert body["hard_skills"] == ["python", "django", "postgres"]
    assert body["salary_min"] == 90000
    assert body["cached"] is False
    assert Job.objects.count() == 1
    assert len(llm.calls) == 1
    assert len(embedder.calls) == 1


def test_parse_job_validation_error(client):
    resp = client.post("/jobs/parse", json={"raw_text": ""})
    assert resp.status_code == 422
    assert Job.objects.count() == 0


def test_parse_job_missing_field(client):
    resp = client.post("/jobs/parse", json={})
    assert resp.status_code == 422


def test_parse_job_is_cached(client, _patch_providers):
    """A second identical request must NOT call the providers again."""
    llm, embedder = _patch_providers
    text = "Senior Django dev wanted"

    first = client.post("/jobs/parse", json={"raw_text": text})
    second = client.post("/jobs/parse", json={"raw_text": text})

    assert first.json()["cached"] is False
    assert second.json()["cached"] is True
    assert first.json()["id"] == second.json()["id"]
    assert Job.objects.count() == 1
    # Provider called exactly once across both requests.
    assert len(llm.calls) == 1
    assert len(embedder.calls) == 1


def test_parse_job_whitespace_variants_share_cache(client, _patch_providers):
    """Normalization means trivially different whitespace hits the same cached row."""
    llm, _ = _patch_providers
    client.post("/jobs/parse", json={"raw_text": "Senior   Django   dev"})
    client.post("/jobs/parse", json={"raw_text": "Senior Django dev"})

    assert Job.objects.count() == 1
    assert len(llm.calls) == 1
