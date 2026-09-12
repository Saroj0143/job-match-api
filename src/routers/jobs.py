from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src import models, schemas
from src.database import get_db

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=schemas.JobOut, status_code=201)
def create_job(payload: schemas.JobCreate, db: Session = Depends(get_db)):
    if payload.salary_max < payload.salary_min:
        raise HTTPException(status_code=400, detail="salary_max must be >= salary_min")
    job = models.Job(**payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/{job_id}", response_model=schemas.JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(models.Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job