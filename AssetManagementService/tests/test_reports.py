from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.services import translation_loader

@pytest.fixture
def client(tmp_path: Path):
    database_file = tmp_path / "test-reports.db"

    test_engine = create_engine(
        f"sqlite:///{database_file}",
        connect_args={"check_same_thread": False},
    )

    TestSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    def override_get_db():
        db = TestSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app)

    yield test_client

    app.dependency_overrides.clear()
    test_engine.dispose()


@pytest.mark.parametrize(
    "language",
    ["en", "fr", "de"],
)
def test_create_report_returns_pdf(
    client: TestClient,
    language: str,
) -> None:
    response = client.post(
        "/reports",
        json={"language": language},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_create_report_rejects_unsupported_language(
    client: TestClient,
) -> None:
    response = client.post(
        "/reports",
        json={"language": "es"},
    )

    assert response.status_code == 422


def test_create_report_returns_503_when_translation_file_is_missing(
    client: TestClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        translation_loader,
        "TRANSLATIONS_DIRECTORY",
        tmp_path,
    )

    response = client.post(
        "/reports",
        json={"language": "en"},
    )

    assert response.status_code == 503
    assert isinstance(response.json()["detail"], str)


def test_create_report_returns_503_when_translation_json_is_invalid(
    client: TestClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invalid_translation_file = tmp_path / "messages.en.json"

    invalid_translation_file.write_text(
        "{ invalid json }",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        translation_loader,
        "TRANSLATIONS_DIRECTORY",
        tmp_path,
    )

    response = client.post(
        "/reports",
        json={"language": "en"},
    )

    assert response.status_code == 503
    assert isinstance(response.json()["detail"], str)