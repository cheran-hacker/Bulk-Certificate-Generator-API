from app.services.processing_service import ProcessingService
from app.db.models.generation_job import JobStatus

def test_failure_isolation(client, db_session):
    data = {
        "certificate_title": "Test Certificate",
        "event_name": "Test Event",
        "organization_name": "Test Org",
        "issue_date": "2026-10-10",
        "recipients": [
            {"name": "Valid Name 1", "email": "user1@test.com"},
            {"name": "Invalid Recipient", "email": "invalid@test.com"},
            {"name": "Valid Name 2", "email": "user2@test.com"}
        ]
    }
    response = client.post("/api/v1/jobs", json=data)
    import uuid
    job_id = uuid.UUID(response.json()["data"]["job_id"])
    
    processor = ProcessingService(db_session)
    processor.process_job_background(job_id)
    
    job_resp = client.get(f"/api/v1/jobs/{job_id}")
    job_data = job_resp.json()["data"]
    assert job_data["status"] == "COMPLETED_WITH_ERRORS"
    assert job_data["successful"] == 2
    assert job_data["failed"] == 1
    assert job_data["progress_percentage"] == 100.0
    
    cert_resp = client.get(f"/api/v1/jobs/{job_id}/certificates")
    certs = cert_resp.json()["items"]
    
    success_count = sum(1 for c in certs if c["status"] == "COMPLETED")
    fail_count = sum(1 for c in certs if c["status"] == "FAILED")
    
    assert success_count == 2
    assert fail_count == 1
    
    failed_cert = next(c for c in certs if c["status"] == "FAILED")
    assert failed_cert["error_code"] == "PDF_GENERATION_ERROR"
