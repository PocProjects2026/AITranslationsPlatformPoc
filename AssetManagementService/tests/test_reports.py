import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.mark.parametrize(
    "language",
    ["en", "fr", "de"],
)
def test_create_report_returns_pdf(language: str) -> None:
    response = client.post(
        "/reports",
        json={"language": language},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_create_report_rejects_unsupported_language() -> None:
    response = client.post(
        "/reports",
        json={"language": "es"},
    )

    assert response.status_code == 422