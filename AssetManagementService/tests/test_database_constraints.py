import pytest

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Asset, Tag


def create_test_database():
    engine = create_engine(
        "sqlite:///:memory:"
    )

    Base.metadata.create_all(
        bind=engine
    )

    return engine


def test_asset_reference_must_be_unique() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        first_asset = Asset(
            name="Server-01",
            reference="SRV-001",
            status="Active",
        )

        db.add(first_asset)
        db.commit()

        second_asset = Asset(
            name="Server-02",
            reference="SRV-001",
            status="Active",
        )

        db.add(second_asset)

        with pytest.raises(IntegrityError):
            db.commit()


def test_tag_name_must_be_unique() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        first_tag = Tag(
            name="Production"
        )

        db.add(first_tag)
        db.commit()

        second_tag = Tag(
            name="Production"
        )

        db.add(second_tag)

        with pytest.raises(IntegrityError):
            db.commit()


def test_asset_name_is_required() -> None:
    engine = create_test_database()

    with Session(engine) as db:
        asset = Asset(
            name=None,
            reference="SRV-002",
            status="Active",
        )

        db.add(asset)

        with pytest.raises(IntegrityError):
            db.commit()