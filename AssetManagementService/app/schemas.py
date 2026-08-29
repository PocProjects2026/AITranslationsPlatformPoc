from pydantic import BaseModel, ConfigDict


class AssetCreate(BaseModel):
    name: str
    reference: str
    status: str
    owner: str | None = None
    tags: list[str] = []


class TagResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True
    )


class AssetResponse(BaseModel):
    id: int
    name: str
    reference: str
    status: str
    owner: str | None = None
    tags: list[TagResponse]

    model_config = ConfigDict(
        from_attributes=True
    )
class AssetUpdate(BaseModel):
    name: str | None = None
    reference: str | None = None
    status: str | None = None
    owner: str | None = None
    tags: list[str] | None = None