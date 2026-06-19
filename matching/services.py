"""Matching service — the deliberate cost split lives here.

    SCORE       -> cosine distance between the two pgvector embeddings. NO LLM.
    EXPLANATION -> a single LLM call over the two parsed JSONs.

Both are cached on the `Match` row, so a given (resume, job) pair is computed once.
"""

from __future__ import annotations

import json

from pgvector.django import CosineDistance

from jobs.models import Job
from matching.models import Match
from resumes.models import Resume
from services.llm import LLMProvider, get_llm
from services.prompts import MATCH_EXPLANATION_PROMPT


def similarity_to_score(similarity: float) -> int:
    """Map cosine similarity in [-1, 1] to an integer match score in [0, 100].

    Pure function (no DB, no provider) so the scoring rule is trivially unit-testable.
    """
    score = round((similarity + 1) / 2 * 100)
    return max(0, min(100, score))


def _cosine_score(resume: Resume, job: Job) -> int:
    """Compute the score via pgvector cosine distance. No LLM involved.

    pgvector returns cosine *distance* (1 - similarity); we convert back to similarity.
    """
    distance = (
        Resume.objects.filter(pk=resume.pk)
        .annotate(d=CosineDistance("embedding", job.embedding))
        .values_list("d", flat=True)
        .first()
    )
    similarity = 1.0 - float(distance)
    return similarity_to_score(similarity)


def _build_explanation(resume: Resume, job: Job, score: int, llm: LLMProvider) -> dict:
    """The ONLY LLM call in the matching path — prose only, never the score."""
    payload = {
        "score": score,
        "job": {
            "seniority": job.seniority,
            "hard_skills": job.hard_skills,
            "soft_skills": job.soft_skills,
            "red_flags": job.red_flags,
        },
        "resume": {
            "seniority": resume.seniority,
            "hard_skills": resume.hard_skills,
            "soft_skills": resume.soft_skills,
            "years_experience": resume.years_experience,
        },
    }
    return llm.complete_json(MATCH_EXPLANATION_PROMPT, json.dumps(payload))


def compute_match(
    resume: Resume,
    job: Job,
    *,
    llm: LLMProvider | None = None,
) -> tuple[Match, bool]:
    """Return (match, cached). On a cache hit, the LLM is NOT called."""
    existing = Match.objects.filter(resume=resume, job=job).first()
    if existing is not None:
        return existing, True

    # Cheap half: cosine score from embeddings, no LLM.
    score = _cosine_score(resume, job)

    # Expensive half: one LLM call for the human-readable explanation.
    llm = llm or get_llm()
    explanation = _build_explanation(resume, job, score, llm)

    match = Match.objects.create(
        resume=resume,
        job=job,
        score=score,
        explanation=explanation,
    )
    return match, False
