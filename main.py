from recommender import CareerRecommender
import requests

def embed_query(text):
    r = requests.post(
        "http://localhost:11434/api/embed",
        json={"model": "bge-m3", "input": [text]}
    )
    return r.json()["embeddings"][0]

# Example user input
user_input = "java , javascript , html , css , reactjs"
query_emb = embed_query(user_input)

recommender = CareerRecommender("data/embeddings.joblib")

# Find similar profiles
print("🧭 Similar Profiles:")
print(recommender.find_similar_profiles(query_emb))

# Recommend career roles
print("\n🎯 Recommended Roles:")
print(recommender.recommend_roles(query_emb))

# Recommend skills
print("\n💡 Suggested Skills:")
print(recommender.recommend_skills(query_emb))