from io import BytesIO

from fastapi.testclient import TestClient
from pypdf import PdfReader
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Asset,Tag


def test_report_uses_asset_count_from_database(
    tmp_path,
) -> None:
    database_file = (
        tmp_path
        / "integration-test.db"
    )

    test_engine = create_engine(
        f"sqlite:///{database_file}",
        connect_args={
            "check_same_thread": False,
        },
    )

    TestSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(
        bind=test_engine
    )
    with TestSessionLocal() as db:
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

    database = Asset(
        name="Database-01",
        reference="DB-001",
        status="Active",
        tags=[
            production_tag,
            critical_tag,
        ],
    )

    laptop = Asset(
        name="Laptop-01",
        reference="LAP-001",
        status="Inactive",
        tags=[
            linux_tag,
        ],
    )

    db.add_all(
        [
            server,
            database,
            laptop,
        ]
    )

    db.commit()

    def override_get_db():
        db = TestSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = (
        override_get_db
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/reports",
            json={
                "language": "en",
            },
        )

        assert response.status_code == 200
        assert (
            response.headers["content-type"]
            == "application/pdf"
        )

        pdf_reader = PdfReader(
            BytesIO(response.content)
        )

        pdf_text = "\n".join(
            page.extract_text() or ""
            for page in pdf_reader.pages
        )

        assert "Total assets: 3" in pdf_text
        assert "Server-01" in pdf_text
        assert "SRV-001" in pdf_text
        assert "Production" in pdf_text
        assert "Critical" in pdf_text
        assert "Linux" in pdf_text

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        test_engine.dispose()