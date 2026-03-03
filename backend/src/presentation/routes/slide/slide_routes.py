from fastapi import APIRouter, Response

from backend.src.application.dto.slide.slide_dto import GenerateSlidesRequestDto
from backend.src.container.container import get_slide_controller


def create_slide_router() -> APIRouter:
    router = APIRouter(prefix="/api/slides", tags=["slides"])

    @router.post("/generate")
    def generate_slides(request: GenerateSlidesRequestDto) -> Response:
        controller = get_slide_controller()
        return controller.generate_slides(request)

    return router
