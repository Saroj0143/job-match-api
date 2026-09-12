"""
Rule-based, explainable job matching scorer.

Total = 100 points, distributed as:
    Skills      : 50  (35 must-have + 15 nice-to-have)
    Experience  : 20
    Location    : 15
    Salary      : 15

See README.md for the full rationale behind these weights.
"""
from typing import Optional, Dict, Any

WEIGHTS = {
    "skills_must": 35,
    "skills_nice": 15,
    "experience": 20,
    "location": 15,
    "salary": 15,
}

MAX_TOTAL = sum(WEIGHTS.values())


def _normalize(skills):
    return {s.strip().lower() for s in (skills or []) if s and s.strip()}


def score_job(candidate, job) -> Optional[Dict[str, Any]]:
    candidate_skills = _normalize(candidate.skills)
    must_haves = _normalize(job.must_have_skills)
    nice_to_haves = _normalize(job.nice_to_have_skills)

    # 1. Must-have hard gate
    if not must_haves.issubset(candidate_skills):
        return None

    # 2. Skills (max 50)
    if must_haves:
        must_ratio = len(must_haves & candidate_skills) / len(must_haves)
    else:
        must_ratio = 1.0
    must_score = must_ratio * WEIGHTS["skills_must"]

    if nice_to_haves:
        nice_ratio = len(nice_to_haves & candidate_skills) / len(nice_to_haves)
    else:
        nice_ratio = 1.0
    nice_score = nice_ratio * WEIGHTS["skills_nice"]

    skills_score = must_score + nice_score

    # 3. Experience (max 20) — penalize, never exclude
    if candidate.years_of_experience >= job.min_years_experience:
        exp_score = WEIGHTS["experience"]
    else:
        shortfall = job.min_years_experience - candidate.years_of_experience
        exp_score = max(5, WEIGHTS["experience"] - shortfall * 5)

    # 4. Location (max 15) — 3 tiers
    if candidate.location.strip().lower() == job.location.strip().lower():
        loc_score = WEIGHTS["location"]
    elif job.remote_allowed:
        loc_score = WEIGHTS["location"] * 2 / 3
    else:
        loc_score = 0

    # 5. Salary (max 15) — overlap based
    exp_sal = candidate.expected_salary
    sal_min, sal_max = job.salary_min, job.salary_max

    if exp_sal <= sal_min:
        sal_score = WEIGHTS["salary"]
    elif exp_sal <= sal_max:
        span = max(sal_max - sal_min, 1)
        position = (exp_sal - sal_min) / span
        sal_score = WEIGHTS["salary"] - position * 10
    else:
        sal_score = 0

    total = skills_score + exp_score + loc_score + sal_score

    return {
        "overall_score": round(total),
        "breakdown": {
            "skills": f"{round(skills_score)}/{WEIGHTS['skills_must'] + WEIGHTS['skills_nice']}",
            "experience": f"{round(exp_score)}/{WEIGHTS['experience']}",
            "location": f"{round(loc_score)}/{WEIGHTS['location']}",
            "salary": f"{round(sal_score)}/{WEIGHTS['salary']}",
        },
    }


def rank_jobs_for_candidate(candidate, jobs, limit: Optional[int] = None):
    scored = []
    for job in jobs:
        result = score_job(candidate, job)
        if result is None:
            continue
        scored.append({
            "job_id": job.id,
            "title": job.title,
            "overall_score": result["overall_score"],
            "breakdown": result["breakdown"],
        })

    scored.sort(key=lambda r: r["overall_score"], reverse=True)

    if limit is not None:
        scored = scored[:limit]

    return scored