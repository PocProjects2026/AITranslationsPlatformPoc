import pytest

from app.services.translation_loader import load_translations


@pytest.mark.parametrize(
    "language",
    ["fr", "de"],
)
def test_translation_files_have_same_keys_as_english(
    language: str,
) -> None:
    english_translations = load_translations("en")
    selected_translations = load_translations(language)

    english_keys = set(english_translations.keys())
    selected_keys = set(selected_translations.keys())

    missing_keys = english_keys - selected_keys
    extra_keys = selected_keys - english_keys

    assert not missing_keys, (
        f"Missing keys in {language}: {missing_keys}"
    )

    assert not extra_keys, (
        f"Extra keys in {language}: {extra_keys}"
    )