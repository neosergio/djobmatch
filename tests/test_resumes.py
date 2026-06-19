"""Tests for POST /resumes/parse — happy path, validation, and caching."""

from __future__ import annotations

import pytest

from resumes import services as resumes_services
from resumes.models import Resume
from tests.conftest import FakeEmbedder, FakeLLM

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _patch_providers(monkeypatch, resume_extraction):
    llm = FakeLLM(resume_extraction)
    embedder = FakeEmbedder()
    monkeypatch.setattr(resumes_services, "get_llm", lambda: llm)
    monkeypatch.setattr(resumes_services, "get_embedder", lambda: embedder)
    return llm, embedder


def test_parse_resume_happy_path(client, _patch_providers):
    llm, embedder = _patch_providers
    resp = client.post("/resumes/parse", json={"raw_text": "7 years of Django"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["seniority"] == "senior"
    assert body["years_experience"] == 7
    assert body["titles"] == ["Backend Engineer"]
    assert body["cached"] is False
    assert Resume.objects.count() == 1
    assert len(llm.calls) == 1
    assert len(embedder.calls) == 1


def test_parse_resume_validation_error(client):
    resp = client.post("/resumes/parse", json={"raw_text": ""})
    assert resp.status_code == 422
    assert Resume.objects.count() == 0


def test_parse_resume_is_cached(client, _patch_providers):
    llm, embedder = _patch_providers
    text = "7 years of Django"

    first = client.post("/resumes/parse", json={"raw_text": text})
    second = client.post("/resumes/parse", json={"raw_text": text})

    assert first.json()["cached"] is False
    assert second.json()["cached"] is True
    assert Resume.objects.count() == 1
    assert len(llm.calls) == 1
    assert len(embedder.calls) == 1
