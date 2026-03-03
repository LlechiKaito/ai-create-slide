import pytest
from httpx import ASGITransport, AsyncClient

from backend.src.main import app


@pytest.mark.anyio
async def test_health_check() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["is_success"] is True
    assert data["message"] == "OK"


@pytest.mark.anyio
async def test_should_generate_slides_with_valid_data() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/slides/generate",
            json={
                "deck_title": "Test Presentation",
                "author": "Test Author",
                "slides": [
                    {
                        "title": "First Slide",
                        "subtitle": "Subtitle",
                        "content": "Some content here",
                        "bullet_points": ["Point 1", "Point 2"],
                    },
                ],
            },
        )
    assert response.status_code == 200
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    assert len(response.content) > 0


@pytest.mark.anyio
async def test_should_return_422_when_deck_title_missing() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/slides/generate",
            json={
                "author": "Author",
                "slides": [{"title": "Slide"}],
            },
        )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_should_return_422_when_slides_empty() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/slides/generate",
            json={
                "deck_title": "Test",
                "author": "",
                "slides": [],
            },
        )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_should_return_422_when_slide_title_empty() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/slides/generate",
            json={
                "deck_title": "Test",
                "author": "",
                "slides": [
                    {
                        "title": "",
                        "content": "Content",
                    },
                ],
            },
        )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_should_generate_multiple_slides() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/slides/generate",
            json={
                "deck_title": "Multi Slide Deck",
                "author": "",
                "slides": [
                    {"title": "Slide 1", "content": "Content 1"},
                    {"title": "Slide 2", "content": "Content 2"},
                    {
                        "title": "Slide 3",
                        "content": "",
                        "bullet_points": ["A", "B"],
                    },
                ],
            },
        )
    assert response.status_code == 200
    assert len(response.content) > 0
