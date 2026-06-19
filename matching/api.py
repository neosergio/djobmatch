from __future__ import annotations

from ninja import Router
from ninja.errors import HttpError

from jobs.models import Job
from matching.schemas import MatchExplanation, MatchOut, MatchRequest
from matching.services import compute_match
from resumes.models import Resume

router = Router(tags=["matching"])


@router.post("", response=MatchOut)
def match(request, payload: MatchRequest) -> MatchOut:
    resume = Resume.objects.filter(pk=payload.resume_id).first()
    if resume is None:
        raise HttpError(404, "Resume not found. Parse it via /resumes/parse first.")

    job = Job.objects.filter(pk=payload.job_id).first()
    if job is None:
        raise HttpError(404, "Job not found. Parse it via /jobs/parse first.")

    obj, cached = compute_match(resume, job)
    return MatchOut(
        id=obj.pk,
        resume_id=obj.resume_id,
        job_id=obj.job_id,
        score=obj.score,
        explanation=MatchExplanation(**obj.explanation),
        cached=cached,
    )
