#!/usr/bin/env python3
"""
Pipeline de traduction : extraction -> traduction IA -> amélioration -> réinjection.
Supporte JSON (i18n imbriqué) et XLIFF (1.2 / 2.0).

Exemples :
    python translate.py --input en.json --output fr.json \
        --source-lang en --target-lang fr --provider anthropic --improve

    python translate.py --input strings.xlf --output strings_fr.xlf \
        --source-lang en --target-lang fr --provider echo
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.formats import load_source, save_json, save_xliff
from lib.providers import get_provider


def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def main():
    p = argparse.ArgumentParser(description="Traduction automatisée JSON/XLIFF via IA.")
    p.add_argument("--input", required=True, help="Fichier source (.json, .xlf, .xliff)")
    p.add_argument("--output", required=True, help="Fichier de sortie traduit")
    p.add_argument("--source-lang", default="en", help="Langue source (ex: en)")
    p.add_argument("--target-lang", required=True, help="Langue cible (ex: fr)")
    p.add_argument("--provider", default="anthropic", choices=["anthropic", "openai", "deepl", "echo"],
                    help="Provider utilisé pour la traduction initiale.")
    p.add_argument("--improve", action="store_true", help="Active la passe d'amélioration/relecture")
    p.add_argument("--improve-provider", choices=["anthropic", "openai", "deepl", "echo"],
                    help="Provider utilisé pour la relecture, si différent de --provider "
                         "(ex: --provider deepl --improve --improve-provider anthropic).")
    p.add_argument("--batch-size", type=int, default=25, help="Nb de segments par appel IA")
    p.add_argument("--glossary", help="Fichier JSON {terme_source: terme_cible} à imposer")
    p.add_argument("--dump-report", help="Chemin d'un JSON récap source/brouillon/final (optionnel)")
    args = p.parse_args()

    glossary = None
    if args.glossary:
        glossary = json.loads(Path(args.glossary).read_text(encoding="utf-8"))

    fmt, loaded = load_source(args.input)
    segments = loaded["segments"]
    if not segments:
        print("Aucun segment traduisible trouvé.", file=sys.stderr)
        sys.exit(1)

    print(f"[1/3] {len(segments)} segments extraits ({fmt}).")

    provider = get_provider(args.provider)
    improve_provider = get_provider(args.improve_provider) if args.improve_provider else provider

    # --- Étape traduction ---
    drafts: list[str] = []
    texts = [s["text"] for s in segments]
    for i, batch in enumerate(chunked(texts, args.batch_size)):
        print(f"[2/3] Traduction batch {i + 1} ({len(batch)} segments)...")
        drafts.extend(
            provider.translate_batch(batch, args.source_lang, args.target_lang, glossary)
        )

    # --- Étape amélioration (optionnelle) ---
    finals = drafts
    if args.improve:
        finals = []
        for i, (src_batch, draft_batch) in enumerate(
            zip(chunked(texts, args.batch_size), chunked(drafts, args.batch_size))
        ):
            print(f"[3/3] Amélioration batch {i + 1} ({len(src_batch)} segments)...")
            finals.extend(
                improve_provider.improve_batch(src_batch, draft_batch, args.target_lang, glossary)
            )
    else:
        print("[3/3] Passe d'amélioration ignorée (--improve non fourni).")

    # --- Réinjection ---
    if fmt == "json":
        translations = {seg["path"]: text for seg, text in zip(segments, finals)}
        save_json(loaded["raw"], translations, args.output)
    else:  # xliff
        pairs = [(seg["path"], text) for seg, text in zip(segments, finals)]
        save_xliff(loaded["tree"], loaded["root"], loaded["version"], pairs, args.output)

    print(f"✓ Traduction écrite dans {args.output}")

    if args.dump_report:
        report = [
            {"id": s["id"], "source": s["text"], "draft": d, "final": f}
            for s, d, f in zip(segments, drafts, finals)
        ]
        Path(args.dump_report).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"✓ Rapport détaillé écrit dans {args.dump_report}")


if __name__ == "__main__":
    main()
