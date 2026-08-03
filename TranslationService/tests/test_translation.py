import pytest
from translation_service.formats import parse_json, build_json_artifact, parse_xliff, build_xliff_artifact
from translation_service.providers import FakeProvider
from translation_service.pipeline import rank_candidates

def test_json_pipeline():
    source_json = '{"home": {"title": "Hello {{name}}!"}}'
    parsed = parse_json(source_json)
    
    assert len(parsed["segments"]) == 1
    assert parsed["segments"][0]["text"] == "Hello {{name}}!"
    
    provider = FakeProvider()
    drafts = provider.translate_batch([parsed["segments"][0]["text"]], "en", "fr")
    
    assert drafts[0] == "[translated:fr] Hello {{name}}!"
    
    ranked = rank_candidates(parsed["segments"][0]["text"], drafts)
    assert ranked[0]["score"] == 100.0
    
    translations = {parsed["segments"][0]["path"]: ranked[0]["text"]}
    result = build_json_artifact(parsed["raw"], translations)
    
    assert '"title": "[translated:fr] Hello {{name}}!"' in result

def test_xliff_pipeline():
    source_xliff = b'''<?xml version="1.0" encoding="UTF-8"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
  <file source-language="en" target-language="fr" datatype="plaintext" original="ng2.template">
    <body>
      <trans-unit id="123" datatype="html">
        <source>Welcome <x id="INTERPOLATION" equiv-text="{{name}}"/> to our app.</source>
      </trans-unit>
    </body>
  </file>
</xliff>'''

    parsed = parse_xliff(source_xliff)
    assert len(parsed["segments"]) == 1
    assert "Welcome <x id=" in parsed["segments"][0]["text"]
    
    provider = FakeProvider()
    drafts = provider.translate_batch([parsed["segments"][0]["text"]], "en", "fr")
    
    translations = {parsed["segments"][0]["path"]: drafts[0]}
    result = build_xliff_artifact(parsed["tree"], parsed["version"], translations)
    
    assert b'<target>' in result
    assert b'[translated:fr] Welcome' in result
    assert b'<x id="INTERPOLATION"' in result

def test_pipeline_validation_penalties():
    source = "Hello {{name}}!"
    candidates = [
        "Bonjour {{name}}!", # Perfect
        "Bonjour!", # Missing placeholder
        "Bonjour {{name}} {{other}}!", # Extra placeholder
    ]
    ranked = rank_candidates(source, candidates)
    
    assert ranked[0]["text"] == "Bonjour {{name}}!"
    assert ranked[0]["score"] == 100.0
    assert ranked[1]["score"] < 100.0
    assert ranked[2]["score"] < 100.0
