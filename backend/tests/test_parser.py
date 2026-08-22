import pytest
from backend.services.text_extractor import clean_extracted_text
from backend.services.resume_parser import extract_email, extract_phone, extract_name, segment_resume_sections
from backend.services.resume_structurer import normalize_skill, extract_skills_heuristics

def test_clean_extracted_text():
    raw = "  Line 1   with   spaces\r\n\r\n\r\nLine 2  "
    cleaned = clean_extracted_text(raw)
    assert "Line 1 with spaces" in cleaned
    assert "Line 2" in cleaned
    assert "\r" not in cleaned

def test_extract_contact_info():
    sample = """
    Alex Chen
    Email: alex.chen@example.com
    Phone: (555) 234-5678
    San Francisco, CA
    """
    assert extract_email(sample) == "alex.chen@example.com"
    assert extract_phone(sample) == "(555) 234-5678"
    assert extract_name(sample) == "Alex Chen"

def test_normalize_skill():
    assert normalize_skill("js") == "JavaScript"
    assert normalize_skill("Javascript") == "JavaScript"
    assert normalize_skill("Postgres") == "PostgreSQL"
    assert normalize_skill("ML") == "Machine Learning"
    assert normalize_skill("K8s") == "Kubernetes"

def test_extract_skills_heuristics():
    text = "Proficient in Python, FastAPI, Postgres, Docker, JS, and Machine Learning."
    skills = extract_skills_heuristics(text)
    assert "Python" in skills
    assert "FastAPI" in skills
    assert "PostgreSQL" in skills
    assert "JavaScript" in skills
    assert "Machine Learning" in skills

def test_segment_resume_sections():
    sample = """
    Alex Chen
    
    SUMMARY
    Senior Engineer with 5 years experience.
    
    SKILLS
    Python, SQL, AWS
    
    WORK EXPERIENCE
    Senior Engineer at Tech Corp
    """
    sections = segment_resume_sections(sample)
    assert "summary" in sections
    assert "skills" in sections
    assert "experience" in sections
