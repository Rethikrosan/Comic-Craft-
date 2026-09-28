from pathlib import Path
from uuid import uuid4

from app.schemas import PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import image_generator
from app.services.layout_builder import build_comic_layout


def generate_comic(request: PromptRequest) -> dict:
    outline = generate_outline(request)
    story = generate_story(request, outline)

    image_paths: list[str] = []
    for panel in outline.panels:
        unique_hint = f"panel-{panel.panel_number}-{uuid4().hex[:8]}"
        image_paths.append(
            image_generator.generate(panel.image_prompt, filename_hint=unique_hint)
        )

    layout = build_comic_layout(outline, story, image_paths)
    pdf_path = save_pdf(layout, request.character_name)

    public_layout = []
    for item in layout:
        public_item = dict(item)
        public_item["image_path"] = (
            f"/static/panels/{Path(item['image_path']).name}"
        )
        public_layout.append(public_item)

    pdf_name = Path(pdf_path).name

    return {
        "request": request.model_dump(),
        "layout": public_layout,
        "pdf_path": f"/exports/{pdf_name}",
        "pdf_filename": pdf_name,
    }
