import logging
import json
import re
from typing import List
from app.config import get_settings
from app.models import PanelOutline, PanelStory

logger = logging.getLogger(__name__)

def _extract_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("Gemini did not return a JSON array.")
    return json.loads(text[start:end + 1])

def _mock_story(outlines, character_name, tone):
    return [
        PanelStory(
            panel_number=p.panel_number,
            title=p.title,
            scene_description=p.scene_description,
            caption=f"The story moves forward as {character_name} faces the moment.",
            narration=f"{character_name} takes a careful breath and keeps moving. The {tone.lower()} atmosphere makes every detail feel important.",
            dialogue=f"{character_name}: We have to keep going."
        )
        for p in outlines
    ]

def generate_story(outlines: List[PanelOutline], character_name: str, tone: str) -> List[PanelStory]:
    settings = get_settings()
    is_mock = settings.image_backend.lower() in {"mock", "demo"}
    is_dummy_key = not settings.gemini_api_key or settings.gemini_api_key.startswith("AQ.") or "your_" in settings.gemini_api_key.lower()

    if is_mock or is_dummy_key:
        return _mock_story(outlines, character_name, tone)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.gemini_api_key)
        outline_json = json.dumps([p.model_dump() for p in outlines], ensure_ascii=False)
        prompt = f"""
Expand this {len(outlines)}-panel comic outline into polished comic writing.

Main character: {character_name}
Tone: {tone}
Outline:
{outline_json}

Return ONLY valid JSON array with one object per panel containing:
panel_number, title, scene_description, caption, narration, dialogue.
Keep continuity, character identity, cause-and-effect, and the tone consistent.
Dialogue should be concise and natural. Do not add extra panels.
"""
        response = client.models.generate_content(
            model=settings.gemini_pro_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,
                response_mime_type="application/json",
            ),
        )
        data = _extract_json(response.text)
        stories = [PanelStory.model_validate(x) for x in data]
        if len(stories) != len(outlines):
            raise ValueError("Gemini story response contains the wrong number of panels.")
        return stories
    except Exception as exc:
        logger.warning("Gemini story generation failed, falling back to mock: %s", exc)
        return _mock_story(outlines, character_name, tone)

