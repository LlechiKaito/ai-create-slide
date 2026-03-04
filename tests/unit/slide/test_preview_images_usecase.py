from backend.src.application.usecases.slide.preview_images_usecase import (
    PreviewImagesUseCase,
)
from backend.src.domain.commons.result import Result, Success, success
from backend.src.domain.repositories.slide.slide_preview_repository import (
    SlidePreviewRepository,
)


MOCK_SLIDES = [
    {
        "title": "はじめに",
        "subtitle": "",
        "content": "AIの概要",
        "bullet_points": ["ポイント1", "ポイント2"],
    },
    {
        "title": "まとめ",
        "subtitle": "",
        "content": "結論",
        "bullet_points": [],
    },
]


class MockSlidePreviewRepository(SlidePreviewRepository):
    def __init__(self) -> None:
        self.captured_deck_title = ""
        self.captured_author = ""
        self.captured_slides: list[dict] = []

    def render_preview_images(
        self, deck_title: str, author: str, slides: list[dict],
        color_config: dict | None = None,
    ) -> Result[list[bytes], Exception]:
        self.captured_deck_title = deck_title
        self.captured_author = author
        self.captured_slides = slides
        return success([b"png_title", b"png_slide1", b"png_slide2"])


class TestPreviewImagesUseCase:
    def test_should_render_preview_images_successfully(self) -> None:
        repository = MockSlidePreviewRepository()
        usecase = PreviewImagesUseCase(preview_repository=repository)

        result = usecase.execute(
            deck_title="テスト", author="著者", slides=MOCK_SLIDES
        )

        assert isinstance(result, Success)
        assert len(result.data) == 3

    def test_should_pass_parameters_to_repository(self) -> None:
        repository = MockSlidePreviewRepository()
        usecase = PreviewImagesUseCase(preview_repository=repository)

        usecase.execute(
            deck_title="AIの未来", author="太郎", slides=MOCK_SLIDES
        )

        assert repository.captured_deck_title == "AIの未来"
        assert repository.captured_author == "太郎"
        assert len(repository.captured_slides) == 2

    def test_should_return_bytes_for_each_image(self) -> None:
        repository = MockSlidePreviewRepository()
        usecase = PreviewImagesUseCase(preview_repository=repository)

        result = usecase.execute(
            deck_title="テスト", author="", slides=MOCK_SLIDES
        )

        assert isinstance(result, Success)
        for img in result.data:
            assert isinstance(img, bytes)
