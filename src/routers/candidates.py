from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src import models, schemas
from src.database import get_db

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("", response_model=schemas.CandidateOut, status_code=201)
def create_candidate(payload: schemas.CandidateCreate, db: Session = Depends(get_db)):
    candidate = models.Candidate(**payload.model_dump())
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("/{candidate_id}", response_model=schemas.CandidateOut)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(models.Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate