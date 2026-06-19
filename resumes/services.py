"""Resume parsing service: LLM extraction + cheap embedding, cached by content hash."""

from __future__ import annotations

from resumes.models import Resume
from services.embeddings import EmbeddingProvider, get_embedder
from services.hashing import content_hash
from services.llm import LLMProvider, get_llm
from services.prompts import RESUME_EXTRACTION_PROMPT


def _embedding_text(parsed: dict) -> str:
    """Same canonical shape as jobs so the two vectors are comparable."""
    parts = [
        parsed.get("seniority", ""),
        " ".join(parsed.get("hard_skills", [])),
        " ".join(parsed.get("soft_skills", [])),
    ]
    return " ".join(p for p in parts if p)


def parse_resume(
    raw_text: str,
    *,
    llm: LLMProvider | None = None,
    embedder: EmbeddingProvider | None = None,
) -> tuple[Resume, bool]:
    """Return (resume, cached). On a cache hit, NO provider is called."""
    key = content_hash(raw_text)
    existing = Resume.objects.filter(content_hash=key).first()
    if existing is not None:
        return existing, True

    llm = llm or get_llm()
    embedder = embedder or get_embedder()

    parsed = llm.complete_json(RESUME_EXTRACTION_PROMPT, raw_text)
    vector = embedder.embed(_embedding_text(parsed))

    resume = Resume.objects.create(
        content_hash=key,
        raw_text=raw_text,
        hard_skills=parsed.get("hard_skills", []),
        soft_skills=parsed.get("soft_skills", []),
        seniority=parsed.get("seniority", "") or "",
        years_experience=parsed.get("years_experience"),
        titles=parsed.get("titles", []),
        embedding=vector,
    )
    return resume, False
