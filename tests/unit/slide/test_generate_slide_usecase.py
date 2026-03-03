import pytest

from backend.src.application.errors.application_error import ApplicationError
from backend.src.application.usecases.slide.generate_slide_usecase import (
    GenerateSlideUseCase,
)
from backend.src.domain.commons.result import Failure, Success, failure, success
from backend.src.domain.entities.slide.slide_deck import SlideDeck
from backend.src.domain.errors.domain_error import DomainError
from backend.src.domain.repositories.slide.slide_repository import SlideRepository


class MockSlideRepository(SlideRepository):
    def __init__(self, should_fail: bool = False) -> None:
        self._should_fail = should_fail

    def generate_pptx(self, slide_deck: SlideDeck) -> Success | Failure:
        if self._should_fail:
            return failure(Exception("Generation failed"))
        return success(b"fake-pptx-bytes")


class TestGenerateSlideUseCase:
    def test_should_generate_slides_successfully(self) -> None:
        repository = MockSlideRepository()
        usecase = GenerateSlideUseCase(slide_repository=repository)

        result = usecase.execute(
            deck_title="Test Deck",
            author="Author",
            slides_data=[
                {"title": "Slide 1", "content": "Content 1"},
            ],
        )

        assert isinstance(result, Success)
        assert result.data == b"fake-pptx-bytes"

    def test_should_raise_application_error_when_generation_fails(self) -> None:
        repository = MockSlideRepository(should_fail=True)
        usecase = GenerateSlideUseCase(slide_repository=repository)

        with pytest.raises(ApplicationError) as exc_info:
            usecase.execute(
                deck_title="Test Deck",
                author="Author",
                slides_data=[
                    {"title": "Slide 1", "content": "Content 1"},
                ],
            )
        assert exc_info.value.code == "SLIDE_GENERATION_FAILED"

    def test_should_raise_domain_error_when_title_empty(self) -> None:
        repository = MockSlideRepository()
        usecase = GenerateSlideUseCase(slide_repository=repository)

        with pytest.raises(DomainError) as exc_info:
            usecase.execute(
                deck_title="",
                author="Author",
                slides_data=[
                    {"title": "Slide 1", "content": "Content 1"},
                ],
            )
        assert exc_info.value.code == "EMPTY_TITLE"

    def test_should_handle_multiple_slides(self) -> None:
        repository = MockSlideRepository()
        usecase = GenerateSlideUseCase(slide_repository=repository)

        result = usecase.execute(
            deck_title="Test Deck",
            author="Author",
            slides_data=[
                {"title": "Slide 1", "content": "Content 1"},
                {
                    "title": "Slide 2",
                    "content": "",
                    "bullet_points": ["Point A", "Point B"],
                },
                {"title": "Slide 3", "subtitle": "Sub", "content": "Content 3"},
            ],
        )

        assert isinstance(result, Success)

    def test_should_handle_slides_with_bullet_points(self) -> None:
        repository = MockSlideRepository()
        usecase = GenerateSlideUseCase(slide_repository=repository)

        result = usecase.execute(
            deck_title="Test Deck",
            author="",
            slides_data=[
                {
                    "title": "Bullets",
                    "content": "",
                    "bullet_points": ["A", "B", "C"],
                },
            ],
        )

        assert isinstance(result, Success)
