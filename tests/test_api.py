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


@patch("app.api.routes.chat.generate_chat_response")
@patch("app.api.routes.chat.recommend_skills")
@patch("app.api.routes.chat.predict_profile_type")
@patch("app.api.routes.chat.extract_profile_from_message")
def test_chat_with_skills(mock_extract, mock_predict, mock_recommend, mock_generate):
    """Test chat endpoint with a skills-based message."""
    mock_extract.return_value = {
        "skills": "Python, SQL",
        "years_of_experience": 3,
        "education": "Bachelor's",
        "certifications": "",
        "is_conversational": False,
    }
    mock_predict.return_value = "Data_Science"
    mock_recommend.return_value = ["Pandas", "NumPy", "Scikit-Learn"]
    mock_generate.return_value = "Great skills! You'd fit well in Data Science."

    response = client.post("/chat", json={"message": "I know Python and SQL"})
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_profile"] == "Data_Science"
    assert len(data["recommended_skills"]) == 3
    assert "Great skills" in data["response"]
    mock_extract.assert_called_once()


@patch("app.api.routes.chat.generate_chat_response")
@patch("app.api.routes.chat.extract_profile_from_message")
def test_chat_conversational(mock_extract, mock_generate):
    """Test chat endpoint with a conversational message (no ML prediction)."""
    mock_extract.return_value = {
        "skills": "general",
        "years_of_experience": 0,
        "education": "",
        "certifications": "",
        "is_conversational": True,
    }
    mock_generate.return_value = "Hello! How can I help you today?"

    response = client.post("/chat", json={"message": "Hi there!"})
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_profile"] == "General"
    assert data["recommended_skills"] == []
    assert "Hello" in data["response"]


def test_chat_empty_message():
    """Test that chat endpoint rejects empty messages."""
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 422  # Validation error — min_length=1


def test_chat_whitespace_message():
    """Test that chat endpoint rejects whitespace-only messages."""
    response = client.post("/chat", json={"message": "   "})
    assert response.status_code == 422  # Validation error — strip_whitespace + min_length
