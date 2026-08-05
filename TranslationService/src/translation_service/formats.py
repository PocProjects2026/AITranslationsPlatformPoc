import json
from pathlib import Path
from typing import Any, List, Dict
from lxml import etree

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

def parse_json(content: str) -> Dict:
    data = json.loads(content)
    return {"raw": data, "segments": _flatten_json(data)}

def build_json_artifact(raw: Any, translations: Dict[str, str]) -> str:
    import copy
    output = copy.deepcopy(raw)
    for path, text in translations.items():
        _set_by_path(output, path, text)
    return json.dumps(output, ensure_ascii=False, indent=2)

NS_12 = "urn:oasis:names:tc:xliff:document:1.2"
NS_20 = "urn:oasis:names:tc:xliff:document:2.0"

def _detect_xliff_version(root: etree._Element) -> str:
    version = root.get("version", "")
    return "2.0" if version.startswith("2") else "1.2"

def _get_inner_xml(element: etree._Element) -> str:
    # Gets the string content of an element including its children and text, but not the outer tags.
    text = element.text or ""
    for child in element:
        text += etree.tostring(child, encoding='unicode', with_tail=True)
    return text.strip()

def parse_xliff(content: bytes) -> Dict:
    tree = etree.fromstring(content)
    root = tree
    version = _detect_xliff_version(root)
    ns = {"x": NS_20 if version == "2.0" else NS_12}

    segments = []
    if version == "1.2":
        units = root.findall(".//x:trans-unit", ns)
        for u in units:
            src = u.find("x:source", ns)
            if src is not None:
                inner_text = _get_inner_xml(src)
                if inner_text.strip():
                    segments.append({"id": u.get("id"), "text": inner_text, "path": u})
    else:  # 2.0
        units = root.findall(".//x:unit", ns)
        for u in units:
            for seg in u.findall("x:segment", ns):
                src = seg.find("x:source", ns)
                if src is not None:
                    inner_text = _get_inner_xml(src)
                    if inner_text.strip():
                        segments.append({"id": u.get("id"), "text": inner_text, "path": seg})

    return {"tree": root, "version": version, "segments": segments}

def build_xliff_artifact(root: etree._Element, version: str, translations: Dict[etree._Element, str]) -> bytes:
    ns = {"x": NS_20 if version == "2.0" else NS_12}
    nsmap_uri = NS_20 if version == "2.0" else NS_12
    
    import copy
    root_copy = copy.deepcopy(root)
    
    # We need a way to match elements from original root to copied root. 
    # Let's map by XPath or simply iterate and apply translations.
    # Actually, a simpler way is to just generate the string for the target.
    # Since etree allows us to parse a fragment, we can parse the translated text as XML fragment if it has tags.
    
    # Let's build a map of segment id to translation to apply on the cloned tree.
    trans_map = {}
    for element, text in translations.items():
        if version == "1.2":
            trans_map[element.get("id")] = text
        else:
            trans_map[(element.getparent().get("id"), element.get("id") or "")] = text

    if version == "1.2":
        units = root_copy.findall(".//x:trans-unit", ns)
        for u in units:
            u_id = u.get("id")
            if u_id in trans_map:
                text = trans_map[u_id]
                target = u.find("x:target", ns)
                if target is None:
                    target = etree.SubElement(u, f"{{{nsmap_uri}}}target")
                else:
                    target.clear()
                # If text contains XML tags, we need to append them as children.
                try:
                    frag = etree.fromstring(f"<target>{text}</target>")
                    target.text = frag.text
                    for child in frag:
                        target.append(child)
                except Exception:
                    target.text = text
    else:
        units = root_copy.findall(".//x:unit", ns)
        for u in units:
            u_id = u.get("id")
            for seg in u.findall("x:segment", ns):
                seg_id = seg.get("id") or ""
                key = (u_id, seg_id)
                if key in trans_map:
                    text = trans_map[key]
                    target = seg.find("x:target", ns)
                    if target is None:
                        target = etree.SubElement(seg, f"{{{nsmap_uri}}}target")
                    else:
                        target.clear()
                    try:
                        frag = etree.fromstring(f"<target>{text}</target>")
                        target.text = frag.text
                        for child in frag:
                            target.append(child)
                    except Exception:
                        target.text = text

    return etree.tostring(root_copy, encoding="utf-8", xml_declaration=True, pretty_print=True)
