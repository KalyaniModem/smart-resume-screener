from fastapi import APIRouter
from backend.services.llm_service import llm_service

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health")
def health_check():
    """Application status and LLM configuration health check endpoint."""
    return {
        "status": "healthy",
        "service": "Smart Resume Screener API",
        "llm_configured": llm_service.is_configured(),
        "llm_provider": llm_service.provider
    }
