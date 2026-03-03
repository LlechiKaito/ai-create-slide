from backend.src.application.errors.application_error import (
    APPLICATION_ERRORS,
    ApplicationError,
)
from backend.src.domain.commons.result import Failure, Result, success
from backend.src.domain.repositories.slide.ai_slide_repository import AiSlideRepository


class AiReviseUseCase:
    def __init__(self, ai_repository: AiSlideRepository) -> None:
        self._ai_repository = ai_repository

    def execute(
        self, current_content: dict, revision_instruction: str
    ) -> Result[dict, Exception]:
        result = self._ai_repository.revise_slide_content(
            current_content, revision_instruction
        )

        if isinstance(result, Failure):
            raise ApplicationError(**APPLICATION_ERRORS["AI_REVISION_FAILED"])

        return success(result.data)
