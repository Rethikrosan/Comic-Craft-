from app.schemas import OutlineResponse, StoryResponse


def build_comic_layout(
    outline: OutlineResponse,
    story: StoryResponse,
    image_paths: list[str],
) -> list[dict]:
    story_by_number = {panel.panel_number: panel for panel in story.panels}

    layout = []
    for index, panel in enumerate(outline.panels):
        story_panel = story_by_number.get(panel.panel_number)
        if not story_panel:
            raise ValueError(f"Missing story content for panel {panel.panel_number}.")

        layout.append(
            {
                "panel_number": panel.panel_number,
                "title": panel.title,
                "scene_description": panel.scene_description,
                "image_prompt": panel.image_prompt,
                "image_path": image_paths[index],
                "caption": story_panel.caption,
                "narration": story_panel.narration,
                "dialogue": story_panel.dialogue,
            }
        )
    return layout
