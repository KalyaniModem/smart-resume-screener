from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.repositories import JobRepository
from backend.schemas.job_schema import JobCreate, JobResponse
from backend.utils.validation import validate_job_description

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    """Create and persist a new job description."""
    validate_job_description(job_in.title, job_in.description)
    job = JobRepository.create(
        db=db,
        title=job_in.title.strip(),
        description=job_in.description.strip(),
        required_skills=job_in.required_skills,
        min_experience=job_in.min_experience,
        education_req=job_in.education_req
    )
    return job

@router.get("", response_model=List[JobResponse])
def list_jobs(limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve list of created job descriptions."""
    return JobRepository.get_all(db=db, limit=limit)

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get job description by ID."""
    job = JobRepository.get_by_id(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job
