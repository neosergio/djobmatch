from __future__ import annotations

from django.db import models


class Match(models.Model):
    """A scored (resume, job) pair.

    Unique per pair, so an already-computed match is never recomputed: the cheap
    cosine `score` and the LLM-generated `explanation` are both cached here.
    """

    resume = models.ForeignKey("resumes.Resume", on_delete=models.CASCADE, related_name="matches")
    job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE, related_name="matches")

    score = models.PositiveSmallIntegerField()  # 0-100, from cosine similarity (no LLM)
    explanation = models.JSONField(default=dict)  # summary/strengths/gaps, from the LLM

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["resume", "job"], name="unique_resume_job_match"),
        ]

    def __str__(self) -> str:
        return f"Match<resume={self.resume_id} job={self.job_id} score={self.score}>"
