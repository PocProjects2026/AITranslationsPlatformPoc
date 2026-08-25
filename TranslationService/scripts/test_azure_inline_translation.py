import asyncio
from pathlib import Path
import xml.etree.ElementTree as ET

from app.services.azure_translator import AzureTranslator
from app.services.xlf_parser import protect_inline_elements,restore_inline_elements


XLF_NAMESPACE = "urn:oasis:names:tc:xliff:document:1.2"


async def main():
    file_path = Path("../FrontendApp/src/locale/messages.xlf")

    root = ET.parse(file_path).getroot()

    namespace = {
        "xlf": XLF_NAMESPACE,
    }

    for unit in root.findall(".//xlf:trans-unit", namespace):
        if unit.attrib.get("id") != "mainPageHeading":
            continue

        source = unit.find("xlf:source", namespace)

        if source is None:
            continue

        protected = protect_inline_elements(source)

        translator = AzureTranslator()

        translated_text = await translator.translate(
            protected.text,
            "en",
            "fr",
        )

        print("Original:")
        print(protected.text)

        print("\nTranslated:")
        print(translated_text)

        for token in protected.placeholders:
            if token not in translated_text:
                raise ValueError(
                    f"Azure removed or modified placeholder: {token}"
                )

        print("\nPlaceholders preserved correctly.")

    target = restore_inline_elements(
    translated_text,
    protected.placeholders,
    )
    print("\nGenerated target:")
    print(ET.tostring(target, encoding="unicode"))


asyncio.run(main())