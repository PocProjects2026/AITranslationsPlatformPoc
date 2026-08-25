from pathlib import Path

from app.services.r2_uploader import (
    publish_translation_version,
)


artifacts_directory = Path(
    "artifacts/asset-management"
)

uploaded_keys = publish_translation_version(
    artifacts_directory
)

for object_key in uploaded_keys:
    print(f"Uploaded: {object_key}")