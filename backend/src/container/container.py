from backend.src.application.services.slide.slide_application_service import (
    SlideApplicationService,
)
from backend.src.application.usecases.slide.generate_slide_usecase import (
    GenerateSlideUseCase,
)
from backend.src.infrastructure.repositories.slide.pptx_slide_repository import (
    PptxSlideRepository,
)
from backend.src.presentation.controllers.slide.slide_controller import SlideController


def get_slide_controller() -> SlideController:
    repository = PptxSlideRepository()
    usecase = GenerateSlideUseCase(slide_repository=repository)
    service = SlideApplicationService(generate_slide_usecase=usecase)
    return SlideController(slide_service=service)
