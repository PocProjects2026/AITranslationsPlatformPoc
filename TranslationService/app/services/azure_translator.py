import httpx

from app.config import (
    AZURE_TRANSLATOR_ENDPOINT,
    AZURE_TRANSLATOR_KEY,
    AZURE_TRANSLATOR_REGION,
)


class AzureTranslator:
    def __init__(self) -> None:
        self.endpoint = AZURE_TRANSLATOR_ENDPOINT.rstrip("/")
        self.key = AZURE_TRANSLATOR_KEY
        self.region = AZURE_TRANSLATOR_REGION

    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        translations = await self.translate_many(
            texts=[text],
            source_language=source_language,
            target_language=target_language,
        )

        return translations[0]

    async def translate_many(
        self,
        texts: list[str],
        source_language: str,
        target_language: str,
    ) -> list[str]:
        if not texts:
            return []

        url = f"{self.endpoint}/translate"

        params = {
            "api-version": "3.0",
            "from": source_language,
            "to": target_language,
        }

        headers = {
            "Ocp-Apim-Subscription-Key": self.key,
            "Ocp-Apim-Subscription-Region": self.region,
            "Content-Type": "application/json",
        }

        body = [
            {"text": text}
            for text in texts
        ]

        timeout = httpx.Timeout(
            connect=30.0,
            read=30.0,
            write=30.0,
            pool=30.0,
        )

        async with httpx.AsyncClient(
            timeout=timeout
        ) as client:
            response = await client.post(
                url,
                params=params,
                headers=headers,
                json=body,
            )

        response.raise_for_status()

        data = response.json()

        translated_texts = [
            item["translations"][0]["text"]
            for item in data
        ]

        if len(translated_texts) != len(texts):
            raise ValueError(
                "Azure returned an unexpected number of translations."
            )

        return translated_texts