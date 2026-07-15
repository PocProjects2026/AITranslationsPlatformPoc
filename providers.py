"""
Providers de traduction interchangeables.

Chaque provider implémente :
    - translate_batch(texts, source_lang, target_lang, glossary=None) -> list[str]
    - improve_batch(source_texts, drafts, target_lang, glossary=None) -> list[str]

Pour changer de provider : --provider anthropic|openai|deepl|echo (voir translate.py)
"""
from __future__ import annotations

import json
import os
import re
from typing import List, Optional, Dict


class TranslationProvider:
    name = "base"

    def translate_batch(
        self, texts: List[str], source_lang: str, target_lang: str,
        glossary: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        raise NotImplementedError

    def improve_batch(
        self, source_texts: List[str], drafts: List[str], target_lang: str,
        glossary: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        raise NotImplementedError


def _glossary_note(glossary: Optional[Dict[str, str]]) -> str:
    if not glossary:
        return ""
    lines = "\n".join(f"- {k} -> {v}" for k, v in glossary.items())
    return f"\n\nRespecte ce glossaire de termes imposés :\n{lines}"


def _build_translate_prompt(texts, source_lang, target_lang, glossary):
    numbered = "\n".join(f"{i}: {t}" for i, t in enumerate(texts))
    return f"""Tu es un traducteur professionnel. Traduis chaque segment de {source_lang} vers {target_lang}.

Règles strictes :
- Conserve EXACTEMENT les placeholders (ex: {{name}}, %s, {{{{var}}}}, {{0}}, balises HTML) sans les traduire.
- Conserve le ton et le registre d'origine (UI produit = concis et naturel).
- Ne rajoute aucun commentaire, aucune explication.
- Réponds UNIQUEMENT avec un objet JSON de la forme {{"0": "...", "1": "...", ...}}
  où chaque clé est l'index du segment et la valeur sa traduction.{_glossary_note(glossary)}

Segments à traduire :
{numbered}"""


def _build_improve_prompt(source_texts, drafts, target_lang, glossary):
    pairs = "\n".join(
        f"{i}: SOURCE: {s}\n   DRAFT: {d}" for i, (s, d) in enumerate(zip(source_texts, drafts))
    )
    return f"""Tu es un relecteur professionnel de traductions vers le {target_lang}.
Pour chaque paire SOURCE/DRAFT ci-dessous, corrige la traduction DRAFT si besoin :
fautes, contresens, ton peu naturel, incohérence terminologique, placeholders cassés.
Si la traduction est déjà bonne, renvoie-la telle quelle.

Réponds UNIQUEMENT avec un objet JSON {{"0": "...", "1": "...", ...}}.{_glossary_note(glossary)}

{pairs}"""


def _parse_json_map(raw: str, n: int) -> List[str]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        if raw.lower().startswith("json"):
            raw = raw.split("\n", 1)[1]
    data = json.loads(raw)
    return [data[str(i)] for i in range(n)]


# Placeholders courants en i18n : {name}, {{name}}, %s, %1$s, %(name)s, {0}
_PLACEHOLDER_RE = re.compile(
    r"(\{\{[^{}]+\}\}|\{[^{}]+\}|%\([a-zA-Z_][a-zA-Z0-9_]*\)[sd]|%\d*\$?[sd])"
)


def _protect_placeholders(text: str) -> str:
    """Enveloppe les placeholders dans <x>...</x> pour que DeepL ne les traduise pas."""
    return _PLACEHOLDER_RE.sub(lambda m: f"<x>{m.group(0)}</x>", text)


def _unprotect_placeholders(text: str) -> str:
    return text.replace("<x>", "").replace("</x>", "")


class AnthropicProvider(TranslationProvider):
    name = "anthropic"

    def __init__(self, model: str = "claude-sonnet-4-6"):
        try:
            import anthropic
        except ImportError as e:
            raise RuntimeError(
                "Le package 'anthropic' n'est pas installé. Lance: pip install anthropic"
            ) from e
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("Variable d'environnement ANTHROPIC_API_KEY manquante.")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def _call(self, prompt: str) -> str:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in resp.content if b.type == "text")

    def translate_batch(self, texts, source_lang, target_lang, glossary=None):
        prompt = _build_translate_prompt(texts, source_lang, target_lang, glossary)
        raw = self._call(prompt)
        return _parse_json_map(raw, len(texts))

    def improve_batch(self, source_texts, drafts, target_lang, glossary=None):
        prompt = _build_improve_prompt(source_texts, drafts, target_lang, glossary)
        raw = self._call(prompt)
        return _parse_json_map(raw, len(drafts))


class OpenAIProvider(TranslationProvider):
    """Squelette prêt à remplir. pip install openai, puis complète _call()."""
    name = "openai"

    def __init__(self, model: str = "gpt-4o"):
        try:
            import openai  # noqa: F401
        except ImportError as e:
            raise RuntimeError("pip install openai") from e
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Variable d'environnement OPENAI_API_KEY manquante.")
        import openai
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def _call(self, prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return resp.choices[0].message.content

    def translate_batch(self, texts, source_lang, target_lang, glossary=None):
        prompt = _build_translate_prompt(texts, source_lang, target_lang, glossary)
        raw = self._call(prompt)
        return _parse_json_map(raw, len(texts))

    def improve_batch(self, source_texts, drafts, target_lang, glossary=None):
        prompt = _build_improve_prompt(source_texts, drafts, target_lang, glossary)
        raw = self._call(prompt)
        return _parse_json_map(raw, len(drafts))


class DeepLProvider(TranslationProvider):
    """
    Utilise l'API DeepL (free ou pro). Détecte automatiquement l'endpoint :
    une clé free se termine toujours par ':fx' -> api-free.deepl.com,
    sinon -> api.deepl.com.

    Important : DeepL est un moteur de traduction, pas un LLM. Il n'y a pas
    de vraie relecture/amélioration côté DeepL. improve_batch() ici est un
    fallback qui renvoie le brouillon tel quel (avec un avertissement) —
    pour une vraie passe d'amélioration, combine avec --provider anthropic
    en 2 passes, ou utilise le provider 'deepl+anthropic' (voir plus bas).
    """
    name = "deepl"

    def __init__(self):
        try:
            import requests  # noqa: F401
        except ImportError as e:
            raise RuntimeError("Le package 'requests' n'est pas installé. Lance: pip install requests") from e
        api_key = os.environ.get("DEEPL_API_KEY")
        if not api_key:
            raise RuntimeError("Variable d'environnement DEEPL_API_KEY manquante.")
        self.api_key = api_key
        self.base_url = (
            "https://api-free.deepl.com/v2/translate"
            if api_key.endswith(":fx")
            else "https://api.deepl.com/v2/translate"
        )
        self._warned_glossary = False
        self._warned_improve = False

    def translate_batch(self, texts, source_lang, target_lang, glossary=None):
        import requests

        if glossary and not self._warned_glossary:
            print(
                "[deepl] Note: --glossary n'est pas appliqué automatiquement avec DeepL "
                "(nécessite de créer un glossaire DeepL au préalable via l'API). Ignoré.",
            )
            self._warned_glossary = True

        protected = [_protect_placeholders(t) for t in texts]
        resp = requests.post(
            self.base_url,
            headers={"Authorization": f"DeepL-Auth-Key {self.api_key}"},
            data={
                "text": protected,
                "source_lang": source_lang.upper(),
                "target_lang": target_lang.upper(),
                "tag_handling": "xml",
                "ignore_tags": "x",
                "preserve_formatting": "1",
            },
        )
        resp.raise_for_status()
        translations = [t["text"] for t in resp.json()["translations"]]
        return [_unprotect_placeholders(t) for t in translations]

    def improve_batch(self, source_texts, drafts, target_lang, glossary=None):
        if not self._warned_improve:
            print(
                "[deepl] Note: DeepL n'offre pas de passe de relecture/amélioration. "
                "Le brouillon est renvoyé tel quel. Utilise --provider anthropic pour "
                "une vraie relecture IA, ou combine les deux providers manuellement.",
            )
            self._warned_improve = True
        return drafts


class EchoProvider(TranslationProvider):
    """Provider factice pour tester le pipeline (extraction/réinjection) sans API key."""
    name = "echo"

    def translate_batch(self, texts, source_lang, target_lang, glossary=None):
        return [f"[{target_lang}] {t}" for t in texts]

    def improve_batch(self, source_texts, drafts, target_lang, glossary=None):
        return [f"{d} (revu)" for d in drafts]


PROVIDERS = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "deepl": DeepLProvider,
    "echo": EchoProvider,
}


def get_provider(name: str) -> TranslationProvider:
    if name not in PROVIDERS:
        raise ValueError(f"Provider inconnu: {name}. Choix: {list(PROVIDERS)}")
    return PROVIDERS[name]()
