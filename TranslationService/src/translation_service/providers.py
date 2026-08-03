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

def _glossary_note(glossary: Optional[Dict[str, str]]) -> str:
    if not glossary:
        return ""
    lines = "\n".join(f"- {k} -> {v}" for k, v in glossary.items())
    return f"\n\nRespect these forced glossary terms:\n{lines}"

def _build_translate_prompt(texts, source_lang, target_lang, glossary):
    numbered = "\n".join(f"{i}: {t}" for i, t in enumerate(texts))
    return f"""You are a professional translator. Translate each segment from {source_lang} to {target_lang}.

Strict rules:
- Keep ALL placeholders exactly as they are (e.g. {{name}}, %s, <tag>...</tag>).
- Reply ONLY with a JSON object {{"0": "...", "1": "...", ...}}
  where each key is the segment index.{_glossary_note(glossary)}

Segments:
{numbered}"""

def _parse_json_map(raw: str, n: int) -> List[str]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        if raw.lower().startswith("json"):
            raw = raw.split("\n", 1)[1]
    data = json.loads(raw)
    return [data[str(i)] for i in range(n)]

class AnthropicProvider(TranslationProvider):
    name = "anthropic"

    def __init__(self, model: str = "claude-sonnet-3-5"):
        import anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def translate_batch(self, texts, source_lang, target_lang, glossary=None):
        prompt = _build_translate_prompt(texts, source_lang, target_lang, glossary)
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = "".join(b.text for b in resp.content if b.type == "text")
        return _parse_json_map(raw, len(texts))

class OpenAIProvider(TranslationProvider):
    name = "openai"

    def __init__(self, model: str = "gpt-4o"):
        import openai
        api_key = os.environ.get("OPENAI_API_KEY", "")
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def translate_batch(self, texts, source_lang, target_lang, glossary=None):
        prompt = _build_translate_prompt(texts, source_lang, target_lang, glossary)
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content or "{}"
        return _parse_json_map(raw, len(texts))

class FakeProvider(TranslationProvider):
    name = "fake"

    def translate_batch(self, texts, source_lang, target_lang, glossary=None):
        # Generates deterministic fake translations for unit testing
        results = []
        for t in texts:
            # simple mock translation logic
            translated = f"[translated:{target_lang}] {t}"
            if glossary:
                for k, v in glossary.items():
                    translated = translated.replace(k, v)
            results.append(translated)
        return results

PROVIDERS = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "fake": FakeProvider,
}

def get_provider(name: str) -> TranslationProvider:
    return PROVIDERS[name]()
