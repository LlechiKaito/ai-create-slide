import base64
import logging

from backend.src.application.errors.application_error import (
    APPLICATION_ERRORS,
    ApplicationError,
)
from backend.src.domain.commons.result import Failure, Result, Success, success
from backend.src.domain.repositories.slide.ai_slide_repository import AiSlideRepository

logger = logging.getLogger(__name__)


class AiReviseSlideUseCase:
    def __init__(self, ai_repository: AiSlideRepository) -> None:
        self._ai_repository = ai_repository

    def _generate_image_for_slide(self, slide: dict) -> None:
        image_prompt = slide.get("image_prompt", "")
        if not image_prompt:
            logger.warning("No image_prompt in slide: %s", slide.get("title", "unknown"))
            slide["image_data"] = ""
            return

        logger.info("Generating image for slide: %s", slide.get("title", "unknown"))
        result = self._ai_repository.generate_image(image_prompt)
        if isinstance(result, Success):
            encoded = base64.b64encode(result.data).decode("utf-8")
            logger.info("Image encoded: %d chars for slide: %s", len(encoded), slide.get("title", "unknown"))
            slide["image_data"] = encoded
        else:
            logger.error("Image generation failed for slide '%s': %s", slide.get("title", "unknown"), result.error)
            slide["image_data"] = ""

    def execute(
        self, current_slide: dict, revision_instruction: str,
    ) -> Result[dict, Exception]:
        result = self._ai_repository.revise_single_slide(
            current_slide, revision_instruction,
        )

        if isinstance(result, Failure):
            raise ApplicationError(**APPLICATION_ERRORS["AI_REVISION_FAILED"])

        revised_slide = result.data
        self._generate_image_for_slide(revised_slide)
        return success(revised_slide)
