import asyncio
from pathlib import Path

from app.services.json_translator import (
    generate_translated_json,
)
from app.services.r2_uploader import (
    publish_translation_version,
)
from app.services.json_translator import (
    generate_translated_json,
    load_json_catalog,
    validate_translation_catalogs,
    )

ARTIFACTS_DIRECTORY = Path(
    "artifacts/asset-management"
)

SOURCE_FILE = (
    ARTIFACTS_DIRECTORY
    / "messages.en.json"
)


async def main() -> None:
    await generate_translated_json(
        source_file=SOURCE_FILE,
        output_file=ARTIFACTS_DIRECTORY / "messages.fr.json",
        target_language="fr",
    )

    await generate_translated_json(
        source_file=SOURCE_FILE,
        output_file=ARTIFACTS_DIRECTORY / "messages.de.json",
        target_language="de",
    )
 
    uploaded_keys = publish_translation_version(
        ARTIFACTS_DIRECTORY
    )
    english_catalog = load_json_catalog(
        ARTIFACTS_DIRECTORY / "messages.en.json"
    )

    french_catalog = load_json_catalog(
        ARTIFACTS_DIRECTORY / "messages.fr.json"
    )

    german_catalog = load_json_catalog(
        ARTIFACTS_DIRECTORY / "messages.de.json"
    )

    validate_translation_catalogs(
        english_catalog,
        french_catalog,
        german_catalog,
    )

    uploaded_keys = publish_translation_version(
        ARTIFACTS_DIRECTORY
    )
    for object_key in uploaded_keys:
        print(f"Published: {object_key}")


if __name__ == "__main__":
    asyncio.run(main())