"""Job parsing service: LLM extraction + cheap embedding, cached by content hash."""

from __future__ import annotations

from jobs.models import Job
from services.embeddings import EmbeddingProvider, get_embedder
from services.hashing import content_hash
from services.llm import LLMProvider, get_llm
from services.prompts import JOB_EXTRACTION_PROMPT


def _embedding_text(parsed: dict) -> str:
    """Canonical text embedded for matching — built from parsed fields, not raw text,
    so jobs and resumes live in a comparable vector space."""
    parts = [
        parsed.get("seniority", ""),
        " ".join(parsed.get("hard_skills", [])),
        " ".join(parsed.get("soft_skills", [])),
    ]
    return " ".join(p for p in parts if p)


def parse_job(
    raw_text: str,
    *,
    llm: LLMProvider | None = None,
    embedder: EmbeddingProvider | None = None,
) -> tuple[Job, bool]:
    """Return (job, cached). On a cache hit, NO provider is called."""
    key = content_hash(raw_text)
    existing = Job.objects.filter(content_hash=key).first()
    if existing is not None:
        return existing, True

    llm = llm or get_llm()
    embedder = embedder or get_embedder()

    parsed = llm.complete_json(JOB_EXTRACTION_PROMPT, raw_text)
    vector = embedder.embed(_embedding_text(parsed))

    job = Job.objects.create(
        content_hash=key,
        raw_text=raw_text,
        hard_skills=parsed.get("hard_skills", []),
        soft_skills=parsed.get("soft_skills", []),
        seniority=parsed.get("seniority", "") or "",
        salary_min=parsed.get("salary_min"),
        salary_max=parsed.get("salary_max"),
        salary_currency=parsed.get("salary_currency") or "",
        red_flags=parsed.get("red_flags", []),
        embedding=vector,
    )
    return job, False
