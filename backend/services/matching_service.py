import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.config import settings
from backend.services.llm_service import llm_service, repair_and_parse_json
from backend.utils.logging_config import logger

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

def load_prompt_template(filename: str) -> str:
    path = PROMPTS_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def rule_based_fallback_matching(
    job_title: str,
    job_description: str,
    candidate_name: str,
    candidate_skills: List[str],
    candidate_education: List[Dict[str, Any]],
    candidate_experience: List[Dict[str, Any]],
    raw_text: str,
    threshold: float
) -> Dict[str, Any]:
    """Deterministic rule-based candidate matching engine when LLM API is unconfigured."""
    logger.info("Executing rule-based semantic evaluation fallback...")

    # Extract required skills from job description
    jd_lower = job_description.lower()
    
    # Common tech skills to check against JD
    common_skills = [
        "python", "fastapi", "django", "flask", "javascript", "typescript",
        "html", "css", "sql", "postgresql", "sqlite", "redis", "docker",
        "kubernetes", "aws", "gcp", "git", "linux", "pytest", "selenium",
        "postman", "java", "c++", "react", "node.js"
    ]
    
    required_skills = [s for s in common_skills if s in jd_lower]
    if not required_skills:
        required_skills = ["python", "sql", "git"]

    cand_skills_lower = set([s.lower() for s in candidate_skills])
    raw_lower = raw_text.lower()

    matching_skills = []
    missing_skills = []

    for req in required_skills:
        if req in cand_skills_lower or re.search(r'\b' + re.escape(req) + r'\b', raw_lower):
            matching_skills.append(req.title() if req not in ["sql", "html", "css", "aws", "gcp"] else req.upper())
        else:
            missing_skills.append(req.title() if req not in ["sql", "html", "css", "aws", "gcp"] else req.upper())

    # Calculate skill overlap percentage
    total_req = max(1, len(required_skills))
    skill_match_ratio = len(matching_skills) / total_req
    skills_score = round(min(100.0, skill_match_ratio * 100), 1)

    # Calculate experience score
    experience_score = 70.0
    relevant_exp_bullets = []

    if any(k in raw_lower for k in ["senior", "lead", "architect"]) and "senior" in job_title.lower():
        experience_score += 20.0
        relevant_exp_bullets.append("Demonstrates senior-level technical leadership experience.")
    elif "senior" in job_title.lower() and not any(k in raw_lower for k in ["senior", "lead"]):
        experience_score -= 20.0

    for exp in candidate_experience:
        title = exp.get("job_title", "")
        if any(w in title.lower() for w in job_title.lower().split()):
            relevant_exp_bullets.append(f"Relevant role: {title}")

    if not relevant_exp_bullets and candidate_experience:
        relevant_exp_bullets.append(f"Past experience: {candidate_experience[0].get('job_title', 'Software Professional')}")

    experience_score = max(30.0, min(95.0, experience_score))

    # Education score
    education_score = 80.0
    edu_match_text = "Educational background reviewed."
    if any(k in raw_lower for k in ["computer science", "software engineering", "information technology"]):
        education_score = 90.0
        edu_match_text = "Degree in Computer Science / IT aligns with technical role requirements."

    # Compute overall score (1.0 to 10.0 scale)
    overall_percentage = (skills_score * 0.5) + (experience_score * 0.35) + (education_score * 0.15)
    match_score = round(overall_percentage / 10.0, 1)
    match_score = max(1.0, min(10.0, match_score))

    is_shortlisted = match_score >= threshold
    recommendation = "Shortlist" if is_shortlisted else "Not Shortlisted"
    shortlist_status = "Shortlisted" if is_shortlisted else "Not Shortlisted"

    strengths = []
    gaps = []

    if matching_skills:
        strengths.append(f"Strong match in core skills: {', '.join(matching_skills[:3])}")
    if experience_score >= 75:
        strengths.append("Demonstrates relevant industry work experience.")

    if missing_skills:
        gaps.append(f"Missing required skills: {', '.join(missing_skills[:3])}")
    if experience_score < 70:
        gaps.append("Limited senior-level hands-on experience for this role.")

    why_shortlisted = []
    if is_shortlisted:
        why_shortlisted.append(f"Demonstrates strong alignment with {', '.join(matching_skills[:3])}.")
        why_shortlisted.append(edu_match_text)
        why_shortlisted.append("Meets required experience and qualification threshold.")
    else:
        why_shortlisted.append(f"Match score ({match_score}) falls below shortlist threshold ({threshold}).")
        if missing_skills:
            why_shortlisted.append(f"Lacks key requirements: {', '.join(missing_skills[:2])}.")

    justification = (
        f"Candidate {candidate_name} evaluated against '{job_title}'. "
        f"Demonstrates {len(matching_skills)} matching skills ({', '.join(matching_skills[:3])}) "
        f"with an overall match score of {match_score}/10."
    )

    return {
        "match_score": match_score,
        "skills_score": skills_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "recommendation": recommendation,
        "shortlist_status": shortlist_status,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "relevant_experience": relevant_exp_bullets,
        "education_match": edu_match_text,
        "strengths": strengths,
        "gaps": gaps,
        "justification": justification,
        "why_shortlisted": why_shortlisted,
        "is_fallback": True
    }

