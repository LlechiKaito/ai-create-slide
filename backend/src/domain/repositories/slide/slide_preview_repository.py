from abc import ABC, abstractmethod

from backend.src.domain.commons.result import Result


class SlidePreviewRepository(ABC):
    @abstractmethod
    def render_preview_images(
        self, deck_title: str, author: str, slides: list[dict],
        color_config: dict | None = None,
    ) -> Result[list[bytes], Exception]:
        pass
