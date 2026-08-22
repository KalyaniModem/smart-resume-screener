from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from backend.schemas.job_schema import JobResponse
from backend.schemas.resume_schema import CandidateResponse

class ScreeningRequest(BaseModel):
    job_id: int
    candidate_ids: List[int]
    threshold: float = Field(default=7.0, ge=1.0, le=10.0)

class ScreeningDetailsSchema(BaseModel):
    matching_skills: List[str] = []
    missing_skills: List[str] = []
    strengths: List[str] = []
    gaps: List[str] = []
    relevant_experience: List[str] = []
    education_match: Optional[str] = None
    skills_score: Optional[float] = None
    experience_score: Optional[float] = None
    education_score: Optional[float] = None

class ScreeningResponse(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    match_score: float
    recommendation: str
    shortlist_status: str
    threshold_used: float
    justification: str
    created_at: datetime
    candidate: CandidateResponse
    job: JobResponse
    details: Optional[ScreeningDetailsSchema] = None

    model_config = ConfigDict(from_attributes=True)


class DashboardStatsResponse(BaseModel):
    total_candidates: int
    total_screenings: int
    shortlisted: int
    not_shortlisted: int
    average_match_score: float
