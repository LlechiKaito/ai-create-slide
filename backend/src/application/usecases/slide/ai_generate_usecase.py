import base64

from backend.src.application.errors.application_error import (
    APPLICATION_ERRORS,
    ApplicationError,
)
from backend.src.domain.commons.result import Failure, Result, Success, success
from backend.src.domain.repositories.slide.ai_slide_repository import AiSlideRepository


class AiGenerateUseCase:
    def __init__(self, ai_repository: AiSlideRepository) -> None:
        self._ai_repository = ai_repository

    def _generate_images_for_slides(self, slides: list[dict]) -> None:
        for slide in slides:
            image_prompt = slide.get("image_prompt", "")
            if not image_prompt:
                slide["image_data"] = ""
                continue

            result = self._ai_repository.generate_image(image_prompt)
            if isinstance(result, Success):
                slide["image_data"] = base64.b64encode(result.data).decode("utf-8")
            else:
                slide["image_data"] = ""

    def execute(self, theme: str, num_slides: int) -> Result[dict, Exception]:
        result = self._ai_repository.generate_slide_content(theme, num_slides)

        if isinstance(result, Failure):
            raise ApplicationError(**APPLICATION_ERRORS["AI_GENERATION_FAILED"])

        content = result.data
        self._generate_images_for_slides(content.get("slides", []))
        return success(content)
