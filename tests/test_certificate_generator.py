
from pathlib import Path
from uuid import uuid4

from app.services.certificate_generator import generate_certificate


def test_generate_certificate(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.certificate_generator.OUTPUT_DIR",
        tmp_path,
    )

    recipient_id = str(uuid4())

    path = generate_certificate(
        recipient_name="Arun Kumar",
        course_name="Python Development",
        event_name="Annual Tech Conference",
        issue_date="2026-10-11",
        recipient_id=recipient_id,
    )

    file_path = Path(path)

    assert file_path.exists()
    assert file_path.suffix == ".pdf"
    assert file_path.stat().st_size > 0
    assert file_path.read_bytes().startswith(b"%PDF-")
