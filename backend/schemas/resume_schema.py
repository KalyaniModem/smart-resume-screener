from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class EducationSchema(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    field: Optional[str] = None
    graduation_year: Optional[str] = None

class ExperienceSchema(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    duration: Optional[str] = None
    responsibilities: Optional[str] = None

class SkillSchema(BaseModel):
    skill_name: str
    category: Optional[str] = None

class CandidateStructured(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    education: List[EducationSchema] = []
    experience: List[ExperienceSchema] = []
    skills: List[str] = []

class CandidateResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    resume_filename: str
    created_at: datetime
    education: List[EducationSchema] = []
    experience: List[ExperienceSchema] = []
    skills: List[SkillSchema] = []

    model_config = ConfigDict(from_attributes=True)

