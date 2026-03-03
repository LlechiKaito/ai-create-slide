from abc import ABC, abstractmethod

from backend.src.domain.commons.result import Result
from backend.src.domain.entities.slide.slide_deck import SlideDeck


class SlideRepository(ABC):
    @abstractmethod
    def generate_pptx(self, slide_deck: SlideDeck) -> Result[bytes, Exception]:
        pass
