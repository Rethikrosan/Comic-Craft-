from google import genai
from google.genai import types

from app.config import settings
from app.schemas import OutlineResponse, PromptRequest


def _client() -> genai.Client:
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Add it to .env before generating a comic."
        )
    return genai.Client(api_key=settings.gemini_api_key)


def generate_outline(request: PromptRequest) -> OutlineResponse:
    client = _client()

    prompt = f"""
You are the outline director for ComicCraft, a 5-panel comic generator.

Create exactly 5 sequential comic panels from these user requirements:
- Story idea: {request.story_prompt}
- Main character: {request.character_name}
- Setting: {request.setting}
- Tone: {request.tone}
- Art style: {request.art_style}

Requirements:
1. The five panels must form one coherent beginning-to-ending story.
2. Keep the named character visually consistent.
3. Give each panel a concise title and scene description.
4. Write an image-generation prompt for each panel.
5. Image prompts must describe composition, character appearance, action,
   environment, lighting, camera framing, and the requested art style.
6. Do not put dialogue text inside the generated image prompt.
7. Avoid references to living artists.
8. Return exactly five panels numbered 1 through 5.
"""

    response = client.models.generate_content(
        model=settings.gemini_flash_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            response_mime_type="application/json",
            response_schema=OutlineResponse,
        ),
    )

    if getattr(response, "parsed", None):
        return response.parsed

    if not response.text:
        raise RuntimeError("Gemini returned an empty outline.")

    return OutlineResponse.model_validate_json(response.text)