def evaluate_candidate_match(
    job_title: str,
    job_description: str,
    candidate_name: str,
    candidate_skills: List[str],
    candidate_education: List[Dict[str, Any]],
    candidate_experience: List[Dict[str, Any]],
    raw_text: str,
    threshold: float = 7.0
) -> Dict[str, Any]:
    """Semantic candidate evaluation using LLM with deterministic rule fallback."""
    if not llm_service.is_configured():
        return rule_based_fallback_matching(
            job_title, job_description, candidate_name,
            candidate_skills, candidate_education, candidate_experience,
            raw_text, threshold
        )

    try:
        template = load_prompt_template("matching_prompt.txt")
        prompt = template.format(
            job_title=job_title,
            job_description=job_description,
            candidate_name=candidate_name,
            candidate_skills=", ".join(candidate_skills),
            candidate_education=json.dumps(candidate_education),
            candidate_experience=json.dumps(candidate_experience),
            resume_text=raw_text[:3000] # Truncate to save tokens and prevent overload
        )

        response_text = llm_service.generate_completion(prompt)
        parsed = repair_and_parse_json(response_text)

        score = float(parsed.get("match_score", 5.0))
        score = max(1.0, min(10.0, score))

        is_shortlisted = score >= threshold
        recommendation = "Shortlist" if is_shortlisted else "Not Shortlisted"
        shortlist_status = "Shortlisted" if is_shortlisted else "Not Shortlisted"

        return {
            "match_score": score,
            "skills_score": float(parsed.get("skills_score", score * 10)),
            "experience_score": float(parsed.get("experience_score", score * 10)),
            "education_score": float(parsed.get("education_score", score * 10)),
            "recommendation": parsed.get("recommendation", recommendation),
            "shortlist_status": shortlist_status,
            "matching_skills": parsed.get("matching_skills", []),
            "missing_skills": parsed.get("missing_skills", []),
            "relevant_experience": parsed.get("relevant_experience", []),
            "education_match": parsed.get("education_match", "Reviewed"),
            "strengths": parsed.get("strengths", []),
            "gaps": parsed.get("gaps", []),
            "justification": parsed.get("justification", f"Evaluated score: {score}/10"),
            "why_shortlisted": parsed.get("why_shortlisted", [parsed.get("justification", "")]),
            "is_fallback": False
        }

    except Exception as e:
        logger.error(f"LLM matching failed: {str(e)}. Falling back to deterministic matcher.")
        return rule_based_fallback_matching(
            job_title, job_description, candidate_name,
            candidate_skills, candidate_education, candidate_experience,
            raw_text, threshold
        )
