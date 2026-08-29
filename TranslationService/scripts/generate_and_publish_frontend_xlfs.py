import asyncio
import os
import xml.etree.ElementTree as ET
from pathlib import Path

from app.services.r2_uploader import publish_translation_version
from app.services.xlf_generator import generate_translated_xlf


SERVICE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = SERVICE_ROOT.parent

SOURCE_FILE = (
    REPOSITORY_ROOT
    / "FrontendApp"
    / "src"
    / "locale"
    / "messages.xlf"
)

ARTIFACTS_DIRECTORY = (
    SERVICE_ROOT
    / "artifacts"
    / "frontend"
)

FRENCH_FILE = ARTIFACTS_DIRECTORY / "messages.fr.xlf"
GERMAN_FILE = ARTIFACTS_DIRECTORY / "messages.de.xlf"


def get_translation_version() -> str:
    version = os.getenv("TRANSLATION_VERSION")

    if not version:
        raise ValueError(
            "Missing TRANSLATION_VERSION environment variable."
        )

    return version


def get_translation_unit_ids(
    file_path: Path,
) -> set[str]:

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Missing XLIFF file: {file_path}"
        )

    try:
        tree = ET.parse(file_path)
    except ET.ParseError as exc:
        raise ValueError(
            f"Invalid XLIFF XML: {file_path}"
        ) from exc

    root = tree.getroot()

    translation_ids: set[str] = set()

    for element in root.iter():
        if element.tag.endswith("trans-unit"):
            unit_id = element.get("id")

            if unit_id:
                translation_ids.add(unit_id)

    if not translation_ids:
        raise ValueError(
            f"No translation units found in {file_path}"
        )

    return translation_ids


def validate_xlf_catalogs(
    source_file: Path,
    french_file: Path,
    german_file: Path,
) -> None:

    source_ids = get_translation_unit_ids(
        source_file
    )

    french_ids = get_translation_unit_ids(
        french_file
    )

    german_ids = get_translation_unit_ids(
        german_file
    )

    if french_ids != source_ids:
        missing = source_ids - french_ids
        extra = french_ids - source_ids

        raise ValueError(
            "French XLIFF keys do not match English. "
            f"Missing: {sorted(missing)}. "
            f"Extra: {sorted(extra)}."
        )

    if german_ids != source_ids:
        missing = source_ids - german_ids
        extra = german_ids - source_ids

        raise ValueError(
            "German XLIFF keys do not match English. "
            f"Missing: {sorted(missing)}. "
            f"Extra: {sorted(extra)}."
        )

    print(
        f"XLIFF validation successful: "
        f"{len(source_ids)} translation units."
    )


async def main() -> None:
    version = get_translation_version()

    if not SOURCE_FILE.is_file():
        raise FileNotFoundError(
            f"English source XLIFF does not exist: "
            f"{SOURCE_FILE}"
        )

    ARTIFACTS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("Generating French XLIFF...")

    await generate_translated_xlf(
        source_file=SOURCE_FILE,
        output_file=FRENCH_FILE,
        target_language="fr",
    )

    print("French XLIFF generated.")

    print("Generating German XLIFF...")

    await generate_translated_xlf(
        source_file=SOURCE_FILE,
        output_file=GERMAN_FILE,
        target_language="de",
    )

    print("German XLIFF generated.")

    print("Validating XLIFF catalogs...")

    validate_xlf_catalogs(
        SOURCE_FILE,
        FRENCH_FILE,
        GERMAN_FILE,
    )

    print(
        f"Publishing frontend translation version: "
        f"{version}"
    )

    uploaded_keys = publish_translation_version(
        files=[
            SOURCE_FILE,
            FRENCH_FILE,
            GERMAN_FILE,
        ],
        prefix="translations",
        version=version,
    )

    for object_key in uploaded_keys:
        print(
            f"Published: {object_key}"
        )

    print(
        f"Frontend translation version "
        f"{version} published successfully."
    )


if __name__ == "__main__":
    asyncio.run(main())