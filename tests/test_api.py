"""
Tests for API endpoints.
Uses FastAPI TestClient for integration testing.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_health_check():
    """Test that the health check endpoint returns 200."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "running" in data["message"].lower()


@patch("app.api.routes.predict.predict_profile_type")
def test_predict_profile_type(mock_predict):
    """Test profile prediction endpoint with mocked model."""
    mock_predict.return_value = "Data Scientist"

    payload = {
        "years_of_experience": 5,
        "education_degree": "Master's",
        "education_institution": "MIT",
        "total_skills": "Python, Machine Learning, SQL",
        "certifications": "AWS",
        "city": "Boston",
        "state": "MA",
    }

    response = client.post("/predict_profile_type", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["output_label"] == "Data Scientist"
    mock_predict.assert_called_once()


@patch("app.api.routes.recommend.recommend_skills")
def test_recommend_skills(mock_recommend):
    """Test skill recommendation endpoint with mocked model."""
    mock_recommend.return_value = ["Docker", "Kubernetes", "Terraform"]

    payload = {"total_skills": "Python, AWS, Linux"}

    response = client.post("/recommend_skills", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["recommended_skills"]) == 3
    assert "Docker" in data["recommended_skills"]
    mock_recommend.assert_called_once_with("Python, AWS, Linux")


def test_recommend_skills_empty_input():
    """Test that recommendation endpoint rejects empty input."""
    response = client.post("/recommend_skills", json={})
    assert response.status_code == 422  # Validation error — total_skills is required


@patch("app.api.routes.predict.predict_profile_type")
def test_predict_with_minimal_input(mock_predict):
    """Test prediction works with only required fields populated."""
    mock_predict.return_value = "Frontend Developer"

    payload = {"total_skills": "React, JavaScript"}
    response = client.post("/predict_profile_type", json=payload)
    assert response.status_code == 200
    assert response.json()["output_label"] == "Frontend Developer"
