import json
import re
import httpx
from typing import Dict, Any, Optional
from backend.config import settings
from backend.utils.logging_config import logger

def clean_json_response(raw_text: str) -> str:
    """Clean markdown code fence wrappers and trim excess whitespace."""
    if not raw_text:
        return ""
    text = raw_text.strip()
    # Strip markdown ```json ... ``` wrappers
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text, flags=re.I)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()

def repair_and_parse_json(text: str) -> Dict[str, Any]:
    """Attempt parsing JSON text with regex boundary fallback."""
    cleaned = clean_json_response(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("Standard JSON parse failed, attempting regex JSON repair...")
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        raise ValueError("Could not parse structured JSON response from LLM.")

class LLMService:
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY
        self.provider = settings.LLM_PROVIDER.lower()

    def is_configured(self) -> bool:
        """Check if any LLM API key is configured."""
        return bool(self.gemini_key or self.openai_key)

    def generate_completion(self, prompt: str) -> str:
        """Call configured LLM API (Gemini or OpenAI) with fallback."""
        if (self.provider == "gemini" or self.provider == "auto") and self.gemini_key:
            try:
                return self._call_gemini_api(prompt)
            except Exception as e:
                logger.error(f"Gemini API call failed: {str(e)}")
                if self.openai_key:
                    logger.info("Falling back to OpenAI API...")
                    return self._call_openai_api(prompt)
                raise e

        if (self.provider == "openai" or self.provider == "auto") and self.openai_key:
            return self._call_openai_api(prompt)

        raise RuntimeError("No LLM API key configured (GEMINI_API_KEY or OPENAI_API_KEY required).")

    def _call_gemini_api(self, prompt: str) -> str:
        """Execute HTTP request to Google Gemini API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={self.gemini_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API returned error {resp.status_code}: {resp.text}")
            data = resp.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                raise ValueError("Malformed response structure from Gemini API.")

    def _call_openai_api(self, prompt: str) -> str:
        """Execute HTTP request to OpenAI API."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"OpenAI API returned error {resp.status_code}: {resp.text}")
            data = resp.json()
            return data["choices"][0]["message"]["content"]

llm_service = LLMService()
