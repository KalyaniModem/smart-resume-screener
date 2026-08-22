import json
import csv
import io
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.repositories import ScreeningRepository
from backend.schemas.screening_schema import ScreeningRequest
from backend.services.screening_service import ScreeningService
from backend.utils.logging_config import logger

router = APIRouter(prefix="/api", tags=["Screening"])

@router.post("/screen")
def run_screening(req: ScreeningRequest, db: Session = Depends(get_db)):
    """Run batch screening of candidate resumes against a job description."""
    if not req.candidate_ids:
        raise HTTPException(status_code=400, detail="No candidate IDs provided for screening.")

    results = []
    failed = []

    for candidate_id in req.candidate_ids:
        try:
            res = ScreeningService.screen_candidate(
                db=db,
                job_id=req.job_id,
                candidate_id=candidate_id,
                threshold=req.threshold
            )
            results.append(res)
        except Exception as e:
            logger.error(f"Error screening candidate ID {candidate_id}: {str(e)}")
            failed.append({"candidate_id": candidate_id, "error": str(e)})

    return {
        "message": f"Completed screening for {len(results)} candidates.",
        "screenings": results,
        "failed": failed
    }

@router.get("/screenings")
def list_screenings(
    job_id: Optional[int] = Query(None),
    shortlist_only: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Retrieve list of completed screening evaluations with filtering options."""
    screenings = ScreeningRepository.get_all(db=db, job_id=job_id, shortlist_only=shortlist_only)
    
    output = []
    for s in screenings:
        details = s.details
        matching_skills = json.loads(details.matching_skills) if details and details.matching_skills else []
        missing_skills = json.loads(details.missing_skills) if details and details.missing_skills else []
        strengths = json.loads(details.strengths) if details and details.strengths else []
        gaps = json.loads(details.gaps) if details and details.gaps else []
        relevant_experience = json.loads(details.relevant_experience) if details and details.relevant_experience else []

        output.append({
            "id": s.id,
            "job_id": s.job_id,
            "job_title": s.job.title if s.job else "Unknown Job",
            "candidate_id": s.candidate_id,
            "candidate_name": s.candidate.name if s.candidate else "Unknown Candidate",
            "candidate_email": s.candidate.email if s.candidate else "",
            "match_score": s.match_score,
            "recommendation": s.recommendation,
            "shortlist_status": s.shortlist_status,
            "threshold_used": s.threshold_used,
            "justification": s.justification,
            "created_at": s.created_at,
            "details": {
                "matching_skills": matching_skills,
                "missing_skills": missing_skills,
                "strengths": strengths,
                "gaps": gaps,
                "relevant_experience": relevant_experience,
                "education_match": details.education_match if details else "",
                "skills_score": details.skills_score if details else None,
                "experience_score": details.experience_score if details else None,
                "education_score": details.education_score if details else None
            }
        })
    return output

@router.get("/screenings/{screening_id}")
def get_screening_detail(screening_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed screening evaluation breakdown for candidate."""
    s = ScreeningRepository.get_by_id(db=db, screening_id=screening_id)
    if not s:
        raise HTTPException(status_code=404, detail="Screening result not found.")

    details = s.details
    matching_skills = json.loads(details.matching_skills) if details and details.matching_skills else []
    missing_skills = json.loads(details.missing_skills) if details and details.missing_skills else []
    strengths = json.loads(details.strengths) if details and details.strengths else []
    gaps = json.loads(details.gaps) if details and details.gaps else []
    relevant_experience = json.loads(details.relevant_experience) if details and details.relevant_experience else []

    cand = s.candidate
    return {
        "id": s.id,
        "job_id": s.job_id,
        "job_title": s.job.title if s.job else "",
        "job_description": s.job.description if s.job else "",
        "candidate_id": s.candidate_id,
        "candidate_name": cand.name if cand else "",
        "candidate_email": cand.email if cand else "",
        "candidate_phone": cand.phone if cand else "",
        "candidate_location": cand.location if cand else "",
        "resume_filename": cand.resume_filename if cand else "",
        "match_score": s.match_score,
        "recommendation": s.recommendation,
        "shortlist_status": s.shortlist_status,
        "threshold_used": s.threshold_used,
        "justification": s.justification,
        "created_at": s.created_at,
        "skills": [sk.skill_name for sk in cand.skills] if cand else [],
        "education": [{"degree": e.degree, "institution": e.institution, "field": e.field, "graduation_year": e.graduation_year} for e in cand.education] if cand else [],
        "experience": [{"job_title": ex.job_title, "company": ex.company, "duration": ex.duration, "responsibilities": ex.responsibilities} for ex in cand.experience] if cand else [],
        "details": {
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "strengths": strengths,
            "gaps": gaps,
            "relevant_experience": relevant_experience,
            "education_match": details.education_match if details else "",
            "skills_score": details.skills_score if details else None,
            "experience_score": details.experience_score if details else None,
            "education_score": details.education_score if details else None
        }
    }

@router.get("/screenings/export/csv")
def export_screenings_csv(job_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """Export screening results to a CSV spreadsheet."""
    screenings = ScreeningRepository.get_all(db=db, job_id=job_id)
    
    stream = io.StringIO()
    writer = csv.writer(stream)
    
    # Write header
    writer.writerow([
        "Screening ID", "Candidate Name", "Email", "Job Title",
        "Match Score", "Recommendation", "Shortlist Status",
        "Matching Skills", "Missing Skills", "Justification"
    ])

    for s in screenings:
        details = s.details
        matching_skills = ", ".join(json.loads(details.matching_skills)) if details and details.matching_skills else ""
        missing_skills = ", ".join(json.loads(details.missing_skills)) if details and details.missing_skills else ""

        writer.writerow([
            s.id,
            s.candidate.name if s.candidate else "N/A",
            s.candidate.email if s.candidate else "N/A",
            s.job.title if s.job else "N/A",
            s.match_score,
            s.recommendation,
            s.shortlist_status,
            matching_skills,
            missing_skills,
            s.justification
        ])

    stream.seek(0)
    response = StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = "attachment; filename=screening_results.csv"
    return response
