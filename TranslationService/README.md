# TranslationService

Python service foundation for accepting translation source files, producing candidate
translations, ranking them, and generating consumer-ready artifacts.

## Local development

Requires Python 3.12 or later.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
uvicorn translation_service.main:app --reload
```

The initial endpoint is available at `GET /health`.

## Planned service responsibilities

- Parse XLIFF from FrontendApp and JSON source messages from backend services.
- Generate translation candidates through a provider abstraction.
- Reject unsafe placeholders or tags, apply glossary rules, and rank valid candidates.
- Publish localized XLIFF and JSON artifacts with a versioned manifest.

`samples/` contains consumer input fixtures, `evaluation/` holds curated quality data,
and `artifacts/` is reserved for generated output. CI/CD and deployment configuration
will be added through their separate user stories.
