import argparse
import sys
from pathlib import Path
from .formats import parse_json, build_json_artifact, parse_xliff, build_xliff_artifact
from .providers import get_provider
from .pipeline import rank_candidates
import json

def process_file(input_path: str, output_path: str, source_lang: str, target_lang: str, provider_name: str, glossary_path: str = None):
    glossary = None
    if glossary_path:
        glossary = json.loads(Path(glossary_path).read_text(encoding="utf-8"))

    content = Path(input_path).read_bytes()
    ext = Path(input_path).suffix.lower()
    
    if ext == ".json":
        parsed = parse_json(content.decode("utf-8"))
    elif ext in (".xlf", ".xliff"):
        parsed = parse_xliff(content)
    else:
        raise ValueError("Unsupported format")

    segments = parsed["segments"]
    provider = get_provider(provider_name)

    texts = [s["text"] for s in segments]
    
    # We ask provider for one candidate, but ideally provider might return multiple.
    # We will simulate multiple candidates by just passing the single candidate to ranker.
    # Or provider could generate multiple candidates in the future.
    drafts = provider.translate_batch(texts, source_lang, target_lang, glossary)
    
    final_translations = {}
    for seg, draft in zip(segments, drafts):
        candidates = [draft]
        ranked = rank_candidates(seg["text"], candidates, glossary)
        best = ranked[0]["text"]
        final_translations[seg["path"]] = best
        
    if ext == ".json":
        result = build_json_artifact(parsed["raw"], final_translations)
        Path(output_path).write_text(result, encoding="utf-8")
    else:
        result = build_xliff_artifact(parsed["tree"], parsed["version"], final_translations)
        Path(output_path).write_bytes(result)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--source-lang", default="en")
    p.add_argument("--target-lang", required=True)
    p.add_argument("--provider", default="anthropic")
    p.add_argument("--glossary")
    args = p.parse_args()
    
    process_file(args.input, args.output, args.source_lang, args.target_lang, args.provider, args.glossary)

if __name__ == "__main__":
    main()
