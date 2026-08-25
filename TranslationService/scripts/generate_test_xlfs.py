import asyncio
from pathlib import Path

from app.services.xlf_generator import (
    generate_translated_xlf,
)


async def main():
    source_file = Path(
        "../FrontendApp/src/locale/messages.xlf"
    )

    print("Generating French XLIFF...")

    await generate_translated_xlf(
        source_file=source_file,
        output_file=Path(
            "artifacts/messages.fr.xlf"
        ),
        target_language="fr",
    )

    print(
        "French XLIFF generated successfully."
    )

    print("Generating German XLIFF...")

    await generate_translated_xlf(
        source_file=source_file,
        output_file=Path(
            "artifacts/messages.de.xlf"
        ),
        target_language="de",
    )

    print(
        "German XLIFF generated successfully."
    )


asyncio.run(main())