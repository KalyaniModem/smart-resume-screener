from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.repositories import DashboardRepository
from backend.schemas.screening_schema import DashboardStatsResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Retrieve summary cards analytics for recruiter dashboard."""
    stats = DashboardRepository.get_stats(db=db)
    return stats
