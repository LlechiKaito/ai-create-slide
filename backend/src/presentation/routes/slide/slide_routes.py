from fastapi import APIRouter, Response

from backend.src.application.dto.slide.slide_dto import (
    AiGenerateRequestDto,
    AiReviseRequestDto,
    AiReviseSlideRequestDto,
    GenerateSlidesRequestDto,
    PreviewImagesRequestDto,
)
from backend.src.container.container import get_slide_controller


def create_slide_router() -> APIRouter:
    router = APIRouter(prefix="/api/slides", tags=["slides"])

    @router.post("/generate")
    def generate_slides(request: GenerateSlidesRequestDto) -> Response:
        controller = get_slide_controller()
        return controller.generate_slides(request)

    @router.post("/ai-generate")
    def ai_generate(request: AiGenerateRequestDto) -> dict:
        controller = get_slide_controller()
        return controller.ai_generate(request)

    @router.post("/ai-revise")
    def ai_revise(request: AiReviseRequestDto) -> dict:
        controller = get_slide_controller()
        return controller.ai_revise(request)

    @router.post("/ai-revise-slide")
    def ai_revise_slide(request: AiReviseSlideRequestDto) -> dict:
        controller = get_slide_controller()
        return controller.ai_revise_slide(request)

    @router.post("/preview-images")
    def preview_images(request: PreviewImagesRequestDto) -> dict:
        controller = get_slide_controller()
        return controller.preview_images(request)

    return router
