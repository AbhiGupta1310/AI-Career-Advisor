import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class CareerRecommender:
    def __init__(self, embeddings_path="data/embeddings.joblib"):
        self.df = joblib.load(embeddings_path)
        self.embeddings = np.vstack(self.df["embedding"].values)

    def find_similar_profiles(self, query_embedding, top_k=5):
        """Find top similar profiles based on cosine similarity."""
        sims = cosine_similarity([query_embedding], self.embeddings)[0]
        top_idx = sims.argsort()[-top_k:][::-1]

        return self.df.iloc[top_idx][[
            "current_position",
            "total_skills",
            "education_degree",
            "years_of_experience",
            "text"
        ]]

    def recommend_roles(self, query_embedding, top_k=5):
        """Recommend similar career roles."""
        top_profiles = self.find_similar_profiles(query_embedding, top_k)
        return top_profiles["current_position"].value_counts().head(3).index.tolist()

    def recommend_skills(self, query_embedding, top_k=10):
        """Recommend potential new skills to learn."""
        top_profiles = self.find_similar_profiles(query_embedding, top_k)
        all_skills = ", ".join(top_profiles["total_skills"].fillna("")).lower().split(", ")
        return list(set(all_skills))[:10]
