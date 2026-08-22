import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

from backend.config import settings
from backend.database.database import init_db
from backend.api import health_routes, job_routes, resume_routes, screening_routes, dashboard_routes
from backend.utils.logging_config import logger

# Initialize DB tables
init_db()

app = FastAPI(
    title="Smart Resume Screener API",
    description="AI-powered recruitment resume screening and job matching backend",
    version="1.0.0",
    debug=settings.DEBUG
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health_routes.router)
app.include_router(job_routes.router)
app.include_router(resume_routes.router)
app.include_router(screening_routes.router)
app.include_router(dashboard_routes.router)

# Mount Frontend static assets
frontend_dir = settings.BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/frontend", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

# Mount Sample Data for easy browser download
sample_dir = settings.BASE_DIR / "sample_data"
if sample_dir.exists():
    app.mount("/sample_data", StaticFiles(directory=str(sample_dir)), name="sample_data")

@app.get("/")
def root():
    """Redirect root path to the recruiter frontend dashboard."""
    if frontend_dir.exists():
        return RedirectResponse(url="/frontend/index.html")
    return {"message": "Smart Resume Screener API is running. Access /docs for API documentation."}

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
