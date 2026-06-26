# djobmatch

**Author:** Sergio Infante (<rsinfante@gmail.com>)
Copyright © 2026 Sergio Infante. All rights reserved.

A small REST API (Django + Django Ninja) with two combined features:

1. **Job parser** — `POST /api/jobs/parse` turns the raw text of a job posting into
   structured JSON (hard/soft skills, real seniority, salary range, red flags).
2. **Explainable matcher** — `POST /api/match` scores an already-parsed resume against
   an already-parsed job (0–100) and explains the fit.

Resumes are parsed the same way via `POST /api/resumes/parse`.

## Architecture (the deliberate cost decision)

The LLM is expensive; embeddings are cheap. So:

- The **LLM** is used only to: extract the job JSON, extract the resume JSON, and
  generate the match explanation.
- The numeric match **score** is computed from **cosine distance between embeddings**
  (pgvector) — no LLM call.
- Everything is **cached in the DB**: a job/resume is parsed once (keyed by a hash of
  its normalized text); an already-matched `(resume, job)` pair is never recomputed.
- The LLM and embedding providers sit behind abstractions in `services/`
  (`llm.py`, `embeddings.py`). Endpoints call the services, never the SDK. OpenAI is
  the default provider; swapping to Anthropic/Voyage means adding one class.

## Requirements

- [uv](https://docs.astral.sh/uv/) (manages Python + dependencies)
- Python 3.14 (uv installs it automatically from `.python-version`)
- A Postgres database with the `pgvector` extension (the project targets Supabase)

## Setup

```bash
uv sync                      # create the venv and install everything
cp .env.example .env         # then fill in the values (see below)
uv run python manage.py migrate
uv run python manage.py runserver
```

Interactive API docs: http://127.0.0.1:8000/api/docs

## Environment variables (`.env`)

| Variable                 | Purpose                                                       |
| ------------------------ | ------------------------------------------------------------- |
| `SECRET_KEY`             | Django secret key                                             |
| `DEBUG`                  | `true` / `false`                                              |
| `ALLOWED_HOSTS`          | Comma-separated hosts                                         |
| `DATABASE_URL`           | Supabase Postgres URI (the DB must have `pgvector` available) |
| `LLM_PROVIDER`           | `openai` (default)                                            |
| `EMBEDDING_PROVIDER`     | `openai` (default)                                            |
| `OPENAI_API_KEY`         | OpenAI key for chat + embeddings                              |
| `OPENAI_CHAT_MODEL`      | Chat model (default `gpt-4o-mini`)                            |
| `OPENAI_EMBEDDING_MODEL` | Embedding model (default `text-embedding-3-small`, dim 1536)  |

`.env` is gitignored — never commit it. `.env.example` documents every variable.

## Tests

```bash
uv run pytest
```

Tests mock the LLM and embedding providers (no real API calls) and run against a
Postgres test database. They cover each endpoint (happy path + validation), the
caching logic (a second identical request does not call the provider again), and the
cosine-distance scoring.

> The test database needs Postgres with `pgvector`. Locally:
> `createdb djobmatch && psql -d djobmatch -c 'CREATE EXTENSION IF NOT EXISTS vector;'`
> The pgvector extension is also enabled by a migration (`jobs/0001_enable_pgvector`).

## Lint & format

```bash
uv run ruff format .
uv run ruff check .
```

## License

Copyright © 2026 Sergio Infante. Licensed under the Apache License, Version 2.0 —
see [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE).
