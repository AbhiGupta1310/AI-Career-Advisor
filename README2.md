# Career Recommendation System

A machine learning-based career recommendation system that uses semantic embeddings to match user skills with similar career profiles, suggest relevant job roles, and recommend skills to learn.

## 🎯 Overview

This project analyzes career profiles from LinkedIn data and uses the BGE-M3 embedding model (via Ollama) to create a semantic search and recommendation engine. It can:

- Find similar career profiles based on user skills
- Recommend suitable job roles/positions
- Suggest new skills to learn based on career trajectories

## 🏗️ Architecture

The system consists of three main components:

1. **Data Preprocessing** (`preprocess.py`) - Converts raw LinkedIn JSON profiles into structured CSV format
2. **Embedding Generation** (`career_embeddings.py`) - Creates semantic embeddings for all career profiles
3. **Recommendation Engine** (`recommender.py` + `main.py`) - Performs similarity search and generates recommendations

## 📋 Requirements

### Software Dependencies

- Python 3.7+
- Ollama (with BGE-M3 model installed)

### Python Packages

```bash
pip install pandas scikit-learn joblib requests tqdm
```

### Ollama Setup

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull the BGE-M3 model:

```bash
ollama pull bge-m3
```

3. Ensure Ollama is running (default: `http://localhost:11434`)

## 📁 Project Structure

```
.
├── json/                          # Raw LinkedIn profile JSON files
├── csv/                           # Processed CSV files (generated)
├── data/                          # Embeddings storage (generated)
│   └── embeddings.joblib
├── preprocess.py                  # JSON to CSV converter
├── fixing_jsons.py                # Utility to fix nested JSON structures
├── career_embeddings.py           # Embedding generation script
├── recommender.py                 # Recommendation logic
├── main.py                        # Example usage/demo
└── combined.json                  # Combined profiles for embedding
```

## 🚀 Getting Started

### Step 1: Prepare Your Data

Place your LinkedIn profile JSON files in the `json/` directory. Each file should contain profiles for a specific career type.

If you have nested JSON structures, fix them first:

```bash
python fixing_jsons.py
```

### Step 2: Preprocess JSON to CSV

Convert all JSON files to structured CSV format:

```bash
python preprocess.py
```

This creates CSV files in the `csv/` directory with the following fields:

- Current position & company
- Years of experience
- Skills
- Education (degree & institution)
- Certifications
- Location (city, state, country)
- Profile type

### Step 3: Generate Embeddings

Create a `combined.json` file with all profiles, then generate embeddings:

```bash
python career_embeddings.py
```

This script:

- Loads profiles from `combined.json`
- Creates semantic text representations combining position, skills, education, etc.
- Generates embeddings using Ollama's BGE-M3 model
- Processes in batches (default: 50 profiles per batch)
- Saves embeddings to `data/embeddings.joblib`

**Performance note:** Embedding generation time depends on the number of profiles and your hardware. The script displays progress and timing information.

### Step 4: Run Recommendations

```bash
python main.py
```

## 💡 Usage Examples

### Basic Usage

```python
from recommender import CareerRecommender
import requests

# Create embedding for user query
def embed_query(text):
    r = requests.post(
        "http://localhost:11434/api/embed",
        json={"model": "bge-m3", "input": [text]}
    )
    return r.json()["embeddings"][0]

# Initialize recommender
recommender = CareerRecommender("data/embeddings.joblib")

# User's current skills
user_skills = "python, machine learning, data analysis, sql"
query_embedding = embed_query(user_skills)

# Find similar profiles
similar_profiles = recommender.find_similar_profiles(query_embedding, top_k=10)
print(similar_profiles)

# Get role recommendations
recommended_roles = recommender.recommend_roles(query_embedding, top_k=10)
print(f"Suggested roles: {recommended_roles}")

# Get skill recommendations
suggested_skills = recommender.recommend_skills(query_embedding, top_k=10)
print(f"Skills to learn: {suggested_skills}")
```

### Custom Query Examples

```python
# For a career transition
query = "5 years experience in web development, looking to move into data science"
query_emb = embed_query(query)
roles = recommender.recommend_roles(query_emb)

# For skill gap analysis
query = "software engineer with java, spring boot, need to learn cloud technologies"
query_emb = embed_query(query)
skills = recommender.recommend_skills(query_emb)
```

## 🔧 Configuration

### Adjusting Batch Size

In `career_embeddings.py`, modify the batch size for embedding generation:

```python
for i, batch_texts in enumerate(batch(text_list, 50)):  # Change 50 to 100 for faster processing
```

### Changing Embedding Model

Update the model name in both `career_embeddings.py` and `main.py`:

```python
MODEL_NAME = "bge-m3"  # Change to another Ollama model
```

### Modifying Recommendation Count

Adjust `top_k` parameter in function calls:

```python
recommender.find_similar_profiles(query_emb, top_k=20)  # Get top 20 instead of 10
```

## 📊 Data Processing Details

### Experience Calculation

The system calculates years of experience from:

- Duration strings (e.g., "3 yrs 1 mo")
- Start and end dates (using current date if still employed)

### Profile Text Generation

Each profile is converted to a semantic text combining:

- Current position and company
- Years of experience
- Skills list
- Education background
- Certifications
- Location

Example: _"Senior Software Engineer at Google with 5 years of experience. Skilled in Python, Java, AWS. Education: BS Computer Science from MIT. Located in San Francisco, CA, USA"_

## 🎓 How It Works

1. **Semantic Embedding**: Each career profile is converted into a 1024-dimensional vector (BGE-M3) that captures semantic meaning
2. **Cosine Similarity**: User queries are embedded and compared against all profile embeddings using cosine similarity
3. **Recommendation Logic**:
   - **Similar Profiles**: Returns top-K most similar profiles based on embedding distance
   - **Role Recommendations**: Aggregates positions from similar profiles and returns most common roles
   - **Skill Recommendations**: Extracts skills from similar profiles and suggests ones the user likely doesn't have

## ⚠️ Troubleshooting

### Ollama Connection Issues

```
Error: Connection refused to localhost:11434
```

**Solution**: Ensure Ollama is running. Start it with:

```bash
ollama serve
```

### Memory Issues During Embedding

```
MemoryError or system freeze during embedding generation
```

**Solution**: Reduce batch size in `career_embeddings.py`:

```python
for i, batch_texts in enumerate(batch(text_list, 25)):  # Reduced from 50
```

### JSON Format Errors

```
JSONDecodeError: Extra data
```

**Solution**: Use `fixing_jsons.py` to fix nested JSON structures before processing.

## 🔮 Future Enhancements

- [ ] Add web interface (Flask/FastAPI)
- [ ] Include salary predictions
- [ ] Add career path progression suggestions
- [ ] Implement skill gap visualization
- [ ] Support for multiple languages
- [ ] Real-time LinkedIn profile import
- [ ] Advanced filtering (location, experience level, industry)

## 📝 License

This project is provided as-is for educational and research purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📧 Contact

For questions or feedback, please open an issue in the repository.

---

**Note**: This system works best with a diverse dataset of career profiles. The quality of recommendations improves with more data across different industries and roles.
