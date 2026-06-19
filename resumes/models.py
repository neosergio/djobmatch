from __future__ import annotations

from django.conf import settings
from django.db import models
from pgvector.django import VectorField


class Resume(models.Model):
    """A parsed resume.

    Cached by `content_hash` just like Job: identical resume text is parsed once.
    `embedding` is the cheap vector used for cosine scoring against a job.
    """

    content_hash = models.CharField(max_length=64, unique=True, db_index=True)
    raw_text = models.TextField()

    hard_skills = models.JSONField(default=list)
    soft_skills = models.JSONField(default=list)
    seniority = models.CharField(max_length=32, blank=True)
    years_experience = models.IntegerField(null=True, blank=True)
    titles = models.JSONField(default=list)

    embedding = VectorField(dimensions=settings.EMBEDDING_DIM)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Resume<{self.pk} {self.seniority}>"
