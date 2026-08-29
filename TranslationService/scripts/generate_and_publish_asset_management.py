import asyncio
import os
import shutil
from pathlib import Path

from app.services.json_translator import (
    generate_translated_json,
    load_json_catalog,
    validate_translation_catalogs,
)
from app.services.r2_uploader import (
    publish_translation_version,
)


SERVICE_ROOT = Path(__file__).resolve().parents[1]

SOURCE_FILE = (
    SERVICE_ROOT
    / "sources"
    / "asset-management"
    / "messages.en.json"
)

ARTIFACTS_DIRECTORY = (
    SERVICE_ROOT
    / "artifacts"
    / "asset-management"
)


def get_translation_version() -> str:
    version = os.getenv("TRANSLATION_VERSION")

    if not version:
        raise ValueError(
            "Missing TRANSLATION_VERSION environment variable."
        )

    return version


async def main() -> None:
    version = get_translation_version()

    if not SOURCE_FILE.is_file():
        raise FileNotFoundError(
            f"Missing Asset Management source catalog: "
            f"{SOURCE_FILE}"
        )

    ARTIFACTS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    english_file = (
        ARTIFACTS_DIRECTORY
        / "messages.en.json"
    )

    french_file = (
        ARTIFACTS_DIRECTORY
        / "messages.fr.json"
    )

    german_file = (
        ARTIFACTS_DIRECTORY
        / "messages.de.json"
    )

    shutil.copy2(
        SOURCE_FILE,
        english_file,
    )

    print(
        "Generating French Asset Management "
        "translations..."
    )

    await generate_translated_json(
        source_file=SOURCE_FILE,
        output_file=french_file,
        target_language="fr",
    )

    print(
        "Generating German Asset Management "
        "translations..."
    )

    await generate_translated_json(
        source_file=SOURCE_FILE,
        output_file=german_file,
        target_language="de",
    )

    print(
        "Validating translation catalogs..."
    )

    english_catalog = load_json_catalog(
        english_file
    )

    french_catalog = load_json_catalog(
        french_file
    )

    german_catalog = load_json_catalog(
        german_file
    )

    validate_translation_catalogs(
        english_catalog,
        french_catalog,
        german_catalog,
    )

    print("Validation successful.")

    print(
        f"Publishing Asset Management "
        f"translation version: {version}"
    )

    uploaded_keys = publish_translation_version(
        files=[
            english_file,
            french_file,
            german_file,
        ],
        prefix="asset-management",
        version=version,
    )

    for object_key in uploaded_keys:
        print(
            f"Published: {object_key}"
        )

    print(
        f"Asset Management translation version "
        f"{version} published successfully."
    )


if __name__ == "__main__":
    asyncio.run(main())