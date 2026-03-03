import pytest

from backend.src.application.errors.application_error import ApplicationError
from backend.src.application.usecases.slide.ai_revise_usecase import AiReviseUseCase
from backend.src.domain.commons.result import Failure, Result, Success, failure, success
from backend.src.domain.repositories.slide.ai_slide_repository import AiSlideRepository


MOCK_CURRENT_CONTENT = {
    "deck_title": "AIの未来",
    "author": "",
    "slides": [
        {
            "title": "はじめに",
            "subtitle": "",
            "content": "AIの概要",
            "bullet_points": ["ポイント1"],
            "image_prompt": "A robot thinking",
        },
    ],
}

MOCK_REVISED_CONTENT = {
    "deck_title": "AIの未来と課題",
    "author": "",
    "slides": [
        {
            "title": "はじめに",
            "subtitle": "改訂版",
            "content": "AIの概要（修正済み）",
            "bullet_points": ["ポイント1", "ポイント2"],
            "image_prompt": "A robot learning from data",
        },
    ],
}

MOCK_IMAGE_BYTES = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"


class MockAiSlideRepository(AiSlideRepository):
    def __init__(self, should_fail: bool = False) -> None:
        self._should_fail = should_fail

    def generate_slide_content(self, theme: str, num_slides: int) -> Result[dict, Exception]:
        return success(MOCK_CURRENT_CONTENT)

    def revise_slide_content(
        self, current_content: dict, revision_instruction: str
    ) -> Result[dict, Exception]:
        if self._should_fail:
            return failure(Exception("AI revision failed"))
        return success(MOCK_REVISED_CONTENT)

    def generate_image(self, prompt: str) -> Result[bytes, Exception]:
        return success(MOCK_IMAGE_BYTES)


class TestAiReviseUseCase:
    def test_should_revise_content_successfully(self) -> None:
        repository = MockAiSlideRepository()
        usecase = AiReviseUseCase(ai_repository=repository)

        result = usecase.execute(
            current_content=MOCK_CURRENT_CONTENT,
            revision_instruction="タイトルを修正してください",
        )

        assert isinstance(result, Success)
        assert result.data["deck_title"] == "AIの未来と課題"

    def test_should_raise_application_error_when_revision_fails(self) -> None:
        repository = MockAiSlideRepository(should_fail=True)
        usecase = AiReviseUseCase(ai_repository=repository)

        with pytest.raises(ApplicationError) as exc_info:
            usecase.execute(
                current_content=MOCK_CURRENT_CONTENT,
                revision_instruction="修正してください",
            )
        assert exc_info.value.code == "AI_REVISION_FAILED"

    def test_should_pass_content_and_instruction_to_repository(self) -> None:
        class CapturingRepository(AiSlideRepository):
            def __init__(self) -> None:
                self.captured_content: dict = {}
                self.captured_instruction = ""

            def generate_slide_content(self, theme: str, num_slides: int) -> Result[dict, Exception]:
                return success({})

            def revise_slide_content(
                self, current_content: dict, revision_instruction: str
            ) -> Result[dict, Exception]:
                self.captured_content = current_content
                self.captured_instruction = revision_instruction
                return success(MOCK_REVISED_CONTENT)

            def generate_image(self, prompt: str) -> Result[bytes, Exception]:
                return success(MOCK_IMAGE_BYTES)

        repository = CapturingRepository()
        usecase = AiReviseUseCase(ai_repository=repository)

        usecase.execute(
            current_content=MOCK_CURRENT_CONTENT,
            revision_instruction="箇条書きを追加",
        )

        assert repository.captured_content == MOCK_CURRENT_CONTENT
        assert repository.captured_instruction == "箇条書きを追加"
