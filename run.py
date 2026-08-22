#!/usr/bin/env python3
"""
Application Launcher for Smart Resume Screener
"""
import sys
import uvicorn
from backend.config import settings
from backend.utils.logging_config import logger

if __name__ == "__main__":
    logger.info("Initializing Smart Resume Screener...")
    logger.info(f"Serving at http://{settings.HOST}:{settings.PORT}")
    logger.info(f"Recruiter Dashboard: http://{settings.HOST}:{settings.PORT}/frontend/index.html")
    logger.info(f"API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
