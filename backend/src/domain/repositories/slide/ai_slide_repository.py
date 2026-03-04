from abc import ABC, abstractmethod

from backend.src.constants.slide import DEFAULT_CATEGORY
from backend.src.domain.commons.result import Result


class AiSlideRepository(ABC):
    @abstractmethod
    def generate_slide_content(
        self, theme: str, num_slides: int, category: str = DEFAULT_CATEGORY,
    ) -> Result[dict, Exception]:
        pass

    @abstractmethod
    def revise_slide_content(
        self, current_content: dict, revision_instruction: str,
    ) -> Result[dict, Exception]:
        pass

    @abstractmethod
    def revise_single_slide(
        self, current_slide: dict, revision_instruction: str,
    ) -> Result[dict, Exception]:
        pass

    @abstractmethod
    def generate_image(self, prompt: str) -> Result[bytes, Exception]:
        pass
