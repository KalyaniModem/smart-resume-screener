from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.repositories import CandidateRepository
from backend.schemas.resume_schema import CandidateResponse
from backend.services.screening_service import ScreeningService
from backend.utils.file_utils import save_uploaded_file
from backend.utils.validation import validate_uploaded_file
from backend.utils.logging_config import logger

router = APIRouter(prefix="/api", tags=["Resumes"])

@router.post("/resumes/upload")
async def upload_resumes(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload one or multiple PDF/TXT resume files, extract information, and store candidate profiles."""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    processed_candidates = []
    failed_files = []

    for upload_file in files:
        filename = upload_file.filename
        try:
            content = await upload_file.read()
            file_size = len(content)

            # Validate extension and size
            validate_uploaded_file(filename, file_size)

            # Save file to disk
            saved_path = save_uploaded_file(content, filename)

            # Extract text & store candidate
            candidate_info = ScreeningService.process_and_save_resume(
                db=db,
                file_path=saved_path,
                original_filename=filename
            )
            processed_candidates.append(candidate_info)

        except ValueError as ve:
            logger.warning(f"Validation error for file {filename}: {str(ve)}")
            failed_files.append({"filename": filename, "reason": str(ve)})
        except HTTPException as he:
            logger.warning(f"HTTP validation error for file {filename}: {he.detail}")
            failed_files.append({"filename": filename, "reason": he.detail})
        except Exception as e:
            logger.error(f"Failed to process uploaded file {filename}: {str(e)}")
            failed_files.append({"filename": filename, "reason": f"Processing error: {str(e)}"})

    if not processed_candidates and failed_files:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process uploaded files: {failed_files[0]['reason']}"
        )

    return {
        "message": f"Successfully processed {len(processed_candidates)} candidates.",
        "candidates": processed_candidates,
        "failed_files": failed_files
    }

@router.get("/candidates")
def list_candidates(limit: int = 100, db: Session = Depends(get_db)):
    """Get list of stored candidates."""
    candidates = CandidateRepository.get_all(db=db, limit=limit)
    return [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "location": c.location,
            "resume_filename": c.resume_filename,
            "created_at": c.created_at,
            "skills": [s.skill_name for s in c.skills],
            "education": [{"degree": e.degree, "institution": e.institution, "field": e.field, "graduation_year": e.graduation_year} for e in c.education],
            "experience": [{"job_title": ex.job_title, "company": ex.company, "duration": ex.duration, "responsibilities": ex.responsibilities} for ex in c.experience]
        }
        for c in candidates
    ]

@router.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get candidate profile detail by ID."""
    candidate = CandidateRepository.get_by_id(db=db, candidate_id=candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    
    return {
        "id": candidate.id,
        "name": candidate.name,
        "email": candidate.email,
        "phone": candidate.phone,
        "location": candidate.location,
        "resume_filename": candidate.resume_filename,
        "raw_text": candidate.raw_text,
        "created_at": candidate.created_at,
        "skills": [s.skill_name for s in candidate.skills],
        "education": [{"degree": e.degree, "institution": e.institution, "field": e.field, "graduation_year": e.graduation_year} for e in candidate.education],
        "experience": [{"job_title": ex.job_title, "company": ex.company, "duration": ex.duration, "responsibilities": ex.responsibilities} for ex in candidate.experience]
    }
