from __future__ import annotations

from ninja import Router

from jobs.schemas import JobOut, JobParseRequest
from jobs.services import parse_job

router = Router(tags=["jobs"])


@router.post("/parse", response=JobOut)
def parse(request, payload: JobParseRequest) -> JobOut:
    job, cached = parse_job(payload.raw_text)
    return JobOut(
        id=job.pk,
        seniority=job.seniority,
        hard_skills=job.hard_skills,
        soft_skills=job.soft_skills,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        red_flags=job.red_flags,
        cached=cached,
    )
