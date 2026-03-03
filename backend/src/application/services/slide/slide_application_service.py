from backend.src.application.dto.slide.slide_dto import GenerateSlidesRequestDto
from backend.src.application.usecases.slide.generate_slide_usecase import (
    GenerateSlideUseCase,
)
from backend.src.domain.commons.result import Result


class SlideApplicationService:
    def __init__(self, generate_slide_usecase: GenerateSlideUseCase) -> None:
        self._generate_slide_usecase = generate_slide_usecase

    def generate_slides(
        self, request: GenerateSlidesRequestDto
    ) -> Result[bytes, Exception]:
        slides_data = [
            {
                "title": slide.title,
                "subtitle": slide.subtitle,
                "content": slide.content,
                "bullet_points": slide.bullet_points,
            }
            for slide in request.slides
        ]

        return self._generate_slide_usecase.execute(
            deck_title=request.deck_title,
            author=request.author,
            slides_data=slides_data,
        )
