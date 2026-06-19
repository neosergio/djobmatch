from __future__ import annotations

from ninja import Schema


class MatchRequest(Schema):
    resume_id: int
    job_id: int


class MatchExplanation(Schema):
    summary: str = ""
    strengths: list[str] = []
    gaps: list[str] = []


class MatchOut(Schema):
    id: int
    resume_id: int
    job_id: int
    score: int  # 0-100, cosine similarity — no LLM
    explanation: MatchExplanation
    cached: bool = False
