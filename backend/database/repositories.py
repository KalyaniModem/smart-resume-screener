import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from backend.database.models import (
    Job, Candidate, Education, Experience, Skill, Screening, ScreeningDetails
)

class JobRepository:
    @staticmethod
    def create(db: Session, title: str, description: str, required_skills: Optional[str] = None,
               min_experience: Optional[str] = None, education_req: Optional[str] = None) -> Job:
        job = Job(
            title=title,
            description=description,
            required_skills=required_skills,
            min_experience=min_experience,
            education_req=education_req
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_by_id(db: Session, job_id: int) -> Optional[Job]:
        return db.query(Job).filter(Job.id == job_id).first()

    @staticmethod
    def get_all(db: Session, limit: int = 50) -> List[Job]:
        return db.query(Job).order_by(Job.created_at.desc()).limit(limit).all()


class CandidateRepository:
    @staticmethod
    def create(db: Session, name: str, raw_text: str, resume_filename: str,
               email: Optional[str] = None, phone: Optional[str] = None, location: Optional[str] = None,
               education_list: List[Dict[str, Any]] = None,
               experience_list: List[Dict[str, Any]] = None,
               skills_list: List[str] = None) -> Candidate:
        
        candidate = Candidate(
            name=name,
            email=email,
            phone=phone,
            location=location,
            raw_text=raw_text,
            resume_filename=resume_filename
        )
        db.add(candidate)
        db.flush()

        if education_list:
            for edu in education_list:
                db.add(Education(
                    candidate_id=candidate.id,
                    degree=edu.get("degree"),
                    institution=edu.get("institution"),
                    field=edu.get("field"),
                    graduation_year=edu.get("graduation_year")
                ))

        if experience_list:
            for exp in experience_list:
                db.add(Experience(
                    candidate_id=candidate.id,
                    job_title=exp.get("job_title"),
                    company=exp.get("company"),
                    duration=exp.get("duration"),
                    responsibilities=exp.get("responsibilities")
                ))

        if skills_list:
            for sk in set(skills_list):
                if sk.strip():
                    db.add(Skill(candidate_id=candidate.id, skill_name=sk.strip()))

        db.commit()
        db.refresh(candidate)
        return candidate

    @staticmethod
    def get_by_id(db: Session, candidate_id: int) -> Optional[Candidate]:
        return db.query(Candidate)\
            .options(joinedload(Candidate.education), joinedload(Candidate.experience), joinedload(Candidate.skills))\
            .filter(Candidate.id == candidate_id)\
            .first()

    @staticmethod
    def get_all(db: Session, limit: int = 100) -> List[Candidate]:
        return db.query(Candidate)\
            .options(joinedload(Candidate.skills))\
            .order_by(Candidate.created_at.desc())\
            .limit(limit)\
            .all()


class ScreeningRepository:
    @staticmethod
    def create(
        db: Session,
        job_id: int,
        candidate_id: int,
        match_score: float,
        recommendation: str,
        shortlist_status: str,
        justification: str,
        threshold_used: float = 7.0,
        matching_skills: List[str] = None,
        missing_skills: List[str] = None,
        strengths: List[str] = None,
        gaps: List[str] = None,
        relevant_experience: List[str] = None,
        education_match: str = "",
        skills_score: Optional[float] = None,
        experience_score: Optional[float] = None,
        education_score: Optional[float] = None
    ) -> Screening:
        
        screening = Screening(
            job_id=job_id,
            candidate_id=candidate_id,
            match_score=match_score,
            recommendation=recommendation,
            shortlist_status=shortlist_status,
            threshold_used=threshold_used,
            justification=justification
        )
        db.add(screening)
        db.flush()

        details = ScreeningDetails(
            screening_id=screening.id,
            matching_skills=json.dumps(matching_skills or []),
            missing_skills=json.dumps(missing_skills or []),
            strengths=json.dumps(strengths or []),
            gaps=json.dumps(gaps or []),
            relevant_experience=json.dumps(relevant_experience or []),
            education_match=education_match,
            skills_score=skills_score,
            experience_score=experience_score,
            education_score=education_score
        )
        db.add(details)
        db.commit()
        db.refresh(screening)
        return screening

    @staticmethod
    def get_by_id(db: Session, screening_id: int) -> Optional[Screening]:
        return db.query(Screening)\
            .options(joinedload(Screening.candidate), joinedload(Screening.job), joinedload(Screening.details))\
            .filter(Screening.id == screening_id)\
            .first()

    @staticmethod
    def get_all(db: Session, job_id: Optional[int] = None, shortlist_only: Optional[bool] = None) -> List[Screening]:
        query = db.query(Screening)\
            .options(joinedload(Screening.candidate), joinedload(Screening.job), joinedload(Screening.details))
        
        if job_id:
            query = query.filter(Screening.job_id == job_id)
        if shortlist_only is True:
            query = query.filter(Screening.shortlist_status == "Shortlisted")
        elif shortlist_only is False:
            query = query.filter(Screening.shortlist_status != "Shortlisted")

        return query.order_by(Screening.match_score.desc(), Screening.created_at.desc()).all()

    @staticmethod
    def get_latest_screening_for_candidate(db: Session, candidate_id: int) -> Optional[Screening]:
        return db.query(Screening)\
            .options(joinedload(Screening.candidate), joinedload(Screening.job), joinedload(Screening.details))\
            .filter(Screening.candidate_id == candidate_id)\
            .order_by(Screening.created_at.desc())\
            .first()


class DashboardRepository:
    @staticmethod
    def get_stats(db: Session) -> Dict[str, Any]:
        total_candidates = db.query(Candidate).count()
        total_screenings = db.query(Screening).count()
        shortlisted = db.query(Screening).filter(Screening.shortlist_status == "Shortlisted").count()
        not_shortlisted = total_screenings - shortlisted
        
        # Calculate average match score
        screenings = db.query(Screening.match_score).all()
        if screenings:
            avg_score = round(sum(s[0] for s in screenings) / len(screenings), 1)
        else:
            avg_score = 0.0

        return {
            "total_candidates": total_candidates,
            "total_screenings": total_screenings,
            "shortlisted": shortlisted,
            "not_shortlisted": not_shortlisted,
            "average_match_score": avg_score
        }
