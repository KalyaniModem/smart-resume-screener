import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_create_and_get_job():
    payload = {
        "title": "Software Engineer",
        "description": "Must have Python, SQL, and FastAPI experience."
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 201
    job_data = response.json()
    assert job_data["title"] == "Software Engineer"
    job_id = job_data["id"]

    get_resp = client.get(f"/api/jobs/{job_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == job_id

def test_upload_resume_txt():
    content = b"Alex Chen\nEmail: alex@example.com\nPython, FastAPI, SQL Developer"
    files = {"files": ("test_resume.txt", content, "text/plain")}
    response = client.post("/api/resumes/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert len(data["candidates"]) == 1
    assert data["candidates"][0]["name"] == "Alex Chen"

def test_upload_invalid_file_type():
    content = b"Dummy docx content"
    files = {"files": ("test_resume.docx", content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    response = client.post("/api/resumes/upload", files=files)
    assert response.status_code == 400

def test_dashboard_stats():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_candidates" in data
    assert "average_match_score" in data
