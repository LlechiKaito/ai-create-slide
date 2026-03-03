from dataclasses import dataclass

from backend.src.constants.slide import MAX_SLIDES_PER_DECK
from backend.src.domain.entities.slide.slide import Slide
from backend.src.domain.errors.domain_error import DOMAIN_ERRORS, DomainError
from backend.src.domain.value_objects.slide.slide_title import SlideTitle


@dataclass(frozen=True)
class SlideDeck:
    title: SlideTitle
    slides: tuple[Slide, ...]
    author: str = ""

    def __post_init__(self) -> None:
        if len(self.slides) == 0:
            raise DomainError(**DOMAIN_ERRORS["EMPTY_SLIDES"])
        if len(self.slides) > MAX_SLIDES_PER_DECK:
            raise DomainError(**DOMAIN_ERRORS["TOO_MANY_SLIDES"])

    def slide_count(self) -> int:
        return len(self.slides)
