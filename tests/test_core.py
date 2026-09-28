from pathlib import Path

from app.schemas import PromptRequest, OutlineResponse, PanelOutline, StoryResponse, StoryPanel
from app.services.layout_builder import build_comic_layout


def test_prompt_request_validation():
    request = PromptRequest(
        story_prompt="A fox discovers a magical portal.",
        character_name="Luna",
        setting="Enchanted forest",
        tone="funny",
        art_style="comic book",
    )
    assert request.character_name == "Luna"


def test_layout_builder():
    outline = OutlineResponse(
        panels=[
            PanelOutline(
                panel_number=i,
                title=f"Panel {i}",
                scene_description="Scene",
                image_prompt="Image",
            )
            for i in range(1, 6)
        ]
    )
    story = StoryResponse(
        panels=[
            StoryPanel(
                panel_number=i,
                caption="Caption",
                narration="Narration",
                dialogue="Hello",
            )
            for i in range(1, 6)
        ]
    )
    images = [f"/tmp/panel-{i}.png" for i in range(1, 6)]

    layout = build_comic_layout(outline, story, images)

    assert len(layout) == 5
    assert layout[0]["panel_number"] == 1
    assert layout[-1]["image_path"].endswith("5.png")
