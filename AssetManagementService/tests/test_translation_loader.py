import json

import pytest

from app.services import translation_loader


def test_load_translations_rejects_missing_file(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        translation_loader,
        "TRANSLATIONS_DIRECTORY",
        tmp_path,
    )

    with pytest.raises(
        FileNotFoundError,
        match="messages.fr.json",
    ):
        translation_loader.load_translations(
            "fr"
        )


def test_load_translations_rejects_invalid_json(
    tmp_path,
    monkeypatch,
):
    english_file = (
        tmp_path / "messages.en.json"
    )

    english_file.write_text(
        json.dumps(
            {
                "asset-management-status": "Status"
            }
        ),
        encoding="utf-8",
    )

    french_file = (
        tmp_path / "messages.fr.json"
    )

    french_file.write_text(
        "{ invalid json",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        translation_loader,
        "TRANSLATIONS_DIRECTORY",
        tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="invalid JSON",
    ):
        translation_loader.load_translations(
            "fr"
        )


def test_load_translations_rejects_missing_keys(
    tmp_path,
    monkeypatch,
):
    english_file = (
        tmp_path / "messages.en.json"
    )

    english_file.write_text(
        json.dumps(
            {
                "asset-management-status": "Status",
                "asset-management-reference": "Reference",
            }
        ),
        encoding="utf-8",
    )

    french_file = (
        tmp_path / "messages.fr.json"
    )

    french_file.write_text(
        json.dumps(
            {
                "asset-management-status": "Statut"
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        translation_loader,
        "TRANSLATIONS_DIRECTORY",
        tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="same keys as English",
    ):
        translation_loader.load_translations(
            "fr"
        )