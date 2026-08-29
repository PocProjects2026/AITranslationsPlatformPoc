from copy import deepcopy
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from app.services.azure_translator import AzureTranslator
from app.services.xlf_parser import (
    XLF_NAMESPACE,
    protect_inline_elements,
    restore_inline_elements,
)


NAMESPACE = {
    "xlf": XLF_NAMESPACE,
}


ICU_PLURAL_PATTERN = re.compile(
    r"^\s*\{[^,]+,\s*plural,",
    re.DOTALL,
)


def is_icu_reference_source(
    source: ET.Element,
) -> bool:
    return any(
        child.attrib.get("id") == "ICU"
        for child in source
    )


def is_icu_plural_source(
    source: ET.Element,
) -> bool:
    protected = protect_inline_elements(source)

    return bool(
        ICU_PLURAL_PATTERN.match(
            protected.text
        )
    )


def copy_source_to_target(
    source: ET.Element,
) -> ET.Element:
    target = ET.Element(
        f"{{{XLF_NAMESPACE}}}target"
    )

    target.text = source.text

    for child in source:
        target.append(
            deepcopy(child)
        )

    return target


def validate_placeholders(
    original_text: str,
    translated_text: str,
    placeholders: dict[str, ET.Element],
) -> None:
    for token in placeholders:
        if token not in original_text:
            continue

        if translated_text.count(token) != 1:
            raise ValueError(
                f"Placeholder '{token}' was modified "
                "during translation."
            )


def parse_icu_plural(
    text: str,
) -> tuple[str, list[tuple[str, str]]]:
    text = text.strip()

    if not (
        text.startswith("{")
        and text.endswith("}")
    ):
        raise ValueError(
            "Invalid ICU plural message."
        )

    inner = text[1:-1].strip()

    first_comma = inner.find(",")

    second_comma = inner.find(
        ",",
        first_comma + 1,
    )

    if (
        first_comma == -1
        or second_comma == -1
    ):
        raise ValueError(
            "Invalid ICU plural structure."
        )

    variable = inner[:first_comma].strip()

    message_type = inner[
        first_comma + 1:second_comma
    ].strip()

    if message_type != "plural":
        raise ValueError(
            "Only ICU plural messages "
            "are supported."
        )

    options_text = inner[
        second_comma + 1:
    ].strip()

    options: list[tuple[str, str]] = []

    index = 0

    while index < len(options_text):
        while (
            index < len(options_text)
            and options_text[index].isspace()
        ):
            index += 1

        if index >= len(options_text):
            break

        opening_brace = options_text.find(
            "{",
            index,
        )

        if opening_brace == -1:
            raise ValueError(
                "Invalid ICU plural option."
            )

        selector = options_text[
            index:opening_brace
        ].strip()

        if not selector:
            raise ValueError(
                "ICU plural selector is missing."
            )

        depth = 0

        closing_brace = opening_brace

        while closing_brace < len(options_text):
            character = options_text[
                closing_brace
            ]

            if character == "{":
                depth += 1

            elif character == "}":
                depth -= 1

                if depth == 0:
                    break

            closing_brace += 1

        if depth != 0:
            raise ValueError(
                "Unbalanced ICU braces."
            )

        message = options_text[
            opening_brace + 1:closing_brace
        ]

        options.append(
            (
                selector,
                message,
            )
        )

        index = closing_brace + 1

    if not options:
        raise ValueError(
            "ICU plural message contains "
            "no options."
        )

    return variable, options


async def translate_simple_source(
    source: ET.Element,
    translator: AzureTranslator,
    target_language: str,
) -> ET.Element:
    source_text = (
        source.text or ""
    ).strip()

    translated_text = await translator.translate(
        source_text,
        "en",
        target_language,
    )

    target = ET.Element(
        f"{{{XLF_NAMESPACE}}}target"
    )

    target.text = translated_text

    return target


async def translate_inline_source(
    source: ET.Element,
    translator: AzureTranslator,
    target_language: str,
) -> ET.Element:
    protected = protect_inline_elements(
        source
    )

    translated_text = await translator.translate(
        protected.text,
        "en",
        target_language,
    )

    validate_placeholders(
        protected.text,
        translated_text,
        protected.placeholders,
    )

    return restore_inline_elements(
        translated_text,
        protected.placeholders,
    )


async def translate_icu_plural_source(
    source: ET.Element,
    translator: AzureTranslator,
    target_language: str,
) -> ET.Element:
    protected = protect_inline_elements(
        source
    )

    variable, options = parse_icu_plural(
        protected.text
    )

    translated_options: list[
        tuple[str, str]
    ] = []

    for selector, message in options:
        message = message.strip()

        if message:
            translated_message = (
                await translator.translate(
                    message,
                    "en",
                    target_language,
                )
            )
        else:
            translated_message = ""

        validate_placeholders(
            message,
            translated_message,
            protected.placeholders,
        )

        translated_options.append(
            (
                selector,
                translated_message,
            )
        )

    translated_body = " ".join(
        f"{selector} {{{message}}}"
        for selector, message
        in translated_options
    )

    translated_icu = (
        "{"
        f"{variable}, plural, "
        f"{translated_body}"
        "}"
    )

    if protected.placeholders:
        return restore_inline_elements(
            translated_icu,
            protected.placeholders,
        )

    target = ET.Element(
        f"{{{XLF_NAMESPACE}}}target"
    )

    target.text = translated_icu

    return target


async def generate_translated_xlf(
    source_file: Path,
    output_file: Path,
    target_language: str,
) -> None:
    if target_language not in {
        "fr",
        "de",
    }:
        raise ValueError(
            "Only 'fr' and 'de' are supported."
        )

    try:
        tree = ET.parse(source_file)
    except ET.ParseError as error:
        raise ValueError(
            "Source XLIFF contains invalid XML."
        ) from error

    root = tree.getroot()

    if root.attrib.get("version") != "1.2":
        raise ValueError(
            "Only XLIFF 1.2 is supported."
        )

    translated_root = deepcopy(root)

    file_element = translated_root.find(
        "xlf:file",
        NAMESPACE,
    )

    if file_element is None:
        raise ValueError(
            "XLIFF file does not contain "
            "a <file> element."
        )

    file_element.set(
        "target-language",
        target_language,
    )

    translator = AzureTranslator()

    for unit in translated_root.findall(
        ".//xlf:trans-unit",
        NAMESPACE,
    ):
        source = unit.find(
            "xlf:source",
            NAMESPACE,
        )

        if source is None:
            raise ValueError(
                "A trans-unit does not "
                "contain a source."
            )

        existing_target = unit.find(
            "xlf:target",
            NAMESPACE,
        )

        if existing_target is not None:
            unit.remove(
                existing_target
            )

        if is_icu_reference_source(source):
            target = copy_source_to_target(
                source
            )

        elif is_icu_plural_source(source):
            target = (
                await translate_icu_plural_source(
                    source,
                    translator,
                    target_language,
                )
            )

        elif len(list(source)) == 0:
            source_text = (
                source.text or ""
            ).strip()

            if not source_text:
                continue

            target = await translate_simple_source(
                source,
                translator,
                target_language,
            )

        else:
            target = await translate_inline_source(
                source,
                translator,
                target_language,
            )

        source_index = list(unit).index(
            source
        )

        unit.insert(
            source_index + 1,
            target,
        )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    translated_tree = ET.ElementTree(
        translated_root
    )

    translated_tree.write(
        output_file,
        encoding="UTF-8",
        xml_declaration=True,
    )