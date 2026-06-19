"""Prompt templates for the LLM extraction and explanation calls.

Kept here (not inline in the providers) so the wording is provider-agnostic and
easy to tweak without touching the SDK plumbing.
"""

from __future__ import annotations

JOB_EXTRACTION_PROMPT = """\
You are a job-posting parser. Read the raw job posting and return a JSON object
with exactly these keys:

- "hard_skills": list of strings (concrete technical skills, tools, languages).
- "soft_skills": list of strings (communication, leadership, etc.).
- "seniority": string — the REAL seniority implied by the responsibilities, one of
  "intern", "junior", "mid", "senior", "lead", "principal". Ignore inflated titles.
- "salary_min": number or null (yearly, in the posting's currency).
- "salary_max": number or null.
- "salary_currency": 3-letter ISO code or null.
- "red_flags": list of strings (vague scope, unpaid work, unrealistic demands, etc.).

Return ONLY the JSON object, no prose, no markdown fences.
"""

RESUME_EXTRACTION_PROMPT = """\
You are a resume parser. Read the raw resume and return a JSON object with exactly
these keys:

- "hard_skills": list of strings (concrete technical skills, tools, languages).
- "soft_skills": list of strings.
- "seniority": string — one of "intern", "junior", "mid", "senior", "lead",
  "principal", inferred from real experience.
- "years_experience": number or null.
- "titles": list of strings (past job titles).

Return ONLY the JSON object, no prose, no markdown fences.
"""

MATCH_EXPLANATION_PROMPT = """\
You are an explainable hiring assistant. You are given a parsed JOB and a parsed
RESUME as JSON, plus a precomputed numeric match score (0-100) that was derived
from embedding similarity — do NOT recompute it, just explain it.

Return a JSON object with exactly these keys:

- "summary": one or two sentences on how well the candidate fits.
- "strengths": list of strings (skills/experience that match).
- "gaps": list of strings (required things the candidate is missing).

Return ONLY the JSON object, no prose, no markdown fences.
"""
