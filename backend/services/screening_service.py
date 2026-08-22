from pathlib import Path
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.database.repositories import CandidateRepository, JobRepository, ScreeningRepository
from backend.services.text_extractor import extract_text_from_file
from backend.services.resume_structurer import structure_resume_fallback
from backend.services.matching_service import evaluate_candidate_match
from backend.utils.logging_config import logger

class ScreeningService:
    @staticmethod
    def process_and_save_resume(db: Session, file_path: Path, original_filename: str) -> Dict[str, Any]:
        """Extract text, parse structured information, and store candidate in DB."""
        logger.info(f"Extracting text from uploaded file: {original_filename}")
        raw_text = extract_text_from_file(file_path)
        
        logger.info(f"Structuring candidate information for {original_filename}")
        structured = structure_resume_fallback(raw_text, original_filename)

        candidate = CandidateRepository.create(
            db=db,
            name=structured["name"],
            raw_text=raw_text,
            resume_filename=original_filename,
            email=structured.get("email"),
            phone=structured.get("phone"),
            location=structured.get("location"),
            education_list=structured.get("education", []),
            experience_list=structured.get("experience", []),
            skills_list=structured.get("skills", [])
        )
        logger.info(f"Candidate {candidate.name} (ID: {candidate.id}) saved to database.")

        return {
            "candidate_id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "location": candidate.location,
            "skills": [s.skill_name for s in candidate.skills],
            "resume_filename": candidate.resume_filename
        }

    @staticmethod
    def screen_candidate(db: Session, job_id: int, candidate_id: int, threshold: float = 7.0) -> Dict[str, Any]:
        """Perform semantic screening of candidate against specified job and store result."""
        job = JobRepository.get_by_id(db, job_id)
        if not job:
            raise ValueError(f"Job with ID {job_id} not found.")

        candidate = CandidateRepository.get_by_id(db, candidate_id)
        if not candidate:
            raise ValueError(f"Candidate with ID {candidate_id} not found.")

        candidate_skills = [s.skill_name for s in candidate.skills]
        candidate_education = [
            {"degree": e.degree, "institution": e.institution, "field": e.field, "graduation_year": e.graduation_year}
            for e in candidate.education
        ]
        candidate_experience = [
            {"job_title": ex.job_title, "company": ex.company, "duration": ex.duration, "responsibilities": ex.responsibilities}
            for ex in candidate.experience
        ]

        logger.info(f"Screening Candidate '{candidate.name}' against Job '{job.title}' (Threshold: {threshold})")
        eval_result = evaluate_candidate_match(
            job_title=job.title,
            job_description=job.description,
            candidate_name=candidate.name,
            candidate_skills=candidate_skills,
            candidate_education=candidate_education,
            candidate_experience=candidate_experience,
            raw_text=candidate.raw_text,
            threshold=threshold
        )

        screening = ScreeningRepository.create(
            db=db,
            job_id=job.id,
            candidate_id=candidate.id,
            match_score=eval_result["match_score"],
            recommendation=eval_result["recommendation"],
            shortlist_status=eval_result["shortlist_status"],
            justification=eval_result["justification"],
            threshold_used=threshold,
            matching_skills=eval_result["matching_skills"],
            missing_skills=eval_result["missing_skills"],
            strengths=eval_result["strengths"],
            gaps=eval_result["gaps"],
            relevant_experience=eval_result["relevant_experience"],
            education_match=eval_result["education_match"],
            skills_score=eval_result.get("skills_score"),
            experience_score=eval_result.get("experience_score"),
            education_score=eval_result.get("education_score")
        )

        logger.info(f"Screening completed for Candidate '{candidate.name}': Score={screening.match_score}, Status={screening.shortlist_status}")

        return {
            "screening_id": screening.id,
            "candidate_id": candidate.id,
            "candidate_name": candidate.name,
            "job_id": job.id,
            "job_title": job.title,
            "match_score": screening.match_score,
            "recommendation": screening.recommendation,
            "shortlist_status": screening.shortlist_status,
            "justification": screening.justification,
            "why_shortlisted": eval_result.get("why_shortlisted", []),
            "eval_details": eval_result
        }
