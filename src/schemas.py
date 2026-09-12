from pydantic import BaseModel, Field
from typing import List


class CandidateCreate(BaseModel):
    name: str
    skills: List[str]
    years_of_experience: int = Field(..., ge=0)
    location: str
    expected_salary: int = Field(..., ge=0)


class CandidateOut(CandidateCreate):
    id: int

    class Config:
        from_attributes = True


class JobCreate(BaseModel):
    title: str
    must_have_skills: List[str] = []
    nice_to_have_skills: List[str] = []
    min_years_experience: int = Field(..., ge=0)
    location: str
    salary_min: int = Field(..., ge=0)
    salary_max: int = Field(..., ge=0)
    remote_allowed: bool = False


class JobOut(JobCreate):
    id: int

    class Config:
        from_attributes = True


class ScoreBreakdown(BaseModel):
    skills: str
    experience: str
    location: str
    salary: str


class JobRecommendation(BaseModel):
    job_id: int
    title: str
    overall_score: int
    breakdown: ScoreBreakdown