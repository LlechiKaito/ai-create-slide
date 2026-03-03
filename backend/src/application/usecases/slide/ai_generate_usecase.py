from backend.src.application.errors.application_error import (
    APPLICATION_ERRORS,
    ApplicationError,
)
from backend.src.domain.commons.result import Failure, Result, success
from backend.src.domain.repositories.slide.ai_slide_repository import AiSlideRepository


class AiGenerateUseCase:
    def __init__(self, ai_repository: AiSlideRepository) -> None:
        self._ai_repository = ai_repository

    def execute(self, theme: str, num_slides: int) -> Result[dict, Exception]:
        result = self._ai_repository.generate_slide_content(theme, num_slides)

        if isinstance(result, Failure):
            raise ApplicationError(**APPLICATION_ERRORS["AI_GENERATION_FAILED"])

        return success(result.data)
