from backend.src.application.errors.application_error import (
    APPLICATION_ERRORS,
    ApplicationError,
)
from backend.src.domain.commons.result import Failure, Result, success
from backend.src.domain.entities.slide.slide import Slide
from backend.src.domain.entities.slide.slide_deck import SlideDeck
from backend.src.domain.repositories.slide.slide_repository import SlideRepository
from backend.src.domain.value_objects.slide.slide_content import SlideContent
from backend.src.domain.value_objects.slide.slide_title import SlideTitle


class GenerateSlideUseCase:
    def __init__(self, slide_repository: SlideRepository) -> None:
        self._slide_repository = slide_repository

    def execute(
        self,
        deck_title: str,
        author: str,
        slides_data: list[dict],
        color_config: dict | None = None,
    ) -> Result[bytes, Exception]:
        slides = tuple(
            Slide(
                title=SlideTitle(value=s["title"]),
                content=SlideContent(value=s.get("content", "")),
                subtitle=s.get("subtitle"),
                bullet_points=tuple(s.get("bullet_points", [])),
                image_data=s.get("image_data"),
                chart_data=s.get("chart_data"),
            )
            for s in slides_data
        )

        slide_deck = SlideDeck(
            title=SlideTitle(value=deck_title),
            slides=slides,
            author=author,
        )

        result = self._slide_repository.generate_pptx(slide_deck, color_config)

        if isinstance(result, Failure):
            raise ApplicationError(**APPLICATION_ERRORS["SLIDE_GENERATION_FAILED"])

        return success(result.data)
