from abc import ABC, abstractmethod

from backend.src.domain.commons.result import Result


class AiSlideRepository(ABC):
    @abstractmethod
    def generate_slide_content(self, theme: str, num_slides: int) -> Result[dict, Exception]:
        pass

    @abstractmethod
    def revise_slide_content(
        self, current_content: dict, revision_instruction: str
    ) -> Result[dict, Exception]:
        pass
