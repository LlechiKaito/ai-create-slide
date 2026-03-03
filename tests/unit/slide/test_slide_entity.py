import pytest

from backend.src.domain.entities.slide.slide import Slide
from backend.src.domain.entities.slide.slide_deck import SlideDeck
from backend.src.domain.errors.domain_error import DomainError
from backend.src.domain.value_objects.slide.slide_content import SlideContent
from backend.src.domain.value_objects.slide.slide_title import SlideTitle


class TestSlideTitle:
    def test_should_create_valid_title(self) -> None:
        title = SlideTitle(value="Test Title")
        assert title.value == "Test Title"

    def test_should_raise_error_when_title_is_empty(self) -> None:
        with pytest.raises(DomainError) as exc_info:
            SlideTitle(value="")
        assert exc_info.value.code == "EMPTY_TITLE"

    def test_should_raise_error_when_title_is_whitespace(self) -> None:
        with pytest.raises(DomainError) as exc_info:
            SlideTitle(value="   ")
        assert exc_info.value.code == "EMPTY_TITLE"

    def test_should_raise_error_when_title_exceeds_max_length(self) -> None:
        with pytest.raises(DomainError) as exc_info:
            SlideTitle(value="a" * 201)
        assert exc_info.value.code == "TITLE_TOO_LONG"


class TestSlideContent:
    def test_should_create_valid_content(self) -> None:
        content = SlideContent(value="Test content")
        assert content.value == "Test content"

    def test_should_allow_empty_content(self) -> None:
        content = SlideContent(value="")
        assert content.value == ""

    def test_should_raise_error_when_content_exceeds_max_length(self) -> None:
        with pytest.raises(DomainError) as exc_info:
            SlideContent(value="a" * 5001)
        assert exc_info.value.code == "CONTENT_TOO_LONG"


class TestSlide:
    def test_should_create_slide_with_required_fields(self) -> None:
        slide = Slide(
            title=SlideTitle(value="Title"),
            content=SlideContent(value="Content"),
        )
        assert slide.title.value == "Title"
        assert slide.content.value == "Content"
        assert slide.subtitle is None
        assert slide.bullet_points == ()

    def test_should_create_slide_with_bullet_points(self) -> None:
        slide = Slide(
            title=SlideTitle(value="Title"),
            content=SlideContent(value=""),
            bullet_points=("Point 1", "Point 2"),
        )
        assert slide.has_bullet_points()
        assert len(slide.bullet_points) == 2

    def test_should_report_no_bullet_points_when_empty(self) -> None:
        slide = Slide(
            title=SlideTitle(value="Title"),
            content=SlideContent(value=""),
        )
        assert not slide.has_bullet_points()


class TestSlideDeck:
    def _make_slide(self, title: str = "Slide") -> Slide:
        return Slide(
            title=SlideTitle(value=title),
            content=SlideContent(value="Content"),
        )

    def test_should_create_valid_slide_deck(self) -> None:
        deck = SlideDeck(
            title=SlideTitle(value="Deck"),
            slides=(self._make_slide(),),
        )
        assert deck.title.value == "Deck"
        assert deck.slide_count() == 1

    def test_should_raise_error_when_slides_empty(self) -> None:
        with pytest.raises(DomainError) as exc_info:
            SlideDeck(
                title=SlideTitle(value="Deck"),
                slides=(),
            )
        assert exc_info.value.code == "EMPTY_SLIDES"

    def test_should_raise_error_when_too_many_slides(self) -> None:
        slides = tuple(self._make_slide(f"Slide {i}") for i in range(21))
        with pytest.raises(DomainError) as exc_info:
            SlideDeck(
                title=SlideTitle(value="Deck"),
                slides=slides,
            )
        assert exc_info.value.code == "TOO_MANY_SLIDES"

    def test_should_accept_max_slides(self) -> None:
        slides = tuple(self._make_slide(f"Slide {i}") for i in range(20))
        deck = SlideDeck(
            title=SlideTitle(value="Deck"),
            slides=slides,
        )
        assert deck.slide_count() == 20
