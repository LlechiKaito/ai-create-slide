from pydantic import BaseModel, Field

from backend.src.constants.slide import (
    MAX_BULLET_POINTS_PER_SLIDE,
    MAX_CONTENT_LENGTH,
    MAX_SLIDES_PER_DECK,
    MAX_TITLE_LENGTH,
)


class SlideRequestDto(BaseModel):
    title: str = Field(..., min_length=1, max_length=MAX_TITLE_LENGTH)
    subtitle: str = Field(default="", max_length=MAX_TITLE_LENGTH)
    content: str = Field(default="", max_length=MAX_CONTENT_LENGTH)
    bullet_points: list[str] = Field(
        default_factory=list, max_length=MAX_BULLET_POINTS_PER_SLIDE
    )


class GenerateSlidesRequestDto(BaseModel):
    deck_title: str = Field(..., min_length=1, max_length=MAX_TITLE_LENGTH)
    author: str = Field(default="", max_length=MAX_TITLE_LENGTH)
    slides: list[SlideRequestDto] = Field(
        ..., min_length=1, max_length=MAX_SLIDES_PER_DECK
    )


class GenerateSlidesResponseDto(BaseModel):
    is_success: bool
    message: str
    filename: str


class AiGenerateRequestDto(BaseModel):
    theme: str = Field(..., min_length=1, max_length=MAX_CONTENT_LENGTH)
    num_slides: int = Field(default=5, ge=1, le=MAX_SLIDES_PER_DECK)


class AiSlideContentDto(BaseModel):
    title: str
    subtitle: str = ""
    content: str = ""
    bullet_points: list[str] = Field(default_factory=list)


class AiGenerateResponseDto(BaseModel):
    is_success: bool
    deck_title: str
    author: str = ""
    slides: list[AiSlideContentDto]


class AiReviseRequestDto(BaseModel):
    current_content: AiGenerateResponseDto
    revision_instruction: str = Field(..., min_length=1, max_length=MAX_CONTENT_LENGTH)


class PreviewImagesRequestDto(BaseModel):
    deck_title: str = Field(..., min_length=1, max_length=MAX_TITLE_LENGTH)
    author: str = Field(default="", max_length=MAX_TITLE_LENGTH)
    slides: list[AiSlideContentDto] = Field(
        ..., min_length=1, max_length=MAX_SLIDES_PER_DECK
    )
