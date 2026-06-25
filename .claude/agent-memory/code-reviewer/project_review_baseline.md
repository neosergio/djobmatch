---
name: project-review-baseline
description: Findings from the June 2026 full-codebase review of djobmatch
metadata:
  type: project
---

Full review conducted 2026-06-25. The architecture is sound and mostly clean. Key open issues:

**BLOCKER — Live secrets in .env on disk (not in git)**
- .env contains a real OpenAI API key (sk-proj-EBbQ8...) and Supabase DB credentials. The file is gitignored and was not committed, but the key should be rotated as a precaution since the .env may be exposed via other vectors (e.g., accidental inclusion, editor sync, etc.).

**HIGH — TOCTOU race condition in all three services**
- jobs/services.py:31-41, resumes/services.py:30-40, matching/services.py:73-84: the filter().first() then .create() pattern is not atomic. Two concurrent identical requests can both pass the cache check and both try to create, triggering an IntegrityError on the unique constraint. Fix: use get_or_create() or wrap in select_for_update/transaction.atomic.

**HIGH — LLM null value crash in _embedding_text**
- jobs/services.py:16-19 and resumes/services.py:13-19: if the LLM returns {"hard_skills": null}, dict.get("hard_skills", []) returns None (not []), causing TypeError in " ".join(None). Same applies in .create() calls for JSONField. Fix: use parsed.get("hard_skills") or [].

**HIGH — No global error handler for LLMError/EmbeddingError**
- jobs/api.py, resumes/api.py, matching/api.py: LLMError and EmbeddingError bubble up as unhandled exceptions, producing a 500 with a stack trace. Register exception handlers on the NinjaAPI in config/api.py.

**MEDIUM — salary_min/salary_max type mismatch**
- services/prompts.py says "number" (LLM returns floats like 90000.5); jobs/models.py uses IntegerField. Django silently truncates float -> int. Fix: change prompt to "integer" or use FloatField/DecimalField.

**MEDIUM — No max_length on raw_text inputs**
- jobs/schemas.py:7 and resumes/schemas.py:7: min_length=1 but no upper bound. A malicious or errant client can POST megabytes, burning tokens. Add max_length constraint (e.g., 50_000 chars).

**MEDIUM — _cosine_score crashes on None distance**
- matching/services.py:42: `1.0 - float(distance)` raises TypeError if the annotated query returns None (resume not in DB, which shouldn't happen at that point but is still fragile). Add a guard.

**LOW — Duplicate _embedding_text in two modules**
- jobs/services.py:12-19 and resumes/services.py:12-19 are identical. Extract to services/hashing.py or a new services/embedding_text.py to ensure they can never diverge.

**LOW — No whitespace-normalization test for resumes**
- test_resumes.py lacks the equivalent of test_jobs.py::test_parse_job_whitespace_variants_share_cache.

**LOW — test_match_unknown_job_returns_404 does not assert llm.calls==0**
- tests/test_matching.py:128: sister test for resume does assert it; job test does not.

**LOW — No tests for LLMError / EmbeddingError HTTP response**
- No test exercises the path where a provider raises, so the 500 behavior is untested.

**LOW — OPENAI_API_KEY defaults to "" in settings**
- config/settings.py:21: empty string default means misconfigured deployments fail at request time, not startup. Better to have no default and let django-environ raise on missing key.

**LOW — No authentication or rate limiting**
- config/api.py has no auth middleware; all endpoints are publicly callable. Acceptable for a personal project but worth noting for any future exposure.

**NIT — seniority not validated as enum**
- The LLM is instructed to return one of 6 values, but nothing in the model or schema enforces this. A hallucinated value is stored silently.

**Why:** First full review. **How to apply:** Use as baseline for future incremental reviews.
