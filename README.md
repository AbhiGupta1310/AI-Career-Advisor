# AI Career Advisor 🎯

An intelligent career recommendation system that uses advanced NLP and machine learning techniques to provide personalized career advice, skill recommendations, and profile matching.

## 🌟 Features

- **Profile Similarity Matching**: Uses BGE-M3 embeddings to find similar career profiles
- **Career Role Recommendations**: Suggests potential career paths based on your skills
- **Skill Gap Analysis**: Identifies missing skills for target roles
- **Cluster Analysis**: Groups similar profiles to identify career patterns
- **Interactive Visualizations**: Explores career data through interactive plots
- **Multiple Career Tracks**: Covers various tech roles including:
  - Data Science & Analytics
  - Software Development
  - Blockchain & Web3
  - Mobile Development
  - Business Analysis

## 🛠️ Technology Stack

- **Core Technologies**:
  - Python 3.x
  - Pandas & NumPy for data processing
  - Scikit-learn for machine learning
  - Plotly & Seaborn for visualizations
- **Models & Embeddings**:

  - BGE-M3 for text embeddings
  - K-Means clustering
  - Random Forest Classifier
  - TF-IDF vectorization

- **Additional Libraries**:
  - Joblib for model persistence
  - Requests for API communication
  - tqdm for progress tracking

## 📊 Data Processing Pipeline

1. **Data Collection**: JSON files containing professional profiles
2. **Preprocessing**:

   - Experience calculation
   - Skills extraction
   - Education & certification parsing
   - Location data normalization

3. **Feature Engineering**:
   - Text embeddings generation
   - Skill count analysis
   - Career path clustering
   - Profile type classification

## 🚀 Getting Started

1. **Setup Environment**:

   ```bash
   # Clone the repository
   git clone [repository-url]
   cd AI-Career-Advisor

   # Install required packages
   pip install pandas numpy scikit-learn plotly seaborn requests tqdm joblib
   ```

Here's the markdown text for those sections:

````markdown
## 2. Data Preparation:

```bash
# Process JSON files to CSV
python preprocess.py

# Generate embeddings
python career_embeddings.py
```
````

## 3. Run the Advisor:

```bash
# Start the recommendation system
python main.py
```

## 💡 Usage Examples

```python
# Initialize the recommender
recommender = CareerRecommender("data/embeddings.joblib")

# Get recommendations for a skill set
user_input = "python, data analysis, sql, tableau"
query_emb = embed_query(user_input)

# Find similar profiles
similar_profiles = recommender.find_similar_profiles(query_emb)

# Get role recommendations
recommended_roles = recommender.recommend_roles(query_emb)

# Get skill suggestions
suggested_skills = recommender.recommend_skills(query_emb)
```

## 📊 Analysis Features

- Career cluster visualization
- Skill distribution analysis
- Experience level insights
- Educational background patterns
- Geographical distribution of roles

## 🧠 Model Pipeline

### 1. Text Embedding:

- Uses BGE-M3 model for semantic understanding
- Processes skills, roles, and profile descriptions

### 2. Clustering:

- K-Means clustering for career grouping
- PCA for dimensionality reduction
- Silhouette analysis for cluster validation

### 3. Classification:

- Random Forest for profile type prediction
- TF-IDF for skill importance analysis
- Cross-validation for model evaluation

## 📂 Project Structure

```
AI-Career-Advisor/
├──  data/                          # Processed data and models
├──  csv/                           # Intermediate CSV files
├──  json/                          # Raw JSON profile data
├──  career_embeddings.py           # Embedding generation
├──  recommender.py                 # Recommendation system
├──  preprocess.py                  # Data preprocessing
├──  main.py                        # Main application
└──  main.ipynb                     # Analysis notebook
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💬 Acknowledgments

- Thanks to all contributors and data providers
- Special thanks to the BGE-M3 model creators
- Inspiration from real-world career development needs

---

Created with ❤️ by Abhi Gupta
