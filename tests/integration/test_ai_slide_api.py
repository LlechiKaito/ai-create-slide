from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.src.domain.commons.result import Result, success
from backend.src.main import app

MOCK_IMAGE_BYTES = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"

MOCK_GENERATED_CONTENT = {
    "deck_title": "AIの未来",
    "author": "",
    "slides": [
        {
            "title": "はじめに",
            "subtitle": "",
            "content": "AIの概要",
            "bullet_points": ["ポイント1", "ポイント2"],
            "image_prompt": "A robot thinking about AI",
        },
        {
            "title": "まとめ",
            "subtitle": "",
            "content": "結論",
            "bullet_points": [],
            "image_prompt": "A summary chart",
        },
    ],
}

MOCK_REVISED_CONTENT = {
    "deck_title": "AIの未来と課題",
    "author": "",
    "slides": [
        {
            "title": "はじめに（改訂）",
            "subtitle": "改訂版",
            "content": "AIの概要（修正済み）",
            "bullet_points": ["ポイント1", "ポイント2", "ポイント3"],
            "image_prompt": "A robot learning from data",
        },
    ],
}


def mock_generate(
    self, theme: str, num_slides: int, category: str = "sales_proposal",
) -> Result[dict, Exception]:
    return success(MOCK_GENERATED_CONTENT)


def mock_revise(
    self, current_content: dict, revision_instruction: str
) -> Result[dict, Exception]:
    return success(MOCK_REVISED_CONTENT)


def mock_generate_image(self, prompt: str) -> Result[bytes, Exception]:
    return success(MOCK_IMAGE_BYTES)


@pytest.mark.anyio
@patch(
    "backend.src.infrastructure.external.gemini_client.GeminiAiSlideRepository.generate_slide_content",
    mock_generate,
)
@patch(
    "backend.src.infrastructure.external.gemini_client.GeminiAiSlideRepository.generate_image",
    mock_generate_image,
)
async def test_should_ai_generate_slides() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/slides/ai-generate",
            json={"theme": "AIの未来", "num_slides": 5},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["is_success"] is True
    assert data["deck_title"] == "AIの未来"
    assert len(data["slides"]) == 2


@pytest.mark.anyio
@patch(
    "backend.src.infrastructure.external.gemini_client.GeminiAiSlideRepository.revise_slide_content",
    mock_revise,
)
@patch(
    "backend.src.infrastructure.external.gemini_client.GeminiAiSlideRepository.generate_image",
    mock_generate_image,
)
async def test_should_ai_revise_slides() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/slides/ai-revise",
            json={
                "current_content": {
                    "is_success": True,
                    "deck_title": "AIの未来",
                    "author": "",
                    "slides": [
                        {
                            "title": "はじめに",
                            "subtitle": "",
                            "content": "AIの概要",
                            "bullet_points": ["ポイント1"],
                        },
                    ],
                },
                "revision_instruction": "もっと詳しく書いてください",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["is_success"] is True
    assert data["deck_title"] == "AIの未来と課題"


@pytest.mark.anyio
async def test_should_return_422_when_theme_empty() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/slides/ai-generate",
            json={"theme": "", "num_slides": 5},
        )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_should_return_422_when_revision_instruction_empty() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/slides/ai-revise",
            json={
                "current_content": {
                    "is_success": True,
                    "deck_title": "Test",
                    "author": "",
                    "slides": [{"title": "S1"}],
                },
                "revision_instruction": "",
            },
        )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_should_return_422_when_num_slides_exceeds_max() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/slides/ai-generate",
            json={"theme": "テスト", "num_slides": 100},
        )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_should_generate_preview_images() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/slides/preview-images",
            json={
                "deck_title": "テストプレゼン",
                "author": "テスト太郎",
                "slides": [
                    {
                        "title": "スライド1",
                        "subtitle": "サブタイトル",
                        "content": "本文",
                        "bullet_points": ["箇条書き1"],
                    },
                    {
                        "title": "スライド2",
                        "subtitle": "",
                        "content": "内容",
                        "bullet_points": [],
                    },
                ],
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert "images" in data
    assert len(data["images"]) == 3
    for img in data["images"]:
        assert isinstance(img, str)
        assert len(img) > 0


@pytest.mark.anyio
async def test_should_return_422_when_preview_deck_title_empty() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/slides/preview-images",
            json={
                "deck_title": "",
                "author": "",
                "slides": [{"title": "S1"}],
            },
        )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_should_return_422_when_preview_slides_empty() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/slides/preview-images",
            json={
                "deck_title": "テスト",
                "author": "",
                "slides": [],
            },
        )
    assert response.status_code == 422
