"""Single-file settings driven by django-environ.

Reads everything from the environment (.env in development). No secrets live here.
"""

from __future__ import annotations

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    LLM_PROVIDER=(str, "openai"),
    EMBEDDING_PROVIDER=(str, "openai"),
    OPENAI_CHAT_MODEL=(str, "gpt-4o-mini"),
    OPENAI_EMBEDDING_MODEL=(str, "text-embedding-3-small"),
    OPENAI_API_KEY=(str, ""),
)

# Load .env if present (it is gitignored; production sets real env vars instead).
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="insecure-dev-key-change-me")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    # Local apps
    "jobs",
    "resumes",
    "matching",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    },
]

# Supabase Postgres (with pgvector). Parsed from a single DATABASE_URL.
DATABASES = {"default": env.db("DATABASE_URL")}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "static/"

USE_TZ = True
TIME_ZONE = "UTC"

# --- Provider configuration (consumed by services/) ---------------------------
LLM_PROVIDER = env("LLM_PROVIDER")
EMBEDDING_PROVIDER = env("EMBEDDING_PROVIDER")
OPENAI_API_KEY = env("OPENAI_API_KEY")
OPENAI_CHAT_MODEL = env("OPENAI_CHAT_MODEL")
OPENAI_EMBEDDING_MODEL = env("OPENAI_EMBEDDING_MODEL")

# Dimension of text-embedding-3-small. Keep in sync with the VectorField columns.
EMBEDDING_DIM = 1536
