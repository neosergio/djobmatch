from __future__ import annotations

from ninja import Router

from resumes.schemas import ResumeOut, ResumeParseRequest
from resumes.services import parse_resume

router = Router(tags=["resumes"])


@router.post("/parse", response=ResumeOut)
def parse(request, payload: ResumeParseRequest) -> ResumeOut:
    resume, cached = parse_resume(payload.raw_text)
    return ResumeOut(
        id=resume.pk,
        seniority=resume.seniority,
        hard_skills=resume.hard_skills,
        soft_skills=resume.soft_skills,
        years_experience=resume.years_experience,
        titles=resume.titles,
        cached=cached,
    )
