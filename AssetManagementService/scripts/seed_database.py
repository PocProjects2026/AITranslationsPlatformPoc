from sqlalchemy import select

from app.database import SessionLocal
from app.models import Asset, Tag


def main() -> None:
    db = SessionLocal()

    try:
        existing_asset = db.scalar(
            select(Asset).where(
                Asset.reference == "SRV-001"
            )
        )

        if existing_asset:
            print("Sample data already exists.")
            return

        production_tag = Tag(
            name="Production"
        )

        critical_tag = Tag(
            name="Critical"
        )

        linux_tag = Tag(
            name="Linux"
        )

        server = Asset(
            name="Server-01",
            reference="SRV-001",
            status="Active",
            tags=[
                production_tag,
                critical_tag,
                linux_tag,
            ],
        )

        db.add(server)

        db.commit()

        print("Sample data inserted successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    main()