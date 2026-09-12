from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src import models, schemas
from src.database import get_db
from src.scoring import rank_jobs_for_candidate, score_job

router = APIRouter(tags=["recommendations"])


@router.get(
    "/candidates/{candidate_id}/recommendations",
    response_model=List[schemas.JobRecommendation],
)
def recommend_jobs(
    candidate_id: int,
    limit: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db),
):
    candidate = db.get(models.Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    jobs = db.query(models.Job).all()
    return rank_jobs_for_candidate(candidate, jobs, limit=limit)


@router.get(
    "/jobs/{job_id}/recommendations",
    response_model=List[schemas.JobRecommendation],
)
def recommend_candidates_for_job(
    job_id: int,
    limit: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db),
):
    job = db.get(models.Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    candidates = db.query(models.Candidate).all()

    scored = []
    for cand in candidates:
        result = score_job(cand, job)
        if result is None:
            continue
        scored.append({
            "job_id": cand.id,
            "title": cand.name,
            "overall_score": result["overall_score"],
            "breakdown": result["breakdown"],
        })

    scored.sort(key=lambda r: r["overall_score"], reverse=True)
    if limit:
        scored = scored[:limit]
    return scored