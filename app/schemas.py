from typing import Literal

from pydantic import BaseModel, Field, field_validator

Tone = Literal["light-hearted", "dramatic", "poetic", "funny"]
ArtStyle = Literal["anime", "pixel art", "comic book", "realistic"]


class PromptRequest(BaseModel):
    story_prompt: str = Field(..., min_length=10, max_length=2000)
    character_name: str = Field(..., min_length=1, max_length=80)
    setting: str = Field(..., min_length=1, max_length=120)
    tone: Tone = "light-hearted"
    art_style: ArtStyle = "comic book"

    @field_validator("story_prompt", "character_name", "setting")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value


class PanelOutline(BaseModel):
    panel_number: int = Field(..., ge=1, le=5)
    title: str = Field(..., min_length=1, max_length=120)
    scene_description: str = Field(..., min_length=1, max_length=1000)
    image_prompt: str = Field(..., min_length=1, max_length=1500)


class OutlineResponse(BaseModel):
    panels: list[PanelOutline] = Field(..., min_length=5, max_length=5)


class StoryPanel(BaseModel):
    panel_number: int = Field(..., ge=1, le=5)
    caption: str = Field(default="", max_length=500)
    narration: str = Field(..., min_length=1, max_length=1500)
    dialogue: str = Field(default="", max_length=1000)


class StoryResponse(BaseModel):
    panels: list[StoryPanel] = Field(..., min_length=5, max_length=5)
