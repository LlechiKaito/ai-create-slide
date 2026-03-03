from fastapi import Response

from backend.src.application.dto.slide.slide_dto import GenerateSlidesRequestDto
from backend.src.application.services.slide.slide_application_service import (
    SlideApplicationService,
)
from backend.src.constants.http import HttpStatus
from backend.src.constants.slide import GENERATED_FILENAME


class SlideController:
    def __init__(self, slide_service: SlideApplicationService) -> None:
        self._slide_service = slide_service

    def generate_slides(self, request: GenerateSlidesRequestDto) -> Response:
        result = self._slide_service.generate_slides(request)

        return Response(
            content=result.data,
            status_code=HttpStatus.OK,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "Content-Disposition": f'attachment; filename="{GENERATED_FILENAME}"'
            },
        )
