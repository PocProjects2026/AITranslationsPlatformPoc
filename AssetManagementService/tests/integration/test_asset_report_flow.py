from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from pypdf import PdfReader
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


def test_created_asset_appears_in_report(tmp_path: Path):
    database_file = tmp_path / "test-asset-report.db"

    test_engine = create_engine(
        f"sqlite:///{database_file}",
        connect_args={"check_same_thread": False},
    )

    TestSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    try:
        # 1. Create an Asset through the API
        create_response = client.post(
            "/assets",
            json={
                "name": "Integration Server",
                "reference": "INT-001",
                "status": "Active",
                "owner": "DevOps Team",
                "tags": [
                    "Production",
                    "Linux",
                ],
            },
        )

        assert create_response.status_code == 201

        # 2. Generate the PDF
        report_response = client.post(
            "/reports",
            json={
                "language": "en"
            },
        )

        assert report_response.status_code == 200
        assert report_response.headers["content-type"] == "application/pdf"

        # 3. Read text from the generated PDF
        reader = PdfReader(
            BytesIO(report_response.content)
        )

        pdf_text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

        # 4. Verify our Asset appears in the PDF
        assert "Integration Server" in pdf_text
        assert "INT-001" in pdf_text
        assert "Production" in pdf_text
        assert "Linux" in pdf_text

    finally:
        app.dependency_overrides.clear()
        test_engine.dispose()