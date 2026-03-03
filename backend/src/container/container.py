from backend.src.application.services.slide.slide_application_service import (
    SlideApplicationService,
)
from backend.src.application.usecases.slide.ai_generate_usecase import AiGenerateUseCase
from backend.src.application.usecases.slide.ai_revise_usecase import AiReviseUseCase
from backend.src.application.usecases.slide.generate_slide_usecase import (
    GenerateSlideUseCase,
)
from backend.src.application.usecases.slide.preview_images_usecase import (
    PreviewImagesUseCase,
)
from backend.src.infrastructure.external.gemini_client import GeminiAiSlideRepository
from backend.src.infrastructure.repositories.slide.pil_slide_preview_repository import (
    PilSlidePreviewRepository,
)
from backend.src.infrastructure.repositories.slide.pptx_slide_repository import (
    PptxSlideRepository,
)
from backend.src.presentation.controllers.slide.slide_controller import SlideController


def get_slide_controller() -> SlideController:
    pptx_repository = PptxSlideRepository()
    ai_repository = GeminiAiSlideRepository()
    preview_repository = PilSlidePreviewRepository()

    generate_usecase = GenerateSlideUseCase(slide_repository=pptx_repository)
    ai_generate_usecase = AiGenerateUseCase(ai_repository=ai_repository)
    ai_revise_usecase = AiReviseUseCase(ai_repository=ai_repository)
    preview_images_usecase = PreviewImagesUseCase(preview_repository=preview_repository)

    service = SlideApplicationService(
        generate_slide_usecase=generate_usecase,
        ai_generate_usecase=ai_generate_usecase,
        ai_revise_usecase=ai_revise_usecase,
        preview_images_usecase=preview_images_usecase,
    )
    return SlideController(slide_service=service)
