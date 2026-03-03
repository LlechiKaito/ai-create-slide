import pytest

from backend.src.application.errors.application_error import ApplicationError
from backend.src.application.usecases.slide.ai_generate_usecase import AiGenerateUseCase
from backend.src.domain.commons.result import Failure, Result, Success, failure, success
from backend.src.domain.repositories.slide.ai_slide_repository import AiSlideRepository


MOCK_GENERATED_CONTENT = {
    "deck_title": "AIの未来",
    "author": "",
    "slides": [
        {
            "title": "はじめに",
            "subtitle": "",
            "content": "AIの概要",
            "bullet_points": ["ポイント1", "ポイント2"],
            "image_prompt": "A robot thinking about AI",
        },
    ],
}

MOCK_IMAGE_BYTES = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"


class MockAiSlideRepository(AiSlideRepository):
    def __init__(self, should_fail: bool = False) -> None:
        self._should_fail = should_fail

    def generate_slide_content(self, theme: str, num_slides: int) -> Result[dict, Exception]:
        if self._should_fail:
            return failure(Exception("AI generation failed"))
        return success(MOCK_GENERATED_CONTENT)

    def revise_slide_content(
        self, current_content: dict, revision_instruction: str
    ) -> Result[dict, Exception]:
        return success(current_content)

    def generate_image(self, prompt: str) -> Result[bytes, Exception]:
        return success(MOCK_IMAGE_BYTES)


class TestAiGenerateUseCase:
    def test_should_generate_content_successfully(self) -> None:
        repository = MockAiSlideRepository()
        usecase = AiGenerateUseCase(ai_repository=repository)

        result = usecase.execute(theme="AIの未来", num_slides=5)

        assert isinstance(result, Success)
        assert result.data["deck_title"] == "AIの未来"
        assert len(result.data["slides"]) == 1
        assert result.data["slides"][0]["image_data"] != ""

    def test_should_raise_application_error_when_generation_fails(self) -> None:
        repository = MockAiSlideRepository(should_fail=True)
        usecase = AiGenerateUseCase(ai_repository=repository)

        with pytest.raises(ApplicationError) as exc_info:
            usecase.execute(theme="AIの未来", num_slides=5)
        assert exc_info.value.code == "AI_GENERATION_FAILED"

    def test_should_pass_theme_and_num_slides_to_repository(self) -> None:
        class CapturingRepository(AiSlideRepository):
            def __init__(self) -> None:
                self.captured_theme = ""
                self.captured_num_slides = 0

            def generate_slide_content(self, theme: str, num_slides: int) -> Result[dict, Exception]:
                self.captured_theme = theme
                self.captured_num_slides = num_slides
                return success(MOCK_GENERATED_CONTENT)

            def revise_slide_content(
                self, current_content: dict, revision_instruction: str
            ) -> Result[dict, Exception]:
                return success(current_content)

            def generate_image(self, prompt: str) -> Result[bytes, Exception]:
                return success(MOCK_IMAGE_BYTES)

        repository = CapturingRepository()
        usecase = AiGenerateUseCase(ai_repository=repository)

        usecase.execute(theme="テスト", num_slides=3)

        assert repository.captured_theme == "テスト"
        assert repository.captured_num_slides == 3
