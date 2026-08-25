from pathlib import Path

import boto3

from app.config import (
    R2_ACCESS_KEY_ID,
    R2_BUCKET,
    R2_ENDPOINT,
    R2_SECRET_ACCESS_KEY,
    R2_TRANSLATION_PREFIX,
    TRANSLATION_VERSION,
)


def create_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )


def upload_translation_artifact(
    file_path: Path,
) -> str:
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Artifact '{file_path}' was not found."
        )

    object_key = (
        f"{R2_TRANSLATION_PREFIX}/"
        f"{TRANSLATION_VERSION}/"
        f"{file_path.name}"
    )

    client = create_r2_client()

    client.upload_file(
        str(file_path),
        R2_BUCKET,
        object_key,
    )

    return object_key

def publish_translation_version(
    artifacts_directory: Path,
) -> list[str]:
    required_files = [
        artifacts_directory / "messages.en.json",
        artifacts_directory / "messages.fr.json",
        artifacts_directory / "messages.de.json",
    ]

    missing_files = [
        file_path.name
        for file_path in required_files
        if not file_path.is_file()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Missing translation artifacts: "
            + ", ".join(missing_files)
        )

    uploaded_keys = []

    for file_path in required_files:
        object_key = upload_translation_artifact(
            file_path
        )

        uploaded_keys.append(object_key)

    return uploaded_keys