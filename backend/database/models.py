import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(Text, nullable=True)      # Comma or JSON string
    min_experience = Column(String(100), nullable=True)
    education_req = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    screenings = relationship("Screening", back_populates="job", cascade="all, delete-orphan")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=False)
    resume_filename = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    education = relationship("Education", back_populates="candidate", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="candidate", cascade="all, delete-orphan")
    screenings = relationship("Screening", back_populates="candidate", cascade="all, delete-orphan")


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    degree = Column(String(255), nullable=True)
    institution = Column(String(255), nullable=True)
    field = Column(String(255), nullable=True)
    graduation_year = Column(String(50), nullable=True)

    candidate = relationship("Candidate", back_populates="education")


class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_title = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    duration = Column(String(100), nullable=True)
    responsibilities = Column(Text, nullable=True)

    candidate = relationship("Candidate", back_populates="experience")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=True)

    candidate = relationship("Candidate", back_populates="skills")


class Screening(Base):
    __tablename__ = "screenings"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    match_score = Column(Float, nullable=False)
    recommendation = Column(String(50), nullable=False)    # e.g., "Shortlist" or "Not Shortlisted"
    shortlist_status = Column(String(50), nullable=False) # e.g., "Shortlisted" or "Not Shortlisted"
    threshold_used = Column(Float, default=7.0)
    justification = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    job = relationship("Job", back_populates="screenings")
    candidate = relationship("Candidate", back_populates="screenings")
    details = relationship("ScreeningDetails", back_populates="screening", uselist=False, cascade="all, delete-orphan")


class ScreeningDetails(Base):
    __tablename__ = "screening_details"

    id = Column(Integer, primary_key=True, index=True)
    screening_id = Column(Integer, ForeignKey("screenings.id", ondelete="CASCADE"), nullable=False, unique=True)
    matching_skills = Column(Text, nullable=True)       # JSON string
    missing_skills = Column(Text, nullable=True)        # JSON string
    strengths = Column(Text, nullable=True)             # JSON string
    gaps = Column(Text, nullable=True)                  # JSON string
    relevant_experience = Column(Text, nullable=True) # JSON string
    education_match = Column(Text, nullable=True)
    skills_score = Column(Float, nullable=True)
    experience_score = Column(Float, nullable=True)
    education_score = Column(Float, nullable=True)

    screening = relationship("Screening", back_populates="details")
