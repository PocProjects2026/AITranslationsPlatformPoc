"""
Extraction et réinjection de segments traduisibles pour fichiers JSON (i18n)
et XLIFF (1.2 et 2.0).

Chaque segment extrait est représenté par un dict :
    {"id": str, "text": str, "path": Any}   # path = clé technique pour la réinjection
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Dict

from lxml import etree


# --------------------------------------------------------------------------- #
# JSON
# --------------------------------------------------------------------------- #

def _flatten_json(obj: Any, prefix: str = "") -> List[Dict]:
    segments = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else key
            segments.extend(_flatten_json(value, path))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            path = f"{prefix}[{idx}]"
            segments.extend(_flatten_json(value, path))
    elif isinstance(obj, str) and obj.strip():
        segments.append({"id": prefix, "text": obj, "path": prefix})
    return segments


def _set_by_path(obj: Any, path: str, value: str) -> None:
    """Navigue dans obj selon un chemin du type 'a.b[0].c' et fixe la valeur."""
    tokens: List[Any] = []
    for part in path.replace("]", "").split("."):
        if "[" in part:
            name, idx = part.split("[")
            if name:
                tokens.append(name)
            tokens.append(int(idx))
        else:
            tokens.append(part)

    cur = obj
    for t in tokens[:-1]:
        cur = cur[t]
    cur[tokens[-1]] = value


def load_json(path: str) -> Dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {"raw": data, "segments": _flatten_json(data)}


def save_json(raw: Any, translations: Dict[str, str], out_path: str) -> None:
    for path, text in translations.items():
        _set_by_path(raw, path, text)
    Path(out_path).write_text(
        json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# --------------------------------------------------------------------------- #
# XLIFF (1.2 / 2.0)
# --------------------------------------------------------------------------- #

NS_12 = "urn:oasis:names:tc:xliff:document:1.2"
NS_20 = "urn:oasis:names:tc:xliff:document:2.0"


def _detect_xliff_version(root: etree._Element) -> str:
    version = root.get("version", "")
    return "2.0" if version.startswith("2") else "1.2"


def load_xliff(path: str):
    tree = etree.parse(path)
    root = tree.getroot()
    version = _detect_xliff_version(root)
    ns = {"x": NS_20 if version == "2.0" else NS_12}

    segments = []
    if version == "1.2":
        units = root.findall(".//x:trans-unit", ns)
        for u in units:
            src = u.find("x:source", ns)
            if src is not None and src.text and src.text.strip():
                segments.append({"id": u.get("id"), "text": src.text, "path": u})
    else:  # 2.0
        units = root.findall(".//x:unit", ns)
        for u in units:
            for seg in u.findall("x:segment", ns):
                src = seg.find("x:source", ns)
                if src is not None and src.text and src.text.strip():
                    segments.append({"id": u.get("id"), "text": src.text, "path": seg})

    return {"tree": tree, "root": root, "version": version, "segments": segments}


def save_xliff(tree, root, version: str, elements_and_translations, out_path: str) -> None:
    """
    elements_and_translations: liste de tuples (element, translated_text)
    où element est soit un <trans-unit> (1.2), soit un <segment> (2.0),
    tel que retourné dans segment['path'].
    """
    ns = {"x": NS_20 if version == "2.0" else NS_12}
    nsmap_uri = NS_20 if version == "2.0" else NS_12

    for element, text in elements_and_translations:
        if version == "1.2":
            target = element.find("x:target", ns)
            if target is None:
                target = etree.SubElement(element, f"{{{nsmap_uri}}}target")
            target.text = text
        else:
            target = element.find("x:target", ns)
            if target is None:
                target = etree.SubElement(element, f"{{{nsmap_uri}}}target")
            target.text = text

    tree.write(out_path, encoding="utf-8", xml_declaration=True, pretty_print=True)


# --------------------------------------------------------------------------- #
# API générique (dispatch selon l'extension)
# --------------------------------------------------------------------------- #

def load_source(path: str):
    ext = Path(path).suffix.lower()
    if ext == ".json":
        return "json", load_json(path)
    elif ext in (".xlf", ".xliff"):
        return "xliff", load_xliff(path)
    else:
        raise ValueError(f"Format non supporté: {ext} (attendu .json, .xlf ou .xliff)")
