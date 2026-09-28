from pathlib import Path
from typing import List
from app.models import PanelOutline, PanelStory, ComicPanel

def build_comic_layout(outlines: List[PanelOutline], stories: List[PanelStory], image_paths: List[str]) -> List[ComicPanel]:
    story_by_number = {s.panel_number: s for s in stories}
    result = []
    for outline, image_path in zip(outlines, image_paths):
        story = story_by_number.get(outline.panel_number)
        if story is None:
            raise ValueError(f"Missing story for panel {outline.panel_number}.")
        filename = Path(image_path).name
        result.append(ComicPanel(
            panel_number=outline.panel_number,
            title=story.title or outline.title,
            scene_description=story.scene_description or outline.scene_description,
            caption=story.caption,
            narration=story.narration,
            dialogue=story.dialogue,
            image_prompt=outline.image_prompt,
            image_url=f"/static/panels/{filename}",
            image_path=image_path,
        ))
    return result

