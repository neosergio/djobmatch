"""Tests for POST /match and the cosine scoring logic.

Covers the deliberate cost split: the score comes from cosine distance (no LLM),
the explanation comes from one LLM call, and the whole pair is cached.
"""

from __future__ import annotations

import pytest
from django.conf import settings

from jobs.models import Job
from matching import services as matching_services
from matching.models import Match
from matching.services import similarity_to_score
from resumes.models import Resume
from tests.conftest import FakeLLM

DIM = settings.EMBEDDING_DIM


# --- Pure scoring unit tests (no DB, no providers) ---------------------------


@pytest.mark.parametrize(
    ("similarity", "expected"),
    [
        (1.0, 100),  # identical direction
        (0.0, 50),  # orthogonal
        (-1.0, 0),  # opposite
        (0.5, 75),
    ],
)
def test_similarity_to_score(similarity, expected):
    assert similarity_to_score(similarity) == expected


def test_similarity_to_score_is_clamped():
    assert similarity_to_score(2.0) == 100
    assert similarity_to_score(-2.0) == 0


# --- DB-backed matching tests -------------------------------------------------

pytestmark = pytest.mark.django_db


def _make_job(embedding: list[float]) -> Job:
    return Job.objects.create(
        content_hash=f"job-{embedding[:2]}",
        raw_text="job",
        hard_skills=["python"],
        soft_skills=[],
        seniority="senior",
        red_flags=[],
        embedding=embedding,
    )


def _make_resume(embedding: list[float]) -> Resume:
    return Resume.objects.create(
        content_hash=f"resume-{embedding[:2]}",
        raw_text="resume",
        hard_skills=["python"],
        soft_skills=[],
        seniority="senior",
        years_experience=7,
        titles=[],
        embedding=embedding,
    )


@pytest.fixture(autouse=True)
def _patch_llm(monkeypatch):
    """The explanation LLM is mocked; the score must never touch it."""
    llm = FakeLLM({"summary": "Strong fit", "strengths": ["python"], "gaps": []})
    monkeypatch.setattr(matching_services, "get_llm", lambda: llm)
    return llm


def test_match_identical_vectors_scores_100(client, _patch_llm):
    vec = [1.0] + [0.0] * (DIM - 1)
    resume = _make_resume(vec)
    job = _make_job(list(vec))

    resp = client.post("/match", json={"resume_id": resume.pk, "job_id": job.pk})

    assert resp.status_code == 200
    body = resp.json()
    assert body["score"] == 100
    assert body["explanation"]["summary"] == "Strong fit"
    assert body["cached"] is False
    assert len(_patch_llm.calls) == 1


def test_match_orthogonal_vectors_scores_50(client, _patch_llm):
    resume = _make_resume([1.0, 0.0] + [0.0] * (DIM - 2))
    job = _make_job([0.0, 1.0] + [0.0] * (DIM - 2))

    resp = client.post("/match", json={"resume_id": resume.pk, "job_id": job.pk})

    assert resp.json()["score"] == 50


def test_match_is_cached(client, _patch_llm):
    """A repeat (resume, job) pair must not call the LLM again."""
    vec = [1.0] + [0.0] * (DIM - 1)
    resume = _make_resume(vec)
    job = _make_job(list(vec))

    first = client.post("/match", json={"resume_id": resume.pk, "job_id": job.pk})
    second = client.post("/match", json={"resume_id": resume.pk, "job_id": job.pk})

    assert first.json()["cached"] is False
    assert second.json()["cached"] is True
    assert first.json()["id"] == second.json()["id"]
    assert Match.objects.count() == 1
    assert len(_patch_llm.calls) == 1  # not called on the cache hit


def test_match_unknown_resume_returns_404(client, _patch_llm):
    job = _make_job([1.0] + [0.0] * (DIM - 1))
    resp = client.post("/match", json={"resume_id": 999, "job_id": job.pk})
    assert resp.status_code == 404
    assert len(_patch_llm.calls) == 0


def test_match_unknown_job_returns_404(client, _patch_llm):
    resume = _make_resume([1.0] + [0.0] * (DIM - 1))
    resp = client.post("/match", json={"resume_id": resume.pk, "job_id": 999})
    assert resp.status_code == 404
