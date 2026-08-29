from pathlib import Path

import boto3

from app.config import (
    R2_ACCESS_KEY_ID,
    R2_BUCKET,
    R2_ENDPOINT,
    R2_SECRET_ACCESS_KEY,
)


def create_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )


def ensure_version_does_not_exist(
    prefix: str,
    version: str,
) -> None:
    client = create_r2_client()

    version_prefix = f"{prefix}/{version}/"

    existing = client.list_objects_v2(
        Bucket=R2_BUCKET,
        Prefix=version_prefix,
        MaxKeys=1,
    )

    if existing.get("KeyCount", 0) > 0:
        raise ValueError(
            f"Translation version already exists in R2: "
            f"{version_prefix}"
        )


def upload_translation_artifact(
    file_path: Path,
    prefix: str,
    version: str,
) -> str:
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Artifact '{file_path}' was not found."
        )

    object_key = (
        f"{prefix}/"
        f"{version}/"
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
    files: list[Path],
    prefix: str,
    version: str,
    immutable: bool = True,
) -> list[str]:

    missing_files = [
        file_path.name
        for file_path in files
        if not file_path.is_file()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Missing translation artifacts: "
            + ", ".join(missing_files)
        )

    if immutable:
        ensure_version_does_not_exist(
            prefix,
            version,
        )

    uploaded_keys = []

    for file_path in files:
        object_key = upload_translation_artifact(
            file_path=file_path,
            prefix=prefix,
            version=version,
        )

        uploaded_keys.append(object_key)

    return uploaded_keys