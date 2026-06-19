from __future__ import annotations

from django.conf import settings
from django.db import models
from pgvector.django import VectorField


class Job(models.Model):
    """A parsed job posting.

    Cached by `content_hash` (SHA-256 of the normalized raw text): the same posting
    is only ever parsed by the LLM once. `embedding` holds the cheap vector used for
    cosine scoring in the matcher.
    """

    content_hash = models.CharField(max_length=64, unique=True, db_index=True)
    raw_text = models.TextField()

    # Structured extraction produced by the LLM.
    hard_skills = models.JSONField(default=list)
    soft_skills = models.JSONField(default=list)
    seniority = models.CharField(max_length=32, blank=True)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    salary_currency = models.CharField(max_length=3, blank=True)
    red_flags = models.JSONField(default=list)

    embedding = VectorField(dimensions=settings.EMBEDDING_DIM)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Job<{self.pk} {self.seniority}>"
