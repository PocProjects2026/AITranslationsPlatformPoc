from fastapi import FastAPI
from pydantic import BaseModel

from app.services.azure_translator import AzureTranslator


app = FastAPI(
    title="TranslationService",
    version="0.1.0",
)


class HealthResponse(BaseModel):
    status: str


class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str


class TranslationResponse(BaseModel):
    translated_text: str


@app.get(
    "/health",
    response_model=HealthResponse,
)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post(
    "/translate",
    response_model=TranslationResponse,
)
async def translate(
    request: TranslationRequest,
) -> TranslationResponse:
    translator = AzureTranslator()

    translated_text = await translator.translate(
        text=request.text,
        source_language=request.source_language,
        target_language=request.target_language,
    )

    return TranslationResponse(
        translated_text=translated_text
    )