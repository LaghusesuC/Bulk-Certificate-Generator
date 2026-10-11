
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Recipient
from app.services.certificate_generator import generate_certificate


@pytest.fixture
def client_and_db(tmp_path, monkeypatch):
    # Create an isolated in-memory test database.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Make the background processor use the test database too.
    monkeypatch.setattr(
        "app.services.job_processor.SessionLocal",
        TestSessionLocal,
    )

    # Store test PDFs in a temporary directory.
    output_dir = tmp_path / "certificates"
    output_dir.mkdir()

    monkeypatch.setattr(
        "app.services.certificate_generator.OUTPUT_DIR",
        output_dir,
    )

    client = TestClient(app)

    yield client, TestSessionLocal

    client.close()
    app.dependency_overrides.clear()
    test_engine.dispose()


def create_test_job(client):
    response = client.post(
        "/api/v1/jobs",
        json={
            "event_name": "Annual Tech Conference",
            "course_name": "Python Development",
            "issue_date": "2026-10-11",
            "recipients": [
                {
                    "name": "Arun Kumar",
                    "email": "arun@example.com",
                },
                {
                    "name": "Priya S",
                    "email": "priya@example.com",
                },
            ],
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def test_create_job_and_download_certificate(client_and_db):
    client, TestSessionLocal = client_and_db

    job_id = create_test_job(client)

    # Background processing should finish before the test continues.
    status_response = client.get(f"/api/v1/jobs/{job_id}")

    assert status_response.status_code == 200
    assert status_response.json()["status"] == "completed"
    assert status_response.json()["completed_count"] == 2
    assert status_response.json()["failed_count"] == 0

    with TestSessionLocal() as db:
        recipients = db.query(Recipient).filter(
            Recipient.job_id == job_id
        ).all()

        assert len(recipients) == 2
        recipient_id = recipients[0].id

    download_response = client.get(
        f"/api/v1/jobs/{job_id}/certificates/{recipient_id}"
    )

    assert download_response.status_code == 200
    assert download_response.content.startswith(b"%PDF-")


def test_one_recipient_failure_does_not_stop_others(
    client_and_db, monkeypatch
):
    client, TestSessionLocal = client_and_db

    def generate_with_one_failure(
        recipient_name,
        course_name,
        event_name,
        issue_date,
        recipient_id,
    ):
        if recipient_name == "Arun Kumar":
            raise RuntimeError("Simulated PDF generation failure")

        return generate_certificate(
            recipient_name=recipient_name,
            course_name=course_name,
            event_name=event_name,
            issue_date=issue_date,
            recipient_id=recipient_id,
        )

    monkeypatch.setattr(
        "app.services.job_processor.generate_certificate",
        generate_with_one_failure,
    )

    job_id = create_test_job(client)

    response = client.get(f"/api/v1/jobs/{job_id}")

    assert response.status_code == 200
    result = response.json()

    assert result["status"] == "completed_with_errors"
    assert result["completed_count"] == 1
    assert result["failed_count"] == 1

    with TestSessionLocal() as db:
        recipients = db.query(Recipient).filter(
            Recipient.job_id == job_id
        ).all()

        failed = next(r for r in recipients if r.name == "Arun Kumar")
        successful = next(r for r in recipients if r.name == "Priya S")

        assert failed.status == "failed"
        assert failed.error_message is not None
        assert successful.status == "completed"
        assert successful.certificate_path is not None


def test_create_job_rejects_invalid_email(client_and_db):
    client, _ = client_and_db

    response = client.post(
        "/api/v1/jobs",
        json={
            "event_name": "Annual Tech Conference",
            "course_name": "Python Development",
            "issue_date": "2026-10-11",
            "recipients": [
                {
                    "name": "Arun Kumar",
                    "email": "not-an-email",
                }
            ],
        },
    )

    assert response.status_code == 422


def test_empty_recipient_list_is_rejected(client_and_db):
    client, _ = client_and_db

    response = client.post(
        "/api/v1/jobs",
        json={
            "event_name": "Annual Tech Conference",
            "course_name": "Python Development",
            "issue_date": "2026-10-11",
            "recipients": [],
        },
    )

    assert response.status_code == 422


def test_unknown_job_returns_404(client_and_db):
    client, _ = client_and_db

    response = client.get(
        "/api/v1/jobs/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404


def test_unknown_recipient_returns_404(client_and_db):
    client, _ = client_and_db

    job_id = create_test_job(client)

    response = client.get(
        f"/api/v1/jobs/{job_id}/certificates/"
        "00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404
