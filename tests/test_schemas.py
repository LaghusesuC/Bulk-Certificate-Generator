
import pytest
from datetime import date
from pydantic import ValidationError

from app.schemas import CreateJobRequest


def test_valid_bulk_request():
    request = CreateJobRequest(
        event_name="Annual Tech Conference",
        course_name="Python Development",
        issue_date=date(2026, 10, 11),
        recipients=[
            {"name": "Arun Kumar", "email": "arun@example.com"},
            {"name": "Priya S", "email": "priya@example.com"},
        ],
    )

    assert len(request.recipients) == 2


def test_rejects_empty_recipient_list():
    with pytest.raises(ValidationError):
        CreateJobRequest(
            event_name="Annual Tech Conference",
            course_name="Python Development",
            issue_date=date(2026, 10, 11),
            recipients=[],
        )


def test_rejects_invalid_email():
    with pytest.raises(ValidationError):
        CreateJobRequest(
            event_name="Annual Tech Conference",
            course_name="Python Development",
            issue_date=date(2026, 10, 11),
            recipients=[
                {"name": "Arun Kumar", "email": "not-an-email"}
            ],
        )
