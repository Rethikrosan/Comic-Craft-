import logging
import json
import re
from typing import List
from app.config import get_settings
from app.models import PanelOutline

logger = logging.getLogger(__name__)

def _extract_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("Gemini did not return a JSON array.")
    return json.loads(text[start:end + 1])

def _mock_outline(story_prompt, character_name, setting, tone, art_style):
    cleaned = story_prompt.strip()
    sentences = [s.strip() for s in re.split(r'[.!?]+', cleaned) if s.strip()]
    
    s1 = sentences[0] if len(sentences) > 0 else f"{character_name} arrives in {setting}."
    s2 = sentences[1] if len(sentences) > 1 else f"{character_name} discovers a mysterious detail in {setting}."
    s3 = sentences[2] if len(sentences) > 2 else f"{character_name} interacts with the discovery as tension builds."
    s4 = sentences[3] if len(sentences) > 3 else f"A sudden action climax occurs in {setting} involving {character_name}."
    s5 = sentences[4] if len(sentences) > 4 else f"{character_name} completes the adventure in {setting}."

    char_anchor = f"{character_name}, energetic protagonist with expressive outfit"

    panel_configs = [
        ("The Arrival", f"{character_name} enters {setting}. {s1}", f"wide cinematic shot, {character_name} entering {setting}, atmospheric lighting"),
        ("The Discovery", f"Inside {setting}, {character_name} spots a key discovery. {s2}", f"medium shot, {character_name} looking closely at key object, dramatic shadows"),
        ("The Interaction", f"As tension rises in {setting}, {character_name} reacts. {s3}", f"close-up shot, {character_name} interacting with the environment"),
        ("The Climax", f"A major turning point occurs in {setting}. {s4}", f"dynamic action angle, {character_name} reacting to intense event"),
        ("The Outcome", f"The story resolves as {character_name} reflects in {setting}. {s5}", f"heroic concluding shot, {character_name} standing in warm lighting"),
    ]

    return [
        PanelOutline(
            panel_number=i,
            title=title,
            scene_description=desc,
            image_prompt=f"A cinematic comic-book illustration of {char_anchor} in {setting}. Scene: {desc}. Composition: {camera_note}. Tone: {tone}. Art style: {art_style}, detailed background, 8k resolution, no text, no speech bubbles, no watermark"
        )
        for i, (title, desc, camera_note) in enumerate(panel_configs, 1)
    ]

def generate_outline(story_prompt, character_name, setting, tone, art_style) -> List[PanelOutline]:
    settings = get_settings()
    is_mock = settings.image_backend.lower() in {"mock", "demo"}
    is_dummy_key = not settings.gemini_api_key or settings.gemini_api_key.startswith("AQ.") or "your_" in settings.gemini_api_key.lower()

    if is_mock or is_dummy_key:
        return _mock_outline(story_prompt, character_name, setting, tone, art_style)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.gemini_api_key)
        prompt = f"""
You are an expert comic book visual director and AI prompt engineer.
Create exactly {settings.panels} connected comic panels based on this story idea:

Story: {story_prompt}
Main Character: {character_name}
Setting: {setting}
Tone/Mood: {tone}
Art Style: {art_style}

Guidelines:
1. Divide the story into a 5-panel narrative arc:
   - Panel 1: Arrival / Introduction (character arriving or entering setting)
   - Panel 2: Discovery / Inciting Event (character spotting or discovering something important)
   - Panel 3: Interaction / Rising Action (character examining or interacting with environment)
   - Panel 4: Climax / Peak Action (high-stakes action, confrontation, or sudden event)
   - Panel 5: Resolution / Outcome (satisfying conclusion scene)

2. Create a consistent character visual description for {character_name} across all panels.

3. For each panel, generate a detailed `image_prompt` tailored for text-to-image AI generation. The prompt must describe:
   - Visual appearance of {character_name} (clothing, hair, pose)
   - Specific action happening in the scene based on the story
   - Setting background ({setting}), environment details, time of day, and lighting
   - Mood ({tone}) and camera shot type (wide, medium, close-up, dynamic angle)
   - End with: "{art_style} comic illustration style, cinematic lighting, detailed, no text, no speech bubbles, no watermark"

Return ONLY a valid JSON array of exactly {settings.panels} objects with these exact keys:
[
  {{
    "panel_number": 1,
    "title": "Short Panel Title",
    "scene_description": "2-3 sentence description of story events in this panel.",
    "image_prompt": "Detailed AI image generation prompt for this panel."
  }}
]
Do not include markdown commentary.
"""
        response = client.models.generate_content(
            model=settings.gemini_flash_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                response_mime_type="application/json",
            ),
        )
        data = _extract_json(response.text)
        panels = [PanelOutline.model_validate(x) for x in data]
        if len(panels) != settings.panels:
            raise ValueError(f"Expected {settings.panels} panels, received {len(panels)}.")
        return panels
    except Exception as exc:
        logger.warning("Gemini outline generation failed, falling back to mock: %s", exc)
        return _mock_outline(story_prompt, character_name, setting, tone, art_style)


