import json
import re
from typing import Optional
import requests

from codereviewai.models import CodeReviewResult

DEFAULT_MODELS = {
    "gemini": "gemini-3.6-flash",
    "openai": "gpt-4o",
    "anthropic": "claude-3-5-sonnet-20241022",
}

REVIEW_PROMPT_TEMPLATE = """You are a Principal Staff Engineer. Review the provided code for bugs, vulnerabilities, and logic errors.
CRITICAL: Output ONLY valid JSON. Do not include markdown formatting or explanation outside the JSON.
The JSON MUST follow this exact structure:
{
  "issues": [
    {
      "file": "<filename>",
      "line_number": <integer>,
      "severity": "HIGH" (or "MEDIUM" or "LOW"),
      "category": "<e.g. Bug, Security, Performance>",
      "explanation": "<description>",
      "suggested_fix": "<markdown code block with ```>"
    }
  ],
  "summary": "<overall summary>"
}

Code to review:
"""


class CodeReviewClient:
    def __init__(self, provider: str, api_key: str, model: Optional[str] = None, timeout: int = 120):
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model or DEFAULT_MODELS.get(self.provider, "gemini-3.6-flash")
        self.timeout = timeout

    def review_code(self, file_content: str, filename: str = "code") -> CodeReviewResult:
        prompt = f"{REVIEW_PROMPT_TEMPLATE}\n// File: {filename}\n{file_content}"

        if self.provider == "openai":
            raw_text = self._call_openai(prompt)
        elif self.provider == "anthropic":
            raw_text = self._call_anthropic(prompt)
        elif self.provider == "gemini":
            raw_text = self._call_gemini(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Supported: gemini, openai, anthropic")

        cleaned_json = self._extract_json(raw_text)
        try:
            data = json.loads(cleaned_json)
            return CodeReviewResult.model_validate(data)
        except Exception as e:
            raise ValueError(f"Failed to parse LLM response into review schema: {e}\nRaw output: {raw_text[:500]}")

    def _call_openai(self, prompt: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "user", "content": prompt}],
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"OpenAI API Error ({resp.status_code}): {resp.text}")
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def _call_anthropic(self, prompt: str) -> str:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"Anthropic API Error ({resp.status_code}): {resp.text}")
        data = resp.json()
        return data["content"][0]["text"]

    def _call_gemini(self, prompt: str) -> str:
        fallback_models = [self.model]
        if self.model == "gemini-3.6-flash":
            fallback_models.extend(["gemini-2.5-pro", "gemini-2.0-flash"])

        last_error = None
        for model_name in fallback_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"},
            }
            
            for attempt in range(3):
                try:
                    resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if not candidates or "content" not in candidates[0]:
                            raise RuntimeError(f"Gemini API Error: No valid content in response ({data})")
                        return candidates[0]["content"]["parts"][0]["text"]
                    
                    if resp.status_code in (429, 500, 502, 503, 504):
                        last_error = f"Gemini API Error ({resp.status_code}): {resp.text}"
                        import time
                        time.sleep(1.5 * (attempt + 1))
                        continue
                    else:
                        raise RuntimeError(f"Gemini API Error ({resp.status_code}): {resp.text}")
                except requests.exceptions.RequestException as e:
                    last_error = str(e)
                    import time
                    time.sleep(1.5 * (attempt + 1))
                    
        raise RuntimeError(last_error or f"Gemini API failed across attempts and fallback models.")

    @staticmethod
    def _extract_json(text: str) -> str:
        text = text.strip()
        # Remove ```json ... ``` code fence if present
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

        # Find outer braces if surrounded by other text
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        return text
