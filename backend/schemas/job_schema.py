from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class JobCreate(BaseModel):
    title: str = Field(..., description="Job title, e.g. Senior Python Developer")
    description: str = Field(..., description="Full text description of the job")
    required_skills: Optional[str] = None
    min_experience: Optional[str] = None
    education_req: Optional[str] = None

class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    required_skills: Optional[str] = None
    min_experience: Optional[str] = None
    education_req: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

