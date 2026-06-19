"""Root NinjaAPI: mounts one router per domain app."""

from __future__ import annotations

from ninja import NinjaAPI

from jobs.api import router as jobs_router
from matching.api import router as matching_router
from resumes.api import router as resumes_router

api = NinjaAPI(title="djobmatch API", version="1.0.0")

api.add_router("/jobs", jobs_router)
api.add_router("/resumes", resumes_router)
api.add_router("/match", matching_router)
