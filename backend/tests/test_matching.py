import pytest
from backend.services.llm_service import clean_json_response, repair_and_parse_json
from backend.services.matching_service import rule_based_fallback_matching

def test_clean_json_response():
    markdown_json = "```json\n{\"score\": 8.5}\n```"
    cleaned = clean_json_response(markdown_json)
    assert cleaned == "{\"score\": 8.5}"

def test_repair_and_parse_json():
    raw_text = "Here is the result:\n```json\n{\"match_score\": 8.5, \"recommendation\": \"Shortlist\"}\n```\nHope this helps."
    parsed = repair_and_parse_json(raw_text)
    assert parsed["match_score"] == 8.5
    assert parsed["recommendation"] == "Shortlist"

def test_rule_based_fallback_matching():
    eval_res = rule_based_fallback_matching(
        job_title="Senior Python Engineer",
        job_description="Seeking Python, FastAPI, PostgreSQL, Docker developer.",
        candidate_name="Alex Chen",
        candidate_skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
        candidate_education=[{"degree": "BS Computer Science"}],
        candidate_experience=[{"job_title": "Senior Engineer"}],
        raw_text="Senior Python Engineer with FastAPI and PostgreSQL expertise.",
        threshold=7.0
    )
    
    assert eval_res["match_score"] >= 7.0
    assert eval_res["recommendation"] == "Shortlist"
    assert eval_res["shortlist_status"] == "Shortlisted"
    assert "Python" in eval_res["matching_skills"]
