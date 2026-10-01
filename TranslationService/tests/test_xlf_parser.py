import xml.etree.ElementTree as ET

import pytest

from app.services.xlf_parser import (
    XLF_NAMESPACE,
    protect_inline_elements,
    restore_inline_elements,
)


def test_protect_inline_elements_preserves_placeholder():
    source = ET.Element(f"{{{XLF_NAMESPACE}}}source")
    source.text = "Hello "

    placeholder = ET.SubElement(
        source,
        f"{{{XLF_NAMESPACE}}}x",
        {
            "id": "INTERPOLATION",
            "equiv-text": "{{ name }}",
        },
    )
    placeholder.tail = "!"

    protected = protect_inline_elements(source)

    assert protected.text == "Hello __XLIFF_0__!"
    assert "__XLIFF_0__" in protected.placeholders
    assert (
        protected.placeholders["__XLIFF_0__"].attrib["equiv-text"]
        == "{{ name }}"
    )


def test_restore_inline_elements_restores_placeholder():
    source = ET.Element(f"{{{XLF_NAMESPACE}}}source")

    placeholder = ET.SubElement(
        source,
        f"{{{XLF_NAMESPACE}}}x",
        {
            "id": "INTERPOLATION",
            "equiv-text": "{{ name }}",
        },
    )

    protected = protect_inline_elements(source)

    target = restore_inline_elements(
        "Bonjour __XLIFF_0__ !",
        protected.placeholders,
    )

    assert target.text == "Bonjour "
    assert len(target) == 1

    restored_placeholder = target[0]

    assert restored_placeholder.attrib["id"] == "INTERPOLATION"
    assert restored_placeholder.attrib["equiv-text"] == "{{ name }}"
    assert restored_placeholder.tail == " !"


def test_restore_inline_elements_fails_when_placeholder_is_missing():
    source = ET.Element(f"{{{XLF_NAMESPACE}}}source")

    ET.SubElement(
        source,
        f"{{{XLF_NAMESPACE}}}x",
        {
            "id": "INTERPOLATION",
            "equiv-text": "{{ name }}",
        },
    )

    protected = protect_inline_elements(source)

    with pytest.raises(
        ValueError,
        match="Missing placeholder after translation",
    ):
        restore_inline_elements(
            "Bonjour !",
            protected.placeholders,
        )