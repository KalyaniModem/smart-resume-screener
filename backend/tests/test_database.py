import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.database import Base
from backend.database.repositories import JobRepository, CandidateRepository, ScreeningRepository, DashboardRepository

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_job_repository(db):
    job = JobRepository.create(db, title="Python Dev", description="Build APIs with FastAPI")
    assert job.id is not None
    assert job.title == "Python Dev"
    
    fetched = JobRepository.get_by_id(db, job.id)
    assert fetched.description == "Build APIs with FastAPI"

def test_candidate_repository(db):
    candidate = CandidateRepository.create(
        db=db,
        name="John Doe",
        raw_text="Full resume text",
        resume_filename="resume.txt",
        skills_list=["Python", "SQL"]
    )
    assert candidate.id is not None
    assert candidate.name == "John Doe"
    
    fetched = CandidateRepository.get_by_id(db, candidate.id)
    skills = [s.skill_name for s in fetched.skills]
    assert "Python" in skills
    assert "SQL" in skills

def test_screening_and_dashboard_repository(db):
    job = JobRepository.create(db, title="Backend Dev", description="Python REST APIs")
    candidate = CandidateRepository.create(db, name="Alice", raw_text="Python dev", resume_filename="alice.txt")
    
    screening = ScreeningRepository.create(
        db=db,
        job_id=job.id,
        candidate_id=candidate.id,
        match_score=8.5,
        recommendation="Shortlist",
        shortlist_status="Shortlisted",
        justification="Strong fit",
        matching_skills=["Python"]
    )
    
    assert screening.id is not None
    assert screening.match_score == 8.5
    
    stats = DashboardRepository.get_stats(db)
    assert stats["total_candidates"] == 1
    assert stats["shortlisted"] == 1
    assert stats["average_match_score"] == 8.5
