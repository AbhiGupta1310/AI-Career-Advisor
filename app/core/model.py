"""
ML model loading and prediction logic.
Handles profile type classification and skill recommendation using trained models.
"""

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache

from app.core.config import settings


@lru_cache(maxsize=1)
def _load_profile_model():
    """Lazy-load the XGBoost profile type prediction pipeline."""
    return joblib.load(settings.profile_model_path)


@lru_cache(maxsize=1)
def _load_label_encoder():
    """Lazy-load the label encoder for profile types."""
    return joblib.load(settings.label_encoder_path)


@lru_cache(maxsize=1)
def _load_skill_recommender():
    """Lazy-load the TF-IDF skill recommender bundle."""
    return joblib.load(settings.skill_recommender_path)


@lru_cache(maxsize=1)
def _load_combined_csv():
    """Lazy-load the combined CSV data."""
    return pd.read_csv(settings.combined_csv_path)



def predict_profile_type(features: dict) -> str:
    """Predict profile type from a features dictionary."""
    model = _load_profile_model()
    encoder = _load_label_encoder()

    feature_df = pd.DataFrame([features])
    pred = model.predict(feature_df)
    label = encoder.inverse_transform(pred)
    return label[0]


# Maps predicted profiles to relevant skill keywords for filtering
_PROFILE_SKILL_RELEVANCE = {
    "Frontend_Dev": [
        "typescript", "next.js", "nextjs", "vue", "angular", "svelte", "sass", "tailwind",
        "webpack", "vite", "graphql", "redux", "testing", "jest", "cypress", "figma",
        "ui", "ux", "responsive", "accessibility", "web", "css", "animation", "pwa",
        "storybook", "design system", "performance", "seo", "nuxt",
    ],
    "Backend_Dev": [
        "node", "express", "django", "flask", "spring", "golang", "rust", "postgresql",
        "mongodb", "redis", "kafka", "rabbitmq", "grpc", "rest", "api", "microservice",
        "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "nginx", "linux",
        "sql", "nosql", "celery", "fastapi", "security",
    ],
    "Data_Science": [
        "pandas", "numpy", "scikit-learn", "matplotlib", "seaborn", "jupyter",
        "statistics", "r", "tableau", "power bi", "sql", "data wrangling",
        "feature engineering", "a/b testing", "hypothesis", "visualization",
        "data pipeline", "etl", "spark", "airflow", "dbt",
    ],
    "ML_Engineer": [
        "tensorflow", "pytorch", "keras", "mlflow", "mlops", "kubeflow",
        "model deployment", "feature store", "wandb", "hugging face", "onnx",
        "model monitoring", "data pipeline", "spark", "airflow", "docker",
        "kubernetes", "ci/cd", "aws sagemaker", "vertex ai",
    ],
    "MLOps_Eng": [
        "mlflow", "kubeflow", "docker", "kubernetes", "terraform", "ci/cd",
        "aws", "gcp", "azure", "airflow", "prometheus", "grafana", "model monitoring",
        "feature store", "data pipeline", "jenkins", "github actions", "argo",
    ],
    "DevOps": [
        "docker", "kubernetes", "terraform", "ansible", "jenkins", "ci/cd",
        "aws", "gcp", "azure", "prometheus", "grafana", "linux", "bash",
        "helm", "argo", "istio", "github actions", "monitoring", "security",
    ],
    "Data_Analyst": [
        "sql", "excel", "tableau", "power bi", "python", "r", "statistics",
        "data wrangling", "visualization", "reporting", "dashboard", "etl",
        "google analytics", "looker", "a/b testing",
    ],
}


def recommend_skills(input_skills: str, top_n: int = 10, predicted_profile: str = "") -> list[str]:
    """
    Recommend new skills by comparing input with similar profiles,
    filtered by relevance to the predicted career profile.

    Args:
        input_skills: Comma-separated string of user's current skills.
        top_n: Number of recommendations to return.
        predicted_profile: The ML-predicted career profile for relevance filtering.

    Returns:
        A list of recommended skill names.
    """
    df = _load_combined_csv()
    bundle = _load_skill_recommender()
    tfidf = bundle["tfidf"]
    X_tfidf = bundle["X_tfidf"]

    # Vectorize the input skills
    input_vec = tfidf.transform([input_skills])

    # Compute cosine similarity with all profiles
    sims = cosine_similarity(input_vec, X_tfidf).flatten()

    # Get top 10 most similar profiles (more candidates for better filtering)
    similar_profiles = df.iloc[sims.argsort()[-10:][::-1]]

    # Combine all skills from similar profiles with frequency count
    from collections import Counter
    all_related_skills = []
    for skills in similar_profiles["total_skills"]:
        all_related_skills.extend([s.strip() for s in skills.split(",") if s.strip()])

    skill_counts = Counter(s.lower() for s in all_related_skills)

    # Remove skills user already knows
    input_terms = set(s.strip().lower() for s in input_skills.split(","))
    for known in input_terms:
        skill_counts.pop(known, None)

    # Get relevance keywords for the predicted profile
    relevance_keywords = []
    if predicted_profile:
        relevance_keywords = _PROFILE_SKILL_RELEVANCE.get(predicted_profile, [])

    # Score skills: frequency + relevance bonus
    scored_skills = []
    for skill, count in skill_counts.items():
        score = count
        # Boost skills that are relevant to the predicted career
        if relevance_keywords:
            for keyword in relevance_keywords:
                if keyword in skill or skill in keyword:
                    score += 5  # Strong relevance boost
                    break
        scored_skills.append((skill, score))

    # Sort by score (highest first)
    scored_skills.sort(key=lambda x: x[1], reverse=True)

    # Capitalize nicely and return top_n
    recommended = [s.title() for s in [skill for skill, _ in scored_skills]]
    return recommended[:top_n]
