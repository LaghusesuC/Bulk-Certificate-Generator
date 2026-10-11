from pathlib import Path

from fastapi.responses import FileResponse

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from app.services.job_processor import process_generation_job
from app.schemas import JobStatusResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GenerationJob, Recipient
from app.schemas import CreateJobRequest, JobResponse

router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs"])



@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    request: CreateJobRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = GenerationJob(
        event_name=request.event_name,
        course_name=request.course_name,
        issue_date=request.issue_date,
        status="pending",
        total_recipients=len(request.recipients),
    )

    for recipient_data in request.recipients:
        recipient = Recipient(
            name=recipient_data.name,
            email=str(recipient_data.email),
            status="pending",
        )
        job.recipients.append(recipient)

    try:
        db.add(job)
        db.commit()
        db.refresh(job)

        # Save the ID before scheduling the background task.
        job_id = job.id

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create generation job",
        ) from exc

    background_tasks.add_task(process_generation_job, job_id)

    return job


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Generation job not found",
        )

    recipients = job.recipients

    completed = sum(r.status == "completed" for r in recipients)
    failed = sum(r.status == "failed" for r in recipients)
    processing = sum(r.status == "processing" for r in recipients)
    pending = sum(r.status == "pending" for r in recipients)

    return JobStatusResponse(
        id=job.id,
        event_name=job.event_name,
        course_name=job.course_name,
        status=job.status,
        total_recipients=job.total_recipients,
        completed_count=completed,
        failed_count=failed,
        pending_count=pending,
        processing_count=processing,
    )

    
@router.get("/{job_id}/certificates/{recipient_id}")
def download_certificate(
    job_id: str,
    recipient_id: str,
    db: Session = Depends(get_db),
):
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Generation job not found",
        )

    recipient = db.query(Recipient).filter(
        Recipient.id == recipient_id,
        Recipient.job_id == job_id,
    ).first()

    if recipient is None:
        raise HTTPException(
            status_code=404,
            detail="Recipient not found in this job",
        )

    if recipient.status != "completed" or not recipient.certificate_path:
        raise HTTPException(
            status_code=409,
            detail=f"Certificate is not available. Status: {recipient.status}",
        )

    file_path = Path(recipient.certificate_path)

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Certificate file not found",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{recipient.name.replace(' ', '_')}_certificate.pdf",
    )

