import pytest
from app.core.config import settings
import io

pytestmark = pytest.mark.asyncio

async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

async def test_upload_cv(client):
    file_content = b"This is a test CV text content."
    files = {
        "file": ("test.txt", io.BytesIO(file_content), "text/plain")
    }
    data = {"candidate_name": "John Doe", "title": "Software Engineer"}
    headers = {"X-API-Key": settings.API_KEY}
    response = await client.post("/cvs", files=files, data=data, headers=headers)
    assert response.status_code == 201
    assert "cv_id" in response.json()

async def test_create_job(client):
    data = {
        "title": "Backend Engineer",
        "company": "TechCorp",
        "location": "Remote",
        "description_text": "Need python skills",
        "tags": ["python"]
    }
    headers = {"X-API-Key": settings.API_KEY}
    response = await client.post("/jobs", json=data, headers=headers)
    assert response.status_code == 201
    assert "job_id" in response.json()

async def test_match_cv(client):
    data = {"top_k": 5}
    headers = {"X-API-Key": settings.API_KEY}
    response = await client.post("/match/cv/mock_id", json=data, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
async def test_match_job(client):
    data = {"top_k": 5}
    headers = {"X-API-Key": settings.API_KEY}
    response = await client.post("/match/job/mock_id", json=data, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_explain_match(client):
    data = {"cv_id": "mock_cv", "job_id": "mock_job"}
    headers = {"X-API-Key": settings.API_KEY}
    response = await client.post("/explain", json=data, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert "match_score" in res_data
    assert res_data["match_score"] == 85
