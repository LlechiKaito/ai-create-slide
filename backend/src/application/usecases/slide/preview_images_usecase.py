from backend.src.domain.commons.result import Result
from backend.src.domain.repositories.slide.slide_preview_repository import (
    SlidePreviewRepository,
)


class PreviewImagesUseCase:
    def __init__(self, preview_repository: SlidePreviewRepository) -> None:
        self._preview_repository = preview_repository

    def execute(
        self, deck_title: str, author: str, slides: list[dict]
    ) -> Result[list[bytes], Exception]:
        return self._preview_repository.render_preview_images(
            deck_title=deck_title,
            author=author,
            slides=slides,
        )
