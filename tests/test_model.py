"""
Tests for core model logic.
"""

from unittest.mock import patch, MagicMock
import numpy as np


def test_config_loads():
    """Test that the config module loads without errors."""
    from app.core.config import settings

    assert settings.groq_model == "llama-3.3-70b-versatile"
    assert settings.api_port == 8000


def test_recommend_skills_logic():
    """Test the skill recommendation logic with mocked data."""
    import pandas as pd

    mock_df = pd.DataFrame(
        {
            "total_skills": [
                "Python, Docker, Kubernetes",
                "Python, AWS, Terraform",
                "Python, React, Node.js",
                "Python, SQL, Pandas",
                "Python, FastAPI, PostgreSQL",
            ]
        }
    )

    mock_bundle = {
        "tfidf": MagicMock(),
        "X_tfidf": MagicMock(),
    }

    # Mock the tfidf transform to return a sparse-like matrix
    mock_bundle["tfidf"].transform.return_value = MagicMock()

    with (
        patch("app.core.model._load_combined_csv", return_value=mock_df),
        patch("app.core.model._load_skill_recommender", return_value=mock_bundle),
        patch("app.core.model.cosine_similarity") as mock_sim,
    ):
        # Return similarities that pick the first 5 profiles
        mock_sim.return_value = np.array([[0.9, 0.8, 0.7, 0.6, 0.5]])

        from app.core.model import recommend_skills

        result = recommend_skills("Python, SQL")

        assert isinstance(result, list)
        # Should recommend skills the user doesn't already have
        for skill in result:
            assert skill.lower() not in ["python", "sql"]
