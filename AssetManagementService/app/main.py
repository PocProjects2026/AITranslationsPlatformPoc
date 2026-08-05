from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.pdf_generator import generate_asset_management_report
from app.services.translation_loader import load_translations


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
def create_report(request: ReportRequest) -> FileResponse:
    translations = load_translations(
        request.language
    )

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
        total_assets=3,
        status_label=translations[
            "asset-management-status"
        ],
        completed_status=translations[
            "asset-management-status-completed"
        ],
    )

    return FileResponse(
        path=generated_file,
        media_type="application/pdf",
        filename=(
            f"asset-management-report-description"
            f"{request.language}.pdf"
        ),
    )