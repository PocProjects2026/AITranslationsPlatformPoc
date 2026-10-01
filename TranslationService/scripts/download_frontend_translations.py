import sys
from pathlib import Path

import boto3

from app.config import (
    R2_ACCESS_KEY_ID,
    R2_BUCKET,
    R2_ENDPOINT,
    R2_SECRET_ACCESS_KEY,
)


SERVICE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = SERVICE_ROOT.parent

FRONTEND_LOCALE_DIRECTORY = (
    REPOSITORY_ROOT
    / "FrontendApp"
    / "src"
    / "locale"
)


def create_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )


def download_translation_version(
    version: str,
) -> None:
    client = create_r2_client()

    files = [
        "messages.xlf",
        "messages.fr.xlf",
        "messages.de.xlf",
    ]

    FRONTEND_LOCALE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    for file_name in files:
        object_key = (
            f"translations/"
            f"{version}/"
            f"{file_name}"
        )

        destination = (
            FRONTEND_LOCALE_DIRECTORY
            / file_name
        )

        print(
            f"Downloading {object_key}"
        )

        client.download_file(
            R2_BUCKET,
            object_key,
            str(destination),
        )

        print(
            f"Installed: {destination}"
        )

    print()
    print(
        f"Frontend translation version "
        f"{version} installed successfully."
    )


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: "
            "python -m scripts.download_frontend_translations "
            "version-X"
        )

    version = sys.argv[1]

    download_translation_version(
        version
    )


if __name__ == "__main__":
    main()