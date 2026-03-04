import json
import logging
import os

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

from backend.src.application.errors.application_error import (
    APPLICATION_ERRORS,
    ApplicationError,
)
from backend.src.constants.prompts import (
    BASE_REVISE_PROMPT,
    BASE_SYSTEM_PROMPT,
    CATEGORY_CONTEXT,
    REVISE_SINGLE_SLIDE_PROMPT,
)
from backend.src.constants.slide import DEFAULT_CATEGORY, GEMINI_MODEL_NAME, IMAGEN_MODEL_NAME
from backend.src.domain.commons.result import Result, failure, success
from backend.src.domain.repositories.slide.ai_slide_repository import AiSlideRepository


def _strip_image_data(data: dict | list) -> dict | list:
    if isinstance(data, list):
        return [_strip_image_data(item) if isinstance(item, dict) else item for item in data]
    stripped = {}
    for k, v in data.items():
        if k == "image_data":
            continue
        if isinstance(v, dict):
            stripped[k] = _strip_image_data(v)
        elif isinstance(v, list):
            stripped[k] = _strip_image_data(v)
        else:
            stripped[k] = v
    return stripped


class GeminiAiSlideRepository(AiSlideRepository):
    def _get_client(self) -> genai.Client:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            raise ApplicationError(**APPLICATION_ERRORS["GEMINI_API_KEY_NOT_SET"])
        return genai.Client(api_key=api_key)

    def _parse_json_response(self, text: str) -> dict:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)
        return json.loads(cleaned)

    def generate_slide_content(
        self, theme: str, num_slides: int, category: str = DEFAULT_CATEGORY
    ) -> Result[dict, Exception]:
        client = self._get_client()

        context = CATEGORY_CONTEXT.get(category, CATEGORY_CONTEXT[DEFAULT_CATEGORY])
        system_prompt = BASE_SYSTEM_PROMPT.format(category_context=context)
        user_message = f"テーマ: {theme}\nスライド枚数: {num_slides}枚"

        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=[
                {"role": "user", "parts": [{"text": system_prompt + "\n\n" + user_message}]},
            ],
        )

        parsed = self._parse_json_response(response.text)
        return success(parsed)

    def revise_slide_content(
        self, current_content: dict, revision_instruction: str
    ) -> Result[dict, Exception]:
        client = self._get_client()

        current_json = json.dumps(_strip_image_data(current_content), ensure_ascii=False, indent=2)
        user_message = (
            f"現在のスライド内容:\n{current_json}\n\n"
            f"修正指示: {revision_instruction}"
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=[
                {"role": "user", "parts": [{"text": BASE_REVISE_PROMPT + "\n\n" + user_message}]},
            ],
        )

        parsed = self._parse_json_response(response.text)
        return success(parsed)

    def revise_single_slide(
        self, current_slide: dict, revision_instruction: str
    ) -> Result[dict, Exception]:
        client = self._get_client()

        current_json = json.dumps(_strip_image_data(current_slide), ensure_ascii=False, indent=2)
        user_message = (
            f"現在のスライド内容:\n{current_json}\n\n"
            f"修正指示: {revision_instruction}"
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=[
                {"role": "user", "parts": [{"text": REVISE_SINGLE_SLIDE_PROMPT + "\n\n" + user_message}]},
            ],
        )

        parsed = self._parse_json_response(response.text)
        return success(parsed)

    def generate_image(self, prompt: str) -> Result[bytes, Exception]:
        logger.info("Imagen API call start: model=%s, prompt=%s", IMAGEN_MODEL_NAME, prompt[:80])
        try:
            client = self._get_client()
            response = client.models.generate_images(
                model=IMAGEN_MODEL_NAME,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    safety_filter_level="BLOCK_LOW_AND_ABOVE",
                ),
            )
        except Exception as e:
            logger.error("Imagen API exception: %s: %s", type(e).__name__, e)
            return failure(e)

        if not response.generated_images:
            logger.warning("Imagen API returned no images for prompt: %s", prompt[:80])
            return failure(Exception("No image generated"))

        image_bytes = response.generated_images[0].image.image_bytes
        logger.info("Imagen API success: %d bytes", len(image_bytes))
        return success(image_bytes)
