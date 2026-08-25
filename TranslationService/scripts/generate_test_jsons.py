import asyncio
import shutil
from pathlib import Path

from app.services.json_translator import (
    generate_translated_json,
)


async def main():
    source_file = Path(
        "../AssetManagementService/"
        "app/translations/messages.en.json"
    )

    output_directory = Path(
        "artifacts/asset-management"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copyfile(
        source_file,
        output_directory / "messages.en.json",
    )

    print("Generating French JSON...")

    await generate_translated_json(
        source_file=source_file,
        output_file=(
            output_directory
            / "messages.fr.json"
        ),
        target_language="fr",
    )

    print("French JSON generated successfully.")

    print("Generating German JSON...")

    await generate_translated_json(
        source_file=source_file,
        output_file=(
            output_directory
            / "messages.de.json"
        ),
        target_language="de",
    )

    print("German JSON generated successfully.")


asyncio.run(main())