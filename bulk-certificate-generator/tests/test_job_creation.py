import uuid

def test_create_job_success(client):
    data = {
        "certificate_title": "Test",
        "event_name": "Event",
        "organization_name": "Org",
        "issue_date": "2026-10-10",
        "recipients": [
            {"name": "Cheran", "email": "cheran@test.com"},
            {"name": "Ezhil", "email": "ezhil@test.com"}
        ]
    }
    response = client.post("/api/v1/jobs", json=data)
    assert response.status_code == 202
    res_data = response.json()
    assert res_data["success"] == True
    assert "job_id" in res_data["data"]
    assert res_data["data"]["status"] == "PENDING"
    assert res_data["data"]["total_recipients"] == 2
