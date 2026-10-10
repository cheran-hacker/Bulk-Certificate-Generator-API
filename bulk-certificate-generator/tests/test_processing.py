from app.services.processing_service import ProcessingService
from app.db.models.generation_job import JobStatus
from app.db.models.certificate import CertificateStatus
import os

def test_job_processing(client, db_session):
    data = {
        "certificate_title": "Test Certificate",
        "event_name": "Test Event",
        "organization_name": "Test Org",
        "issue_date": "2026-10-10",
        "recipients": [
            {"name": "Cheran S", "email": "cheran@test.com"},
            {"name": "Ezhil", "email": "ezhil@test.com"}
        ]
    }
    response = client.post("/api/v1/jobs", json=data)
    import uuid
    job_id = uuid.UUID(response.json()["data"]["job_id"])
    
    processor = ProcessingService(db_session)
    processor.process_job_background(job_id)
    
    job_resp = client.get(f"/api/v1/jobs/{job_id}")
    job_data = job_resp.json()["data"]
    assert job_data["status"] == "COMPLETED"
    assert job_data["successful"] == 2
    assert job_data["failed"] == 0
    assert job_data["progress_percentage"] == 100.0
