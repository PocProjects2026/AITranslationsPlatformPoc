from pathlib import Path
import xml.etree.ElementTree as ET

from app.services.xlf_parser import protect_inline_elements


XLF_NAMESPACE = "urn:oasis:names:tc:xliff:document:1.2"

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

    print("Text sent to translator:")
    print(protected.text)

    print("\nProtected placeholders:")

    for token, element in protected.placeholders.items():
        print(token, "->", element.attrib)