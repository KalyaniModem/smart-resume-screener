import re
from typing import Dict, List, Any, Optional

EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
PHONE_REGEX = r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
LOCATION_REGEX = r'([A-Z][a-zA-Z\s]+,\s*[A-Z]{2,4}\b|[A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z\s]+)'

SECTION_HEADERS = {
    "summary": ["SUMMARY", "PROFILE", "OBJECTIVE", "PROFESSIONAL SUMMARY", "ABOUT ME"],
    "skills": ["SKILLS", "TECHNICAL SKILLS", "CORE COMPETENCIES", "TECHNOLOGIES", "SKILLS & TECHNOLOGIES"],
    "experience": ["WORK EXPERIENCE", "EXPERIENCE", "EMPLOYMENT HISTORY", "PROFESSIONAL EXPERIENCE", "WORK HISTORY"],
    "education": ["EDUCATION", "ACADEMIC BACKGROUND", "EDUCATION & CREDENTIALS", "QUALIFICATIONS"],
    "projects": ["PROJECTS", "PERSONAL PROJECTS", "ACADEMIC PROJECTS", "KEY PROJECTS"],
    "certifications": ["CERTIFICATIONS", "LICENSES", "CERTIFICATES", "ACCOMPLISHMENTS", "ACHIEVEMENTS"]
}

def extract_email(text: str) -> Optional[str]:
    match = re.search(EMAIL_REGEX, text)
    return match.group(0) if match else None

def extract_phone(text: str) -> Optional[str]:
    match = re.search(PHONE_REGEX, text)
    return match.group(0) if match else None

def extract_name(text: str) -> str:
    """Extract candidate name from header lines heuristic."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:5]:
        # Exclude lines containing contact keywords or standard resume headers
        if re.search(r'(@|phone|tel|http|resume|cv|summary|experience|curriculum)', line, re.I):
            continue
        # Clean line of bullet characters or numbers
        clean = re.sub(r'[^a-zA-Z\s\.\-]', '', line).strip()
        words = clean.split()
        if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words if w and w[0].isalpha()):
            return clean
    return "Candidate"

def extract_location(text: str) -> Optional[str]:
    lines = text.split("\n")[:10]  # Check header lines
    for line in lines:
        match = re.search(LOCATION_REGEX, line)
        if match:
            loc = match.group(0).strip()
            if not any(k in loc.lower() for k in ["university", "college", "company", "inc", "ltd"]):
                return loc
    return None

def segment_resume_sections(text: str) -> Dict[str, str]:
    """Segment raw resume text into logical section chunks based on section headers."""
    sections = {}
    lines = text.split("\n")
    current_section = "header"
    sections[current_section] = []

    for line in lines:
        trimmed = line.strip().upper()
        # Clean trailing colon or dashes
        header_candidate = re.sub(r'[:\-\=\#]', '', trimmed).strip()

        found_header = None
        for sec_name, keywords in SECTION_HEADERS.items():
            if header_candidate in keywords:
                found_header = sec_name
                break

        if found_header:
            current_section = found_header
            if current_section not in sections:
                sections[current_section] = []
        else:
            sections[current_section].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items() if v}
