from pathlib import Path

import pytest

from app.services.json_translator import (
    load_json_catalog,
    validate_translation_catalogs,
)


def test_load_json_catalog_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "messages.en.json"

    file_path.write_text(
        "{ invalid json }",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_json_catalog(file_path)


def test_validate_translation_catalogs_accepts_matching_keys() -> None:
    english = {
        "title": "Title",
        "status": "Status",
    }

    french = {
        "title": "Titre",
        "status": "Statut",
    }

    german = {
        "title": "Titel",
        "status": "Status",
    }

    validate_translation_catalogs(
        english,
        french,
        german,
    )


def test_validate_translation_catalogs_rejects_missing_french_key() -> None:
    english = {
        "title": "Title",
        "status": "Status",
    }

    french = {
        "title": "Titre",
    }

    german = {
        "title": "Titel",
        "status": "Status",
    }

    with pytest.raises(ValueError):
        validate_translation_catalogs(
            english,
            french,
            german,
        )