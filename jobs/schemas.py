from __future__ import annotations

from ninja import Field, Schema


class JobParseRequest(Schema):
    raw_text: str = Field(..., min_length=1)


class JobOut(Schema):
    id: int
    seniority: str
    hard_skills: list[str]
    soft_skills: list[str]
    salary_min: int | None
    salary_max: int | None
    salary_currency: str
    red_flags: list[str]
    cached: bool = False
