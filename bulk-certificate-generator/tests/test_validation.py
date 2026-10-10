def test_create_job_invalid_email(client):
    data = {
        "certificate_title": "Test",
        "event_name": "Event",
        "organization_name": "Org",
        "issue_date": "2026-10-10",
        "recipients": [
            {"name": "Cheran", "email": "invalid_email"}
        ]
    }
    response = client.post("/api/v1/jobs", json=data)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"

def test_create_job_missing_fields(client):
    data = {
        "recipients": [{"name": "Cheran", "email": "cheran@test.com"}]
    }
    response = client.post("/api/v1/jobs", json=data)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
