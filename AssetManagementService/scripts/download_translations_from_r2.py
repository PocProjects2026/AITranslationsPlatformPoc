import os
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError


SUPPORTED_LANGUAGES = ("en", "fr", "de")

SERVICE_ROOT = Path(__file__).resolve().parents[1]

TRANSLATIONS_DIRECTORY = (
    SERVICE_ROOT
    / "app"
    / "translations"
)


def get_required_environment_variable(name: str) -> str:
    """
    Read a required environment variable.

    Stop the script with a clear error when the variable is missing.
    """
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


def main() -> None:
    r2_endpoint = get_required_environment_variable(
        "R2_ENDPOINT"
    ).rstrip("/")

    r2_bucket = get_required_environment_variable(
        "R2_BUCKET"
    )

    access_key_id = get_required_environment_variable(
        "R2_ACCESS_KEY_ID"
    )

    secret_access_key = get_required_environment_variable(
        "R2_SECRET_ACCESS_KEY"
    )

    translation_version = get_required_environment_variable(
        "TRANSLATION_VERSION"
    ).strip("/")

    translation_prefix = os.getenv(
        "R2_TRANSLATION_PREFIX",
        "asset-management",
    ).strip("/")

    r2_client = boto3.client(
        "s3",
        endpoint_url=r2_endpoint,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name="auto",
    )

    TRANSLATIONS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    for language in SUPPORTED_LANGUAGES:
        filename = f"messages.{language}.json"

        object_key = (
            f"{translation_prefix}/"
            f"{translation_version}/"
            f"{filename}"
        )

        destination_file = (
            TRANSLATIONS_DIRECTORY
            / filename
        )

        print(
            f"Downloading {object_key} "
            f"to {destination_file}"
        )

        r2_client.download_file(
            r2_bucket,
            object_key,
            str(destination_file),
        )

    print(
        "All translation files were "
        "downloaded successfully."
    )


if __name__ == "__main__":
    try:
        main()

    except (
        RuntimeError,
        BotoCoreError,
        ClientError,
    ) as error:
        raise SystemExit(
            f"Translation download failed: {error}"
        ) from error