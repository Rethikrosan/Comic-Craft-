import logging
import re
import uuid
from pathlib import Path
from app.config import get_settings

logger = logging.getLogger(__name__)

def _safe_name(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", text).strip("-").lower()
    return value[:60] or "panel"

def _mock_image(path: Path, prompt: str, panel_number: int = 1):
    from PIL import Image, ImageDraw, ImageFont
    settings = get_settings()
    w, h = settings.image_width, settings.image_height
    
    palettes = [
        ("#1E293B", "#F59E0B", "#FFFFFF"),  # Slate Dark + Gold + White
        ("#2E1065", "#A855F7", "#FFFFFF"),  # Deep Purple + Light Purple + White
        ("#0F172A", "#38BDF8", "#FFFFFF"),  # Midnight Blue + Cyan + White
        ("#450A0A", "#F87171", "#FFFFFF"),  # Deep Crimson + Coral + White
        ("#064E3B", "#34D399", "#FFFFFF"),  # Dark Emerald + Mint + White
    ]
    idx = (panel_number - 1) % len(palettes) if panel_number > 0 else 0
    bg_color, accent_color, text_color = palettes[idx]

    image = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(image)

    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_subtitle = ImageFont.truetype("arial.ttf", 28)
        font_body = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        font_title = ImageFont.load_default(size=36)
        font_subtitle = ImageFont.load_default(size=28)
        font_body = ImageFont.load_default(size=22)

    # Outer comic panel frame
    margin = 20
    draw.rectangle((margin, margin, w - margin, h - margin), outline=accent_color, width=6)
    draw.rectangle((margin + 8, margin + 8, w - margin - 8, h - margin - 8), outline="white", width=2)

    # Top Header Banner
    draw.text((40, 45), "COMICCRAFT", fill=accent_color, font=font_title)
    panel_label = f"PANEL {panel_number}" if panel_number > 0 else "TEST PANEL"
    draw.text((w - 200, 48), panel_label, fill=text_color, font=font_subtitle)

    # Divider line
    draw.line((40, 100, w - 40, 100), fill=accent_color, width=3)

    # Center Graphic Box (Comic Art Placeholder)
    box_top, box_bottom = 120, 480
    draw.rectangle((40, box_top, w - 40, box_bottom), fill="#0F172A", outline=accent_color, width=3)
    draw.line((40, box_top, w - 40, box_bottom), fill=accent_color, width=1)
    draw.line((40, box_bottom, w - 40, box_top), fill=accent_color, width=1)
    
    # Center Badge
    draw.rectangle((80, 260, w - 80, 340), fill=bg_color, outline="white", width=2)
    draw.text((100, 282), f"* {panel_label} ILLUSTRATION *", fill=accent_color, font=font_subtitle)

    # Bottom Prompt Box
    draw.rectangle((40, 500, w - 40, h - 40), fill="#0F172A", outline="white", width=2)
    wrapped_lines = []
    current_line = ""
    for word in prompt.split():
        if len(current_line + " " + word) <= 45:
            current_line += (" " if current_line else "") + word
        else:
            wrapped_lines.append(current_line)
            current_line = word
    if current_line:
        wrapped_lines.append(current_line)

    wrapped_text = "\n".join(wrapped_lines[:6])
    draw.text((55, 515), wrapped_text, fill=text_color, font=font_body, spacing=6)

    image.save(path, format="PNG")

def enhance_prompt(prompt: str) -> str:
    prompt = prompt.strip()
    quality_modifiers = "cinematic lighting, detailed environment, 8k resolution, comic book artwork, masterpiece"
    negative_constraints = "no text, no speech bubbles, no watermark, no logo, no captions"
    if "no text" not in prompt.lower():
        return f"{prompt}, {quality_modifiers}, {negative_constraints}"
    return prompt

def generate_image(image_prompt: str, panel_number: int) -> str:
    settings = get_settings()
    filename = f"{panel_number:02d}-{_safe_name(image_prompt)}-{uuid.uuid4().hex[:8]}.png"
    path = settings.output_dir / filename

    backend = settings.image_backend.lower()

    if backend in {"mock", "demo"}:
        _mock_image(path, image_prompt, panel_number)
        return str(path)

    # Real HF AI Mode
    if not settings.hf_api_key or "your_" in settings.hf_api_key.lower():
        logger.warning("HF_API_KEY is missing in HF mode for panel %d.", panel_number)
        raise ValueError(f"HF_API_KEY is missing for panel {panel_number} in HF mode.")

    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(api_key=settings.hf_api_key)
        final_prompt = enhance_prompt(image_prompt)
        logger.info("Generating HF AI image for Panel %d with prompt: %s", panel_number, final_prompt)
        image = client.text_to_image(
            final_prompt,
            model=settings.hf_image_model,
        )
        if image.size != (settings.image_width, settings.image_height):
            image = image.resize((settings.image_width, settings.image_height))
        image.save(path, format="PNG")
        logger.info("Successfully saved real HF generated image to %s", path)
        return str(path)
    except Exception as exc:
        logger.error("HuggingFace image generation failed for panel %d: %s", panel_number, exc)
        raise RuntimeError(f"HuggingFace image generation failed for panel {panel_number}: {exc}") from exc




