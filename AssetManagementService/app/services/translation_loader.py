import json
from pathlib import Path


TRANSLATIONS_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "translations"
)


def _read_translation_file(
    translation_file: Path,
) -> dict[str, str]:

    if not translation_file.exists():
        raise FileNotFoundError(
            f"Translation file '{translation_file.name}' was not found."
        )

    try:
        with translation_file.open(
            mode="r",
            encoding="utf-8",
        ) as file:
            translations = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Translation file '{translation_file.name}' contains invalid JSON."
        ) from error

    if not isinstance(translations, dict):
        raise ValueError(
            f"Translation file '{translation_file.name}' must contain a JSON object."
        )

    for key, value in translations.items():
        if not isinstance(key, str):
            raise ValueError(
                "Translation keys must be strings."
            )

        if not isinstance(value, str):
            raise ValueError(
                f"Translation value for '{key}' must be a string."
            )

    return translations


def load_translations(
    language: str,
) -> dict[str, str]:

    translation_file = (
        TRANSLATIONS_DIRECTORY
        / f"messages.{language}.json"
    )

    translations = _read_translation_file(
        translation_file
    )

    if language != "en":
        english_file = (
            TRANSLATIONS_DIRECTORY
            / "messages.en.json"
        )

        english_translations = _read_translation_file(
            english_file
        )

        if translations.keys() != english_translations.keys():
            raise ValueError(
                f"Translation file for language '{language}' "
                "does not contain the same keys as English."
            )

    return translations