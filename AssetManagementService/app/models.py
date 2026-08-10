from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database import Base


asset_tags = Table(
    "asset_tags",
    Base.metadata,
    Column(
        "asset_id",
        ForeignKey("assets.id"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        ForeignKey("tags.id"),
        primary_key=True,
    ),
)


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    reference: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    tags: Mapped[list["Tag"]] = relationship(
        secondary=asset_tags,
        back_populates="assets",
    )


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    assets: Mapped[list["Asset"]] = relationship(
        secondary=asset_tags,
        back_populates="tags",
    )