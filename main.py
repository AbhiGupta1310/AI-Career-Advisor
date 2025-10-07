from recommender import CareerRecommender
import requests

def embed_query(text):
    r = requests.post(
        "http://localhost:11434/api/embed",
        json={"model": "bge-m3", "input": [text]}
    )
    return r.json()["embeddings"][0]

# Example user input
user_input = "java,javascript,html,css,reactjs".strip().lower()
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

# import joblib
# import requests
# import google.generativeai as genai
# from recommender import CareerRecommender

# # -----------------------------
# # Configure Gemini
# # -----------------------------
# API_KEY = "AIzaSyDD4vDYp3_1uheoLWMSC_SH5HItsaXuP64"  # Replace
# genai.configure(api_key=API_KEY)
# llm_model = genai.GenerativeModel("gemini-2.5-flash")

# # -----------------------------
# # Embed function
# # -----------------------------
# def embed_query(text):
#     try:
#         r = requests.post(
#             "http://localhost:11434/api/embed",
#             json={"model": "bge-m3", "input": [text]}
#         )
#         r.raise_for_status()
#         return r.json()["embeddings"][0]
#     except Exception as e:
#         print("Embedding error:", e)
#         return None

# # -----------------------------
# # Load recommender
# # -----------------------------
# recommender = CareerRecommender("data/embeddings.joblib")

# # -----------------------------
# # User input
# # -----------------------------
# user_input = input("Enter your skills (comma separated): ")
# query_emb = embed_query([user_input])

# # -----------------------------
# # Use CareerRecommender to predict
# # -----------------------------
# similar_profiles = recommender.find_similar_profiles(query_emb)
# recommended_roles = recommender.recommend_roles(query_emb)
# recommended_skills = recommender.recommend_skills(query_emb)

# print("🧭 Similar Profiles:\n", similar_profiles)
# print("\n🎯 Recommended Roles:\n", recommended_roles)
# print("\n💡 Suggested Skills:\n", recommended_skills)

# # -----------------------------
# # Prepare LLM prompt
# # -----------------------------
# skills_text = ", ".join(recommended_skills)
# prompt = f"""
# You are an AI career advisor. A user has the following predicted skills:

# {skills_text}

# Based on these skills, provide:
# 1. Recommended next skills to learn
# 2. Career paths / roles they can target
# 3. Learning roadmap or advice for growth

# Respond in a friendly and clear way.
# """

# # -----------------------------
# # Generate LLM response
# # -----------------------------
# response = llm_model.generate_content(prompt)
# print("\n📝 Career Guidance by LLM:\n", response.text.strip())
