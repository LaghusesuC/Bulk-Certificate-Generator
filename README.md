# Bulk Certificate Generator API

A REST API built with Python and FastAPI that creates bulk certificate-generation jobs, generates PDF certificates for individual recipients, tracks job progress, and provides certificate downloads.

## Features

- Create bulk certificate-generation jobs.
- Validate recipient names, email addresses, and job input.
- Generate personalized PDF certificates using ReportLab.
- Track job and recipient generation statuses.
- Download generated certificates through a REST API.
- Isolate individual recipient failures so one failure does not stop the remaining recipients.
- Store job and recipient metadata in a relational database.
- Test API endpoints, validation, PDF generation, and failure handling.

## Tech Stack

- **Language:** Python
- **API framework:** FastAPI
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **PDF generation:** ReportLab
- **Validation:** Pydantic
- **Testing:** Pytest and HTTPX
- **ASGI server:** Uvicorn

## Project Structure

```text
bulk-certificate-generator/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── jobs.py
│   └── services/
│       ├── __init__.py
│       ├── certificate_generator.py
│       └── job_processor.py
├── tests/
│   ├── __init__.py
│   ├── test_schemas.py
│   ├── test_certificate_generator.py
│   └── test_jobs.py
├── generated_certificates/
├── .gitignore
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.11 or compatible
- pip

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/LaghusesuC/Bulk-Certificate-Generator.git
cd bulk-certificate-generator
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Start the application

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

Health check:

`GET /health`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API health |
| POST | `/api/v1/jobs` | Create a certificate-generation job |
| GET | `/api/v1/jobs/{job_id}` | Retrieve job status and progress |
| GET | `/api/v1/jobs/{job_id}/certificates/{recipient_id}` | Download a recipient's certificate |

## Example: Create a Generation Job

**Request**

`POST /api/v1/jobs`

```json
{
  "event_name": "Annual Tech Conference",
  "course_name": "Python Development",
  "issue_date": "2026-10-11",
  "recipients": [
    {
      "name": "Arun Kumar",
      "email": "arun@example.com"
    },
    {
      "name": "Priya S",
      "email": "priya@example.com"
    }
  ]
}
```

The API validates the input, stores the job and recipient records, and schedules certificate generation using FastAPI background tasks.

A successful request returns **HTTP 201 Created** with the job details and generated job ID.

## Check Job Progress

**Request**

`GET /api/v1/jobs/{job_id}`

The response includes the job status, total recipient count, and counts of completed, failed, pending, and processing recipients.

Possible overall job statuses:

- `pending`
- `processing`
- `completed`
- `completed_with_errors`
- `failed`

Recipient statuses:

- `pending`
- `processing`
- `completed`
- `failed`

## Download a Certificate

**Request**

`GET /api/v1/jobs/{job_id}/certificates/{recipient_id}`

Use the job ID and recipient ID returned or stored by the application.

A successful request returns the generated PDF file.

Relevant HTTP responses:

- `200 OK` — certificate available.
- `404 Not Found` — job, recipient, or generated file not found.
- `409 Conflict` — certificate is not ready or generation failed.
- `422 Unprocessable Entity` — request validation failed.

## Certificate Storage

Generated certificates are stored as PDF files in the `generated_certificates/` directory.

The database stores the job details, recipient details, generation status, certificate path, and any error message.

## Run Tests

Run the test suite from the project root:

```powershell
python -m pytest -q
```

The tests cover:

- Schema validation.
- PDF certificate generation.
- Job creation and status tracking.
- Successful certificate retrieval.
- Invalid input and missing resources.
- Individual-recipient failure isolation.

## Design Decisions

**Relational data model:** Separate job and recipient tables represent one-to-many relationships between a generation job and its recipients.

**Per-recipient error handling:** Each recipient is processed independently. A failed certificate is recorded without preventing subsequent recipients from being processed.

**Background processing:** FastAPI background tasks allow the API to return the created job response before the complete generation workflow finishes.

**PDF generation:** ReportLab creates personalized certificates programmatically from a predefined layout.

**Input validation:** Pydantic validates request fields and email addresses before the job is created.

**Database choice:** SQLite keeps local setup simple. A production deployment could use PostgreSQL and a durable task queue for more robust concurrent processing.

## Limitations

- Background jobs run in the application process and are not durable across process termination.
- SQLite is intended for this project's straightforward development setup.
- Generated certificate files are stored locally rather than in cloud object storage.

## Future Improvements

- Add a durable background queue such as Celery or RQ.
- Add authentication and authorization.
- Add configurable certificate templates.
- Support ZIP downloads for entire jobs.
- Add cloud storage and deployment configuration.

## License

Add the license required for your intended distribution, if applicable.
