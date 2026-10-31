import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv

load_dotenv()


class GemmaConfigurationError(RuntimeError):
    pass


class GemmaRequestError(RuntimeError):
    pass


def suggest_tasks(project_name: str, description: str, current_tasks: list[str]) -> list[dict]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GemmaConfigurationError(
            "GEMINI_API_KEY is not configured. Add a Google AI Studio key to backend/.env."
        )
    model = os.getenv("GEMMA_MODEL", "gemma-3-27b-it")
    prompt = (
        "You are a project planning assistant. Return only valid JSON with a "
        'single "suggestions" array. Each item must have "title", "description", '
        'and "priority" where priority is low, medium, or high. Suggest no more '
        "than five practical next tasks for this project.\n"
        f"Project: {project_name}\nDescription: {description}\n"
        f"Existing tasks: {json.dumps(current_tasks)}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    request = Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=45) as response:
            response_data = json.loads(response.read())
    except (HTTPError, URLError, TimeoutError) as error:
        raise GemmaRequestError(f"Gemma request failed: {error}") from error
    try:
        response_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        suggestions = json.loads(response_text)["suggestions"]
        if not isinstance(suggestions, list):
            raise TypeError
        return [
            {
                "title": item["title"],
                "description": item.get("description", ""),
                "priority": item.get("priority", "medium"),
            }
            for item in suggestions[:5]
        ]
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
        raise GemmaRequestError("Gemma returned invalid task suggestions") from error


def analyze_with_gemma(input_text: str) -> tuple[str, str]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GemmaConfigurationError(
            "GEMINI_API_KEY is not configured. Add a Google AI Studio key to backend/.env."
        )

    model = os.getenv("GEMMA_MODEL", "gemma-3-27b-it")
    prompt = (
        "Analyze the following submission for SiteSense. Return only valid JSON "
        'with exactly two string arrays: "findings" and "recommendations". '
        "Keep each item concise and practical.\n\nSubmission:\n" + input_text
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    request = Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=45) as response:
            response_data = json.loads(response.read())
    except (HTTPError, URLError, TimeoutError) as error:
        raise GemmaRequestError(f"Gemma request failed: {error}") from error

    try:
        response_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        result = json.loads(response_text)
        findings = result["findings"]
        recommendations = result["recommendations"]
        if not isinstance(findings, list) or not isinstance(recommendations, list):
            raise TypeError
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
        raise GemmaRequestError("Gemma returned an invalid analysis response") from error

    return json.dumps(findings), json.dumps(recommendations)
