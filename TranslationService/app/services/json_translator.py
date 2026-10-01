import json
from pathlib import Path

from app.services.azure_translator import AzureTranslator


def load_json_catalog(
    file_path: Path,
) -> dict[str, str]:
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Translation file '{file_path}' was not found."
        )

    try:
        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Translation file '{file_path}' contains invalid JSON."
        ) from error

    if not isinstance(data, dict):
        raise ValueError(
            "Translation catalog must be a JSON object."
        )

    if not all(
        isinstance(key, str)
        and isinstance(value, str)
        for key, value in data.items()
    ):
        raise ValueError(
            "Translation keys and values must all be strings."
        )

    return data


async def translate_json_catalog(
    source_catalog: dict[str, str],
    target_language: str,
) -> dict[str, str]:
    if target_language not in {"fr", "de"}:
        raise ValueError(
            "Only 'fr' and 'de' are supported."
        )

    translator = AzureTranslator()

    keys = list(source_catalog.keys())
    source_texts = list(source_catalog.values())

    translated_texts = await translator.translate_many(
        texts=source_texts,
        source_language="en",
        target_language=target_language,
    )

    return dict(
        zip(
            keys,
            translated_texts,
        )
    )


async def generate_translated_json(
    source_file: Path,
    output_file: Path,
    target_language: str,
) -> None:
    source_catalog = load_json_catalog(
        source_file
    )

    translated_catalog = await translate_json_catalog(
        source_catalog,
        target_language,
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            translated_catalog,
            file,
            ensure_ascii=False,
            indent=2,
        )

def validate_translation_catalogs(
    english_catalog: dict[str, str],
    french_catalog: dict[str, str],
    german_catalog: dict[str, str],
) -> None:
    english_keys = set(english_catalog.keys())

    if set(french_catalog.keys()) != english_keys:
        raise ValueError(
            "French translation catalog does not contain the same keys as English."
        )

    if set(german_catalog.keys()) != english_keys:
        raise ValueError(
            "German translation catalog does not contain the same keys as English."
        )