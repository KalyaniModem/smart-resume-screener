import re
from typing import Dict, List, Any
from backend.services.resume_parser import (
    extract_name, extract_email, extract_phone, extract_location, segment_resume_sections
)

SKILL_NORMALIZATION_MAP = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "java script": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "py": "Python",
    "python": "Python",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "postgres sql": "PostgreSQL",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "html": "HTML5",
    "html5": "HTML5",
    "css": "CSS3",
    "css3": "CSS3",
    "sql": "SQL",
    "sqlite": "SQLite",
    "redis": "Redis",
    "git": "Git"
}

KNOWN_SKILLS = set(SKILL_NORMALIZATION_MAP.values())

def normalize_skill(skill: str) -> str:
    """Normalize skill name variations (e.g. JS -> JavaScript, Postgres -> PostgreSQL)."""
    clean = skill.strip().strip("-•*,;")
    key = clean.lower()
    return SKILL_NORMALIZATION_MAP.get(key, clean)

def extract_skills_heuristics(text: str) -> List[str]:
    """Extract and normalize candidate skills using dictionary lookup and regex matching."""
    extracted = set()
    
    # 1. Direct dictionary match against text
    for key, normalized in SKILL_NORMALIZATION_MAP.items():
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, text, re.I):
            extracted.add(normalized)

    # 2. Extract bullet points / CSV tokens from Skills section
    sections = segment_resume_sections(text)
    skills_text = sections.get("skills", "")
    if skills_text:
        raw_tokens = re.split(r'[,;|\n•\-\*]', skills_text)
        for token in raw_tokens:
            token_clean = token.strip()
            if 2 <= len(token_clean) <= 30 and not re.search(r'(experience|years|proficient|knowledge|strong|skills)', token_clean, re.I):
                normalized = normalize_skill(token_clean)
                extracted.add(normalized)

    return sorted(list(extracted))

def parse_education_heuristics(edu_text: str) -> List[Dict[str, Any]]:
    """Parse education entries from education section text."""
    if not edu_text:
        return []

    results = []
    lines = [l.strip() for l in edu_text.split("\n") if l.strip()]
    for line in lines:
        if any(keyword in line.lower() for keyword in ["bachelor", "master", "phd", "b.s", "m.s", "b.a", "m.a", "degree", "diploma", "university", "college", "institute"]):
            year_match = re.search(r'\b(19|20)\d{2}\b', line)
            year = year_match.group(0) if year_match else None
            results.append({
                "degree": line,
                "institution": line,
                "field": line,
                "graduation_year": year
            })

    return results[:3]

def parse_experience_heuristics(exp_text: str) -> List[Dict[str, Any]]:
    """Parse work experience items from experience section text."""
    if not exp_text:
        return []

    entries = []
    current_entry = None
    lines = exp_text.split("\n")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Look for job title / company indicator (e.g. Engineer | Company | Date)
        if "|" in stripped or " - " in stripped or any(k in stripped.lower() for k in ["engineer", "developer", "analyst", "manager", "lead", "specialist", "assistant"]):
            if current_entry:
                entries.append(current_entry)
            
            current_entry = {
                "job_title": stripped,
                "company": stripped,
                "duration": "N/A",
                "responsibilities": []
            }
        elif current_entry:
            current_entry["responsibilities"].append(stripped)

    if current_entry:
        entries.append(current_entry)

    # Format responsibilities
    formatted = []
    for entry in entries[:5]:
        formatted.append({
            "job_title": entry["job_title"],
            "company": entry["company"],
            "duration": entry["duration"],
            "responsibilities": " ".join(entry["responsibilities"][:3])
        })
    return formatted

def structure_resume_fallback(raw_text: str, filename: str) -> Dict[str, Any]:
    """Complete rule-based fallback resume structurer."""
    sections = segment_resume_sections(raw_text)
    
    name = extract_name(raw_text)
    email = extract_email(raw_text)
    phone = extract_phone(raw_text)
    location = extract_location(raw_text)
    skills = extract_skills_heuristics(raw_text)
    education = parse_education_heuristics(sections.get("education", ""))
    experience = parse_experience_heuristics(sections.get("experience", ""))

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "summary": sections.get("summary", ""),
        "skills": skills,
        "education": education,
        "experience": experience,
        "raw_text": raw_text,
        "resume_filename": filename
    }
