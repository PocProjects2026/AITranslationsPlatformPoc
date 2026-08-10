from sqlalchemy import func, select
from sqlalchemy.orm import Session , selectinload

from app.models import Asset


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