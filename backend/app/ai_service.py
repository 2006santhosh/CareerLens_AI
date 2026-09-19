"""
AI service abstraction layer.

The rest of the backend never calls an LLM directly - it goes through this
module. This keeps the system maintainable and guarantees a working DEMO
fallback whenever AI_MODE=demo, or whenever a live call fails for any
reason (missing key, network/API outage, invalid response).
"""
import json
import re
from typing import Optional

import httpx

from .config import settings

EXTRACTION_SYSTEM_PROMPT = """You are a resume skill extraction engine. Extract ONLY skills that are \
explicitly supported by the supplied resume text. Map each extracted skill to the closest match in the \
supplied canonical skill list - do not invent skills that are not in that list and are not clearly present \
in the text. Return ONLY valid JSON matching this schema, with no preamble, no markdown fences:

{
  "skills": [{"name": "<canonical skill name>", "confidence": <0-1 float>, "evidence": "<short quote/paraphrase from text>"}],
  "projects": ["<short project name/description>"],
  "certifications": ["<certification name>"],
  "education": ["<degree / institution>"]
}
"""


class AIService:
    def __init__(self):
        self.mode = settings.ai_mode
        self.api_key = settings.ai_api_key

    # ---------------- public API ----------------

    def extract_resume(self, text: str, canonical_skills: list[str]) -> dict:
        """Extract structured skill/project/cert/education data from resume text."""
        if self.mode == "live" and self.api_key:
            result = self._call_live_extraction(text, canonical_skills)
            if result is not None:
                return {**result, "ai_mode": "live"}
        return {**self._demo_extraction(text, canonical_skills), "ai_mode": "demo"}

    def explain_gap(self, skill_name: str, required: int, current: int,
                     importance: str, is_prereq_for: list[str]) -> str:
        """Deterministic, template-based explanation (kept off the LLM critical path
        so gap explanations always work, even in demo mode)."""
        gap = max(0, required - current)
        parts = [
            f"{skill_name} has a target proficiency of {required} for this role; "
            f"your current demonstrated level is {current}, a gap of {gap} points."
        ]
        if importance == "High":
            parts.append(f"{skill_name} is a high-importance requirement for this career.")
        elif importance == "Medium":
            parts.append(f"{skill_name} is a moderately important requirement for this career.")
        if is_prereq_for:
            parts.append(
                f"It is also a prerequisite for {', '.join(is_prereq_for[:3])}, "
                f"so closing this gap unlocks progress on related skills."
            )
        return " ".join(parts)

    def recommend_resource_note(self, skill_name: str) -> str:
        return f"Recommended because it directly targets your current gap in {skill_name}."

    # ---------------- live provider ----------------

    def _call_live_extraction(self, text: str, canonical_skills: list[str]) -> Optional[dict]:
        try:
            skill_list_str = ", ".join(canonical_skills)
            user_prompt = (
                f"Canonical skill list: {skill_list_str}\n\n"
                f"Resume text:\n{text[:12000]}"
            )
            resp = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.ai_model,
                    "max_tokens": 1500,
                    "system": EXTRACTION_SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            text_out = "".join(
                block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
            )
            text_out = re.sub(r"^```json|```$", "", text_out.strip(), flags=re.MULTILINE).strip()
            parsed = json.loads(text_out)
            # Validate minimal schema shape before trusting it
            if "skills" not in parsed or not isinstance(parsed["skills"], list):
                return None
            valid_names = {s.lower() for s in canonical_skills}
            parsed["skills"] = [
                s for s in parsed["skills"]
                if isinstance(s, dict) and s.get("name", "").lower() in valid_names
            ]
            parsed.setdefault("projects", [])
            parsed.setdefault("certifications", [])
            parsed.setdefault("education", [])
            return parsed
        except Exception:
            # Any failure (network, auth, parsing) -> fall back to demo mode upstream
            return None

    # ---------------- demo / deterministic fallback ----------------

    def _demo_extraction(self, text: str, canonical_skills: list[str]) -> dict:
        """Deterministic keyword-matching extraction used for the hackathon demo
        and as a safety net when the live AI API is unavailable."""
        lower_text = text.lower()
        found = []
        for skill in canonical_skills:
            pattern = r"\b" + re.escape(skill.lower()) + r"\b"
            matches = list(re.finditer(pattern, lower_text))
            if matches:
                idx = matches[0].start()
                snippet = text[max(0, idx - 40): idx + len(skill) + 40].strip().replace("\n", " ")
                confidence = min(0.95, 0.6 + 0.1 * len(matches))
                found.append({"name": skill, "confidence": round(confidence, 2), "evidence": snippet or skill})

        projects = []
        for line in text.splitlines():
            if re.search(r"\bproject\b", line, re.IGNORECASE) and len(line.strip()) > 8:
                projects.append(line.strip()[:120])
        projects = projects[:5]

        certifications = []
        for line in text.splitlines():
            if re.search(r"certif", line, re.IGNORECASE) and len(line.strip()) > 5:
                certifications.append(line.strip()[:120])
        certifications = certifications[:5]

        education = []
        for line in text.splitlines():
            if re.search(r"\b(b\.?tech|bachelor|master|university|college|degree)\b", line, re.IGNORECASE):
                education.append(line.strip()[:150])
        education = education[:3]

        return {
            "skills": found,
            "projects": projects,
            "certifications": certifications,
            "education": education,
        }


ai_service = AIService()
