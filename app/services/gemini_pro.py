from google import genai
from google.genai import types

from app.config import settings
from app.schemas import OutlineResponse, PromptRequest, StoryResponse


def _client() -> genai.Client:
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Add it to .env before generating a comic."
        )
    return genai.Client(api_key=settings.gemini_api_key)


def generate_story(request: PromptRequest, outline: OutlineResponse) -> StoryResponse:
    client = _client()

    outline_json = outline.model_dump_json(indent=2)
    prompt = f"""
You are ComicCraft's senior comic writer.

Turn this 5-panel outline into a polished comic script.

User:
- Story idea: {request.story_prompt}
- Main character: {request.character_name}
- Setting: {request.setting}
- Tone: {request.tone}
- Art style: {request.art_style}

Outline:
{outline_json}

For every panel produce:
- panel_number
- caption: a short environmental/impact caption
- narration: concise prose describing the action/emotion
- dialogue: natural character dialogue, or an empty string if no dialogue is needed

Keep continuity across all five panels. Make the ending feel complete.
Do not add panels. Do not include markdown.
"""

    response = client.models.generate_content(
        model=settings.gemini_pro_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            response_mime_type="application/json",
            response_schema=StoryResponse,
        ),
    )

    if getattr(response, "parsed", None):
        return response.parsed

    if not response.text:
        raise RuntimeError("Gemini returned an empty story.")

    return StoryResponse.model_validate_json(response.text)
