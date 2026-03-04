from backend.src.application.dto.slide.slide_dto import (
    AiGenerateRequestDto,
    AiReviseRequestDto,
    AiReviseSlideRequestDto,
    GenerateSlidesRequestDto,
    PreviewImagesRequestDto,
)
from backend.src.application.usecases.slide.ai_generate_usecase import AiGenerateUseCase
from backend.src.application.usecases.slide.ai_revise_slide_usecase import (
    AiReviseSlideUseCase,
)
from backend.src.application.usecases.slide.ai_revise_usecase import AiReviseUseCase
from backend.src.application.usecases.slide.generate_slide_usecase import (
    GenerateSlideUseCase,
)
from backend.src.application.usecases.slide.preview_images_usecase import (
    PreviewImagesUseCase,
)
from backend.src.domain.commons.result import Result


class SlideApplicationService:
    def __init__(
        self,
        generate_slide_usecase: GenerateSlideUseCase,
        ai_generate_usecase: AiGenerateUseCase,
        ai_revise_usecase: AiReviseUseCase,
        ai_revise_slide_usecase: AiReviseSlideUseCase,
        preview_images_usecase: PreviewImagesUseCase,
    ) -> None:
        self._generate_slide_usecase = generate_slide_usecase
        self._ai_generate_usecase = ai_generate_usecase
        self._ai_revise_usecase = ai_revise_usecase
        self._ai_revise_slide_usecase = ai_revise_slide_usecase
        self._preview_images_usecase = preview_images_usecase

    def generate_slides(
        self, request: GenerateSlidesRequestDto
    ) -> Result[bytes, Exception]:
        slides_data = [
            {
                "title": slide.title,
                "subtitle": slide.subtitle,
                "content": slide.content,
                "bullet_points": slide.bullet_points,
                "image_data": slide.image_data,
                "chart_data": slide.chart_data.model_dump() if slide.chart_data else None,
            }
            for slide in request.slides
        ]

        return self._generate_slide_usecase.execute(
            deck_title=request.deck_title,
            author=request.author,
            slides_data=slides_data,
            color_config=request.color_config.model_dump(),
        )

    def ai_generate(self, request: AiGenerateRequestDto) -> Result[dict, Exception]:
        return self._ai_generate_usecase.execute(
            theme=request.theme,
            num_slides=request.num_slides,
            category=request.category,
        )

    def ai_revise(self, request: AiReviseRequestDto) -> Result[dict, Exception]:
        current_dict = request.current_content.model_dump()
        return self._ai_revise_usecase.execute(
            current_content=current_dict,
            revision_instruction=request.revision_instruction,
        )

    def ai_revise_slide(self, request: AiReviseSlideRequestDto) -> Result[dict, Exception]:
        current_slide_dict = request.current_slide.model_dump()
        return self._ai_revise_slide_usecase.execute(
            current_slide=current_slide_dict,
            revision_instruction=request.revision_instruction,
        )

    def preview_images(
        self, request: PreviewImagesRequestDto
    ) -> Result[list[bytes], Exception]:
        slides_data = [s.model_dump() for s in request.slides]
        return self._preview_images_usecase.execute(
            deck_title=request.deck_title,
            author=request.author,
            slides=slides_data,
            color_config=request.color_config.model_dump(),
        )
