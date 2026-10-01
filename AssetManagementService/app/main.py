from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Asset
from app.schemas import AssetCreate, AssetResponse, AssetUpdate
from app.services.asset_service import (
    count_assets,
    create_asset,
    delete_asset,
    get_asset_by_id,
    get_assets,
    update_asset,
)
from app.services.pdf_generator import generate_asset_management_report
from app.services.translation_loader import load_translations


app = FastAPI(title="Asset Management Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4300"],
    allow_origin_regex=(
        r"https://([a-z0-9-]+\.)?"
        r"translation-platform-frontend\.pages\.dev"
    ),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICE_ROOT = Path(__file__).resolve().parents[1]
GENERATED_REPORTS_DIRECTORY = SERVICE_ROOT / "generated-reports"


class ReportRequest(BaseModel):
    language: Literal["en", "fr", "de"]


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/reports", tags=["Reports"], response_class=FileResponse)
def create_report(
    request: ReportRequest,
    db: Session = Depends(get_db),
) -> FileResponse:
    try:
        translations = load_translations(request.language)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    assets = get_assets(db)
    asset_data = [
        {
            "name": asset.name,
            "reference": asset.reference,
            "status": asset.status,
            "tags": ", ".join(tag.name for tag in asset.tags),
        }
        for asset in assets
    ]

    output_file = (
        GENERATED_REPORTS_DIRECTORY
        / f"asset-management-report-{request.language}.pdf"
    )

    generated_file = generate_asset_management_report(
        output_path=output_file,
        report_title=translations["asset-management-report-title"],
        total_assets_label=translations["asset-management-total-assets"],
        total_assets=count_assets(db),
        assets_label=translations["asset-management-assets"],
        reference_label=translations["asset-management-reference"],
        status_label=translations["asset-management-status"],
        tags_label=translations["asset-management-tags"],
        completed_status=translations["asset-management-status-completed"],
        assets=asset_data,
    )

    return FileResponse(
        path=generated_file,
        media_type="application/pdf",
        filename=f"asset-management-report-{request.language}.pdf",
    )


@app.post(
    "/assets",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_asset(
    asset_data: AssetCreate,
    db: Session = Depends(get_db),
) -> Asset:
    try:
        return create_asset(db, asset_data)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@app.get("/assets", response_model=list[AssetResponse])
def list_assets(db: Session = Depends(get_db)) -> list[Asset]:
    return get_assets(db)


@app.get("/assets/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
) -> Asset:
    asset = get_asset_by_id(db, asset_id)

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    return asset


@app.patch("/assets/{asset_id}", response_model=AssetResponse)
def update_existing_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    db: Session = Depends(get_db),
) -> Asset:
    asset = get_asset_by_id(db, asset_id)

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    try:
        return update_asset(db, asset, asset_data)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@app.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_asset(
    asset_id: int,
    db: Session = Depends(get_db),
) -> None:
    asset = get_asset_by_id(db, asset_id)

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    delete_asset(db, asset)
