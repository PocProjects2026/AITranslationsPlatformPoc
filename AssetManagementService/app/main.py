from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.pdf_generator import generate_asset_management_report
from app.services.translation_loader import load_translations
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.asset_service import count_assets,get_assets

app = FastAPI(
    title="Asset Management Service",
    version="0.1.0",
)


SERVICE_ROOT = Path(__file__).resolve().parents[1]

GENERATED_REPORTS_DIRECTORY = (
    SERVICE_ROOT
    / "generated-reports"
)


class ReportRequest(BaseModel):
    language: Literal["en", "fr", "de"]


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/reports",
    tags=["Reports"],
    response_class=FileResponse,
)
def create_report(request: ReportRequest,db: Session = Depends(get_db)) -> FileResponse:
    translations = load_translations(
        request.language
    )
    total_assets = count_assets(db)
    assets = get_assets(db)
    asset_data = [
    {
        "name": asset.name,
        "reference": asset.reference,
        "status": asset.status,
        "tags": ", ".join(
            tag.name for tag in asset.tags
        ),
    }
    for asset in assets
]

    output_file = (
        GENERATED_REPORTS_DIRECTORY
        / f"asset-management-report-{request.language}.pdf"
    )

    generated_file = generate_asset_management_report(
    output_path=output_file,
    report_title=translations[
        "asset-management-report-title"
    ],
    report_description=translations[
        "asset-management-report-description"
    ],
    total_assets_label=translations[
        "asset-management-total-assets"
    ],
    total_assets=total_assets,
    assets_label=translations[
        "asset-management-assets"
    ],
    reference_label=translations[
        "asset-management-reference"
    ],
    status_label=translations[
        "asset-management-status"
    ],
    tags_label=translations[
        "asset-management-tags"
    ],
    completed_status=translations[
        "asset-management-status-completed"
    ],
    assets=asset_data,
)

    return FileResponse(
        path=generated_file,
        media_type="application/pdf",
        filename=(
            f"asset-management-report-description"
            f"{request.language}.pdf"
        ),
    )