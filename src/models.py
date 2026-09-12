from sqlalchemy import Column, Integer, String, Boolean, JSON
from src.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    skills = Column(JSON, nullable=False, default=list)
    years_of_experience = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    expected_salary = Column(Integer, nullable=False)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    must_have_skills = Column(JSON, nullable=False, default=list)
    nice_to_have_skills = Column(JSON, nullable=False, default=list)
    min_years_experience = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    salary_min = Column(Integer, nullable=False)
    salary_max = Column(Integer, nullable=False)
    remote_allowed = Column(Boolean, default=False)