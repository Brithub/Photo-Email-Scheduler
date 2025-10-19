import os
import uuid
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient, Response

import response_api
from response_api import photo_taken


def test_photo_taken_first_of_day():
    # Test photo_taken endpoint for first photo of the day

    test_meta_directory = f"/tmp/{uuid.uuid4()}"
    os.environ["META_DIRECTORY"] = test_meta_directory

    response = photo_taken("sam", "+0000")

    # it'll be using the default responses
    assert response[:8] == "Response"


def test_photo_taken_already_taken(monkeypatch):
    # Test photo_taken when photo already taken today
    test_meta_directory = f"/tmp/{uuid.uuid4()}"
    os.environ["META_DIRECTORY"] = test_meta_directory

    mock_now = MagicMock()
    mock_now.return_value = MagicMock(year=2023, month=1, day=1)
    monkeypatch.setattr(response_api, "now", mock_now)
    marker_path = test_meta_directory + "/markers/sam/2023/1/1/marker"
    Path(marker_path).parent.mkdir(exist_ok=True, parents=True)
    with open(marker_path, mode="w") as f:
        f.write("Photo taken")

    response = photo_taken("sam", "+0000")

    # We use the korean flag as a delimiter for some reason
    assert "🇰🇷" in response


@pytest.mark.anyio
async def test_add_text():
    test_meta_directory = f"/tmp/{uuid.uuid4()}"
    os.environ["META_DIRECTORY"] = test_meta_directory

    base_url = "http://test"
    app = response_api.app
    async with AsyncClient(transport=ASGITransport(app), base_url=base_url) as ac:
        response: Response = await ac.put(
            "/add_text/responses", content="This is a new message"
        )

        assert response.text == '"Message added"'


@pytest.mark.anyio
async def test_add_text_invalid_type():
    test_meta_directory = f"/tmp/{uuid.uuid4()}"
    os.environ["META_DIRECTORY"] = test_meta_directory

    base_url = "http://test"
    app = response_api.app
    async with AsyncClient(transport=ASGITransport(app), base_url=base_url) as ac:
        response: Response = await ac.put(
            "/add_text/other", content="This is a new message"
        )

        assert response.text == '"Invalid message type"'
