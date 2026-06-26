# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Author / owner: Sergio Infante (<rsinfante@gmail.com>). Copyright © 2026 Sergio Infante.

## Commands

All commands run through `uv` (never `pip`/`poetry`). The toolchain pins Python 3.14.

```bash
uv sync                                   # install deps into .venv
uv run python manage.py migrate           # apply migrations
uv run python manage.py runserver         # serve at http://127.0.0.1:8000/api/
uv run python manage.py makemigrations    # after model changes
uv run pytest                             # full test suite
uv run pytest tests/test_matching.py      # one file
uv run pytest tests/test_matching.py::test_match_is_cached   # one test
uv run ruff format . && uv run ruff check --fix .            # format + lint
```

Tests and `runserver` need a Postgres DB with `pgvector` (see README). Migrations and
`makemigrations` only need settings to load (a valid `DATABASE_URL` in `.env`, no live
connection).

## The core architecture decision (do not violate)

The whole design is a cost split: **the LLM is expensive, embeddings are cheap.**

- The LLM is called in exactly three places: extract job JSON (`jobs/services.py`),
  extract resume JSON (`resumes/services.py`), generate the match explanation
  (`matching/services.py`). Nowhere else.
- The match **score is never produced by the LLM** — it is cosine distance between the
  two pgvector embeddings (`matching/services._cosine_score`). Keep it that way.
- Results are **cached in the DB**. `Job`/`Resume` are keyed by `content_hash` (SHA-256
  of normalized raw text); `Match` is unique per `(resume, job)`. The cache check is the
  first thing each service does and returns `(obj, cached: bool)`. Adding work that
  re-calls a provider on a cache hit is a regression — the tests assert call counts.

## Provider abstraction

Endpoints and services must NOT import the OpenAI SDK directly. They depend on the
interfaces in `services/`:

- `services/llm.py` — `LLMProvider` (ABC) + `OpenAILLMProvider` + `get_llm()` factory.
- `services/embeddings.py` — `EmbeddingProvider` (ABC) + `OpenAIEmbeddingProvider` +
  `get_embedder()` factory.

To add Anthropic/Voyage: write one concrete class and add a branch to the factory. The
provider is chosen by `LLM_PROVIDER` / `EMBEDDING_PROVIDER` env vars. Domain services
accept optional `llm=` / `embedder=` params so tests inject fakes (see
`tests/conftest.py` — providers are always mocked, no real API calls).

`OpenAILLMProvider` returns parsed JSON via `_extract_json`, which tolerates markdown
fences and surrounding prose. The embedding dimension (`settings.EMBEDDING_DIM`, 1536
for `text-embedding-3-small`) must match the `VectorField(dimensions=...)` columns.

## Layout

- `config/` — the project module: `settings.py` (single file, django-environ),
  `urls.py`, and `api.py` (the root `NinjaAPI`, which registers one router per app).
- `jobs/`, `resumes/`, `matching/` — one app per domain. Each has `models.py`,
  `schemas.py` (Ninja request/response, kept separate from models), `services.py`
  (LLM/embedding + caching), and `api.py` (the router; thin — it calls the service).
- `services/` — provider abstractions + `prompts.py` + `hashing.py`. Not a Django app.
- `tests/` — pytest at the repo root; `DJANGO_SETTINGS_MODULE=config.settings` is set in
  `pyproject.toml`.

## Migrations & pgvector

The `vector` extension is enabled by its own migration, `jobs/0001_enable_pgvector.py`
(`VectorExtension`). It must run before any `VectorField` table is created:
`jobs/0002_initial` follows it implicitly (same app) and `resumes/0001_initial` declares
an explicit dependency on it. Preserve that ordering when regenerating migrations.

## Endpoints (do not add others without being asked)

- `POST /api/jobs/parse` → `JobOut`
- `POST /api/resumes/parse` → `ResumeOut`
- `POST /api/match` (body: `resume_id`, `job_id`) → `MatchOut`

## Conventions

- Type hints everywhere; `from __future__ import annotations` at the top of modules.
- Ruff is the formatter and linter (config in `pyproject.toml`, line length 100).
- Lean by intent: no Celery, no Docker, no extra layers. Match the existing structure
  rather than introducing new patterns.
