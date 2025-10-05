import requests
import os
import json
import pandas as pd
import joblib
import time
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity

# Ollama API setup
OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL_NAME = "bge-m3"


def create_embedding(text_list):
    """Generate embeddings from Ollama's API with timing."""
    start_time = time.time()
    r = requests.post(
        OLLAMA_URL,
        json={"model": MODEL_NAME, "input": text_list}
    )
    r.raise_for_status()
    elapsed = time.time() - start_time
    print(f"⏱️ Embedding batch of {len(text_list)} items took {elapsed:.2f} seconds")
    return r.json()["embeddings"]


def create_profile_text(profile):
    """Combine fields into a meaningful text for embedding."""
    parts = []

    # Role and company
    if profile.get("current_position"):
        parts.append(f"{profile['current_position']} at {profile.get('current_company', 'Unknown Company')}")

    # Experience
    if profile.get("years_of_experience"):
        parts.append(f"with {profile['years_of_experience']} years of experience")

    # Skills
    if profile.get("total_skills"):
        parts.append(f"Skilled in {profile['total_skills']}")

    # Education
    if profile.get("education_degree") or profile.get("education_institution"):
        parts.append(
            f"Education: {profile.get('education_degree', '')} from {profile.get('education_institution', '')}"
        )

    # Certifications
    if profile.get("certifications"):
        parts.append(f"Certifications: {profile['certifications']}")

    # Location
    if profile.get("city"):
        parts.append(f"Located in {profile['city']}, {profile.get('state', '')}, {profile.get('country', '')}")

    return ". ".join(parts)


def batch(iterable, n=50):
    """Helper: Split data into chunks of size n."""
    for i in range(0, len(iterable), n):
        yield iterable[i:i+n]


def load_json_profiles(file_path="combined.json"):
    """Load and prepare career chunks from combined.json."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks = []
    text_list = []

    print(f"🔹 Preparing {len(data)} profiles...")
    start_time = time.time()

    # Convert each profile into a text representation
    for profile in tqdm(data, desc="Creating profile texts"):
        text = create_profile_text(profile)
        profile["text"] = text
        text_list.append(text)
        chunks.append(profile)

    print(f"🔹 Generating embeddings in batches...")
    all_embeddings = []
    embedding_start = time.time()

    # Process in batches to avoid freezing
    for i, batch_texts in enumerate(batch(text_list, 50)):  # You can adjust 50 → 100 if your system is strong
        print(f"\n🔸 Processing batch {i+1}/{len(text_list)//50 + 1} ({len(batch_texts)} profiles)...")
        batch_embeddings = create_embedding(batch_texts)
        all_embeddings.extend(batch_embeddings)

    total_embed_time = time.time() - embedding_start
    print(f"\n✅ Embedding generation completed in {total_embed_time:.2f} seconds")

    # Attach embeddings to profiles
    for i, emb in enumerate(all_embeddings):
        chunks[i]["chunk_id"] = i
        chunks[i]["embedding"] = emb

    print(f"✅ Total processing time: {time.time() - start_time:.2f} seconds")
    return chunks


if __name__ == "__main__":
    chunks = load_json_profiles("combined.json")
    df = pd.DataFrame.from_records(chunks)
    os.makedirs("data", exist_ok=True)
    joblib.dump(df, "data/embeddings.joblib")
    print("✅ Embeddings saved to data/embeddings.joblib")
    print(f"Total profiles processed: {len(chunks)}")
