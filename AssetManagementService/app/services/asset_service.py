from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Asset, Tag
from app.schemas import AssetCreate,AssetUpdate

def count_assets(db: Session) -> int:
    statement = select(
        func.count(Asset.id)
    )

    total_assets = db.scalar(statement)

    return total_assets or 0


def get_assets(db: Session) -> list[Asset]:
    statement = select(Asset).options(
        selectinload(Asset.tags)
    )

    assets = db.scalars(statement).all()

    return list(assets)

def create_asset(
    db: Session,
    asset_data: AssetCreate,
) -> Asset:

    existing_asset = db.scalar(
        select(Asset).where(
            Asset.reference == asset_data.reference
        )
    )

    if existing_asset:
        raise ValueError(
            "An asset with this reference already exists."
        )

    tags = []

    unique_tag_names = dict.fromkeys(
        asset_data.tags
    )

    for tag_name in unique_tag_names:
        tag = db.scalar(
            select(Tag).where(
                Tag.name == tag_name
            )
        )

        if tag is None:
            tag = Tag(
                name=tag_name
            )

            db.add(tag)

        tags.append(tag)

    asset = Asset(
        name=asset_data.name,
        reference=asset_data.reference,
        status=asset_data.status,
        owner=asset_data.owner,
        tags=tags,
    )

    db.add(asset)
    db.commit()
    db.refresh(asset)

    return asset

def get_asset_by_id(
    db: Session,
    asset_id: int,
) -> Asset | None:

    statement = (
        select(Asset)
        .options(selectinload(Asset.tags))
        .where(Asset.id == asset_id)
    )

    return db.scalar(statement)

def update_asset(
    db: Session,
    asset: Asset,
    asset_data: AssetUpdate,
) -> Asset:

    update_data = asset_data.model_dump(
        exclude_unset=True
    )

    if "reference" in update_data:
        existing_asset = db.scalar(
            select(Asset).where(
                Asset.reference == update_data["reference"],
                Asset.id != asset.id,
            )
        )

        if existing_asset:
            raise ValueError(
                "An asset with this reference already exists."
            )

    if "name" in update_data:
        asset.name = update_data["name"]

    if "reference" in update_data:
        asset.reference = update_data["reference"]

    if "status" in update_data:
        asset.status = update_data["status"]

    if "owner" in update_data:
        asset.owner = update_data["owner"]

    if "tags" in update_data:
        tags = []

        unique_tag_names = dict.fromkeys(
            update_data["tags"]
        )

        for tag_name in unique_tag_names:
            tag = db.scalar(
                select(Tag).where(
                    Tag.name == tag_name
                )
            )

            if tag is None:
                tag = Tag(name=tag_name)
                db.add(tag)

            tags.append(tag)

        asset.tags = tags

    db.commit()
    db.refresh(asset)

    return asset

def delete_asset(
    db: Session,
    asset: Asset,
) -> None:
    db.delete(asset)
    db.commit()