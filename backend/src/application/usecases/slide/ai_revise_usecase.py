import base64
import logging
from concurrent.futures import ThreadPoolExecutor

from backend.src.application.errors.application_error import (
    APPLICATION_ERRORS,
    ApplicationError,
)
from backend.src.domain.commons.result import Failure, Result, Success, success
from backend.src.domain.repositories.slide.ai_slide_repository import AiSlideRepository

logger = logging.getLogger(__name__)


class AiReviseUseCase:
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

    def _generate_images_for_slides(self, slides: list[dict]) -> None:
        with ThreadPoolExecutor() as executor:
            executor.map(self._generate_image_for_slide, slides)

    def _build_old_prompts(self, current_content: dict) -> dict[int, dict[str, str]]:
        old: dict[int, dict[str, str]] = {}
        for i, slide in enumerate(current_content.get("slides", [])):
            old[i] = {
                "image_prompt": slide.get("image_prompt", ""),
                "image_data": slide.get("image_data", ""),
            }
        return old

    def _generate_images_selective(
        self, slides: list[dict], old_prompts: dict[int, dict[str, str]],
    ) -> None:
        needs_generation: list[dict] = []
        for i, slide in enumerate(slides):
            old = old_prompts.get(i)
            new_prompt = slide.get("image_prompt", "")
            if old and old["image_prompt"] == new_prompt and old["image_data"]:
                logger.info("Reusing existing image for slide: %s", slide.get("title", "unknown"))
                slide["image_data"] = old["image_data"]
            else:
                needs_generation.append(slide)

        if needs_generation:
            logger.info("Generating images for %d/%d slides", len(needs_generation), len(slides))
            with ThreadPoolExecutor() as executor:
                executor.map(self._generate_image_for_slide, needs_generation)

    def execute(
        self, current_content: dict, revision_instruction: str,
    ) -> Result[dict, Exception]:
        old_prompts = self._build_old_prompts(current_content)

        result = self._ai_repository.revise_slide_content(
            current_content, revision_instruction,
        )

        if isinstance(result, Failure):
            raise ApplicationError(**APPLICATION_ERRORS["AI_REVISION_FAILED"])

        content = result.data
        self._generate_images_selective(content.get("slides", []), old_prompts)
        return success(content)
