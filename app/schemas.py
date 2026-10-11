from datetime import date, datetime
from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RecipientInput(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    email: EmailStr

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Recipient name cannot be blank")
        return value


class CreateJobRequest(BaseModel):
    event_name: str = Field(min_length=2, max_length=200)
    course_name: str = Field(min_length=2, max_length=200)
    issue_date: date
    recipients: list[RecipientInput] = Field(
        min_length=1,
        max_length=1000,
    )

    @field_validator("event_name", "course_name")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value


class RecipientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: EmailStr
    status: str
    certificate_path: str | None = None
    error_message: str | None = None


class JobResponse(BaseModel):
    id: str
    event_name: str
    course_name: str
    issue_date: date
    status: str
    total_recipients: int
    created_at: datetime


class JobStatusResponse(BaseModel):
    id: str
    event_name: str
    course_name: str
    status: str
    total_recipients: int
    completed_count: int
    failed_count: int
    pending_count: int
    processing_count: int

