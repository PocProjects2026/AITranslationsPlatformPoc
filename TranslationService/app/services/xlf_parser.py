from copy import deepcopy
from dataclasses import dataclass
import xml.etree.ElementTree as ET


XLF_NAMESPACE = "urn:oasis:names:tc:xliff:document:1.2"

ET.register_namespace("", XLF_NAMESPACE)


@dataclass(frozen=True)
class ProtectedXlfText:
    text: str
    placeholders: dict[str, ET.Element]


def protect_inline_elements(
    source: ET.Element,
) -> ProtectedXlfText:
    parts: list[str] = []
    placeholders: dict[str, ET.Element] = {}

    if source.text:
        parts.append(source.text)

    for index, child in enumerate(source):
        token = f"__XLIFF_{index}__"

        placeholders[token] = child
        parts.append(token)

        if child.tail:
            parts.append(child.tail)

    return ProtectedXlfText(
        text="".join(parts).strip(),
        placeholders=placeholders,
    )


def restore_inline_elements(
    translated_text: str,
    placeholders: dict[str, ET.Element],
) -> ET.Element:
    target = ET.Element(
        f"{{{XLF_NAMESPACE}}}target"
    )

    positions = []

    for token, element in placeholders.items():
        position = translated_text.find(token)

        if position == -1:
            raise ValueError(
                f"Missing placeholder after translation: {token}"
            )

        positions.append(
            (position, token, element)
        )

    positions.sort()

    cursor = 0
    previous_child = None

    for position, token, element in positions:
        text_before = translated_text[cursor:position]

        if previous_child is None:
            target.text = text_before
        else:
            previous_child.tail = text_before

        child_copy = deepcopy(element)
        child_copy.tail = None

        target.append(child_copy)

        previous_child = child_copy
        cursor = position + len(token)

    remaining_text = translated_text[cursor:]

    if previous_child is None:
        target.text = remaining_text
    else:
        previous_child.tail = remaining_text

    return target