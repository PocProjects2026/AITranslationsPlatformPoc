import json
from pathlib import Path


TRANSLATIONS_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "translations"
)


def load_translations(
    language: str,
) -> dict[str, str]:
    """
    Charge le fichier JSON correspondant à la langue demandée.
    """

    translation_file = (
        TRANSLATIONS_DIRECTORY
        / f"messages.{language}.json"
    )

    if not translation_file.exists():
        raise FileNotFoundError(
            f"Translation file not found: {translation_file}"
        )

    with translation_file.open(
        mode="r",
        encoding="utf-8",
    ) as file:
        translations = json.load(file)

    return translations