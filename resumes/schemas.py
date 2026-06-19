from __future__ import annotations

from ninja import Field, Schema


class ResumeParseRequest(Schema):
    raw_text: str = Field(..., min_length=1)


class ResumeOut(Schema):
    id: int
    seniority: str
    hard_skills: list[str]
    soft_skills: list[str]
    years_experience: int | None
    titles: list[str]
    cached: bool = False
