from abc import ABC, abstractmethod

from backend.src.domain.commons.result import Result


class SlidePreviewRepository(ABC):
    @abstractmethod
    def render_preview_images(
        self, deck_title: str, author: str, slides: list[dict]
    ) -> Result[list[bytes], Exception]:
        pass
