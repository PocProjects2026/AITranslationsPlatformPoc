import asyncio
from pathlib import Path

from app.services.xlf_generator import generate_translated_xlf


async def main():
    await generate_translated_xlf(
        source_file=Path(
            "../FrontendApp/src/locale/messages.xlf"
        ),
        output_file=Path(
            "artifacts/messages.fr.xlf"
        ),
        target_language="fr",
    )


asyncio.run(main())