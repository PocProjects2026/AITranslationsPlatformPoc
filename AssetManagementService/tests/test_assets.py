import os
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


def test_asset_crud(tmp_path: Path):
    database_file = tmp_path / "test-assets.db"

    test_database_url = os.getenv(
        "TEST_DATABASE_URL",
        f"sqlite:///{database_file}",
    )

    connect_args = {}

    if test_database_url.startswith("sqlite"):
        connect_args = {
            "check_same_thread": False
        }

    test_engine = create_engine(
        test_database_url,
        connect_args=connect_args,
    )

    TestSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    def override_get_db():
        db = TestSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    try:
        # CREATE
        create_response = client.post(
            "/assets",
            json={
                "name": "Test Server",
                "reference": "TEST-001",
                "status": "Active",
                "owner": "DevOps",
                "tags": [
                    "Production",
                    "Linux",
                ],
            },
        )

        assert create_response.status_code == 201

        created_asset = create_response.json()

        assert created_asset["name"] == "Test Server"
        assert created_asset["reference"] == "TEST-001"
        assert created_asset["status"] == "Active"
        assert created_asset["owner"] == "DevOps"

        asset_id = created_asset["id"]

        # READ ONE
        get_response = client.get(
            f"/assets/{asset_id}"
        )

        assert get_response.status_code == 200

        asset = get_response.json()

        assert asset["name"] == "Test Server"
        assert asset["reference"] == "TEST-001"

        # READ ALL
        list_response = client.get(
            "/assets"
        )

        assert list_response.status_code == 200

        assets = list_response.json()

        assert len(assets) == 1

        # UPDATE
        update_response = client.patch(
            f"/assets/{asset_id}",
            json={
                "status": "Inactive",
                "owner": "Cloud Team",
            },
        )

        assert update_response.status_code == 200

        updated_asset = update_response.json()

        assert updated_asset["status"] == "Inactive"
        assert updated_asset["owner"] == "Cloud Team"

        # DELETE
        delete_response = client.delete(
            f"/assets/{asset_id}"
        )

        assert delete_response.status_code == 204

        # VERIFY DELETE
        missing_response = client.get(
            f"/assets/{asset_id}"
        )

        assert missing_response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        test_engine.dispose()