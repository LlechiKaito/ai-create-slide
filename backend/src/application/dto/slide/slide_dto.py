from pydantic import BaseModel, Field

from backend.src.constants.slide import (
    DEFAULT_CATEGORY,
    MAX_BULLET_POINTS_PER_SLIDE,
    MAX_CONTENT_LENGTH,
    MAX_SLIDES_PER_DECK,
    MAX_TITLE_LENGTH,
)


class ColorConfigDto(BaseModel):
    accent: str = Field(default="#F08228")
    text: str = Field(default="#323232")
    background: str = Field(default="#FFFFFF")


class ChartSeriesDto(BaseModel):
    name: str = ""
    values: list[float] = Field(default_factory=list)


class ChartDataDto(BaseModel):
    chart_type: str = Field(default="column")
    title: str = ""
    categories: list[str] = Field(default_factory=list)
    series: list[ChartSeriesDto] = Field(default_factory=list)


class SlideRequestDto(BaseModel):
    title: str = Field(..., min_length=1, max_length=MAX_TITLE_LENGTH)
    subtitle: str = Field(default="", max_length=MAX_TITLE_LENGTH)
    content: str = Field(default="", max_length=MAX_CONTENT_LENGTH)
    bullet_points: list[str] = Field(
        default_factory=list, max_length=MAX_BULLET_POINTS_PER_SLIDE
    )
    image_data: str = ""
    chart_data: ChartDataDto | None = None


class GenerateSlidesRequestDto(BaseModel):
    deck_title: str = Field(..., min_length=1, max_length=MAX_TITLE_LENGTH)
    author: str = Field(default="", max_length=MAX_TITLE_LENGTH)
    slides: list[SlideRequestDto] = Field(
        ..., min_length=1, max_length=MAX_SLIDES_PER_DECK
    )
    color_config: ColorConfigDto = Field(default_factory=ColorConfigDto)


class GenerateSlidesResponseDto(BaseModel):
    is_success: bool
    message: str
    filename: str


class AiGenerateRequestDto(BaseModel):
    theme: str = Field(..., min_length=1, max_length=MAX_CONTENT_LENGTH)
    num_slides: int = Field(default=5, ge=1, le=MAX_SLIDES_PER_DECK)
    category: str = Field(default=DEFAULT_CATEGORY)
    color_config: ColorConfigDto = Field(default_factory=ColorConfigDto)


class AiSlideContentDto(BaseModel):
    title: str
    subtitle: str = ""
    content: str = ""
    bullet_points: list[str] = Field(default_factory=list)
    image_prompt: str = ""
    image_data: str = ""
    chart_data: ChartDataDto | None = None


class AiGenerateResponseDto(BaseModel):
    is_success: bool
    deck_title: str
    author: str = ""
    slides: list[AiSlideContentDto]


class AiReviseRequestDto(BaseModel):
    current_content: AiGenerateResponseDto
    revision_instruction: str = Field(..., min_length=1, max_length=MAX_CONTENT_LENGTH)
    color_config: ColorConfigDto = Field(default_factory=ColorConfigDto)


class AiReviseSlideRequestDto(BaseModel):
    slide_index: int = Field(..., ge=0)
    current_slide: AiSlideContentDto
    revision_instruction: str = Field(..., min_length=1, max_length=MAX_CONTENT_LENGTH)


class PreviewImagesRequestDto(BaseModel):
    deck_title: str = Field(..., min_length=1, max_length=MAX_TITLE_LENGTH)
    author: str = Field(default="", max_length=MAX_TITLE_LENGTH)
    slides: list[AiSlideContentDto] = Field(
        ..., min_length=1, max_length=MAX_SLIDES_PER_DECK
    )
    color_config: ColorConfigDto = Field(default_factory=ColorConfigDto)
