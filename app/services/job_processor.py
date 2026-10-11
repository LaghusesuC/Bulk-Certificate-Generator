
from pathlib import Path

from app.database import SessionLocal
from app.models import GenerationJob, Recipient
from app.services.certificate_generator import generate_certificate


def process_generation_job(job_id: str) -> None:
    """Generate certificates independently for each recipient."""
    db = SessionLocal()

    try:
        job = db.query(GenerationJob).filter(
            GenerationJob.id == job_id
        ).first()

        if job is None:
            return

        job.status = "processing"
        db.commit()

        recipients = db.query(Recipient).filter(
            Recipient.job_id == job_id
        ).all()

        for recipient in recipients:
            try:
                recipient.status = "processing"
                recipient.error_message = None
                db.commit()

                path = generate_certificate(
                    recipient_name=recipient.name,
                    course_name=job.course_name,
                    event_name=job.event_name,
                    issue_date=job.issue_date.isoformat(),
                    recipient_id=recipient.id,
                )

                if not Path(path).is_file():
                    raise FileNotFoundError(
                        "Certificate PDF was not created"
                    )

                recipient.certificate_path = path
                recipient.status = "completed"
                db.commit()

            except Exception as exc:
                db.rollback()

                # Reload this recipient after rollback.
                recipient = db.query(Recipient).filter(
                    Recipient.id == recipient.id
                ).first()

                if recipient is not None:
                    recipient.status = "failed"
                    recipient.error_message = str(exc)[:1000]
                    db.commit()

        db.refresh(job)

        failed_count = db.query(Recipient).filter(
            Recipient.job_id == job_id,
            Recipient.status == "failed",
        ).count()

        completed_count = db.query(Recipient).filter(
            Recipient.job_id == job_id,
            Recipient.status == "completed",
        ).count()

        if failed_count == 0:
            job.status = "completed"
        elif completed_count == 0:
            job.status = "failed"
        else:
            job.status = "completed_with_errors"

        db.commit()

    finally:
        db.close()
