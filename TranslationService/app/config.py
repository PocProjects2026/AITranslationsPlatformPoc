import os

from dotenv import load_dotenv


load_dotenv()

AZURE_TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY")
AZURE_TRANSLATOR_REGION = os.getenv("AZURE_TRANSLATOR_REGION")
AZURE_TRANSLATOR_ENDPOINT = os.getenv("AZURE_TRANSLATOR_ENDPOINT")

R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_BUCKET = os.getenv("R2_BUCKET")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_TRANSLATION_PREFIX = os.getenv(
    "R2_TRANSLATION_PREFIX",
    "asset-management",
)
TRANSLATION_VERSION = os.getenv(
    "TRANSLATION_VERSION",
    "version-1",
)