# AI Career Advisor

An intelligent career recommendation system using advanced ML techniques for personalized career path suggestions, skill recommendations, and profile classification. The system leverages embedding-based similarity matching and XGBoost classification for accurate career predictions.

---

## 🌟 Features

- **Profile Type Classification**: XGBoost-powered classification of career profiles
- **Skill Clustering**: Advanced embedding-based skill clustering using BGE-M3
- **Skill Recommendations**: Smart skill suggestions using TF-IDF and cosine similarity
- **Interactive Visualizations**: PCA-based cluster visualizations
- **Career Tracks Analysis**: Covers multiple tech roles:
  - ML Engineering (ML_Eng)
  - Data Science (DS)
  - Data Analytics (DA)
  - Business Analysis (BA)
  - Business Intelligence (BI_Dev)
  - Backend Development
  - Frontend Development
  - Full Stack Development
  - Mobile Development
  - Blockchain & Web3 Development
  - Security Analysis
  - MLOps Engineering

---

## 🛠️ Technology Stack

### Core Technologies

- Python 3.x
- Pandas & NumPy for data processing
- Scikit-learn for ML pipelines
- XGBoost for classification

### Models & Techniques

- BGE-M3 embeddings for semantic analysis
- XGBoost Classifier
- K-Means clustering
- TF-IDF vectorization
- PCA for dimensionality reduction

### Additional Libraries

- Joblib for model persistence
- Matplotlib & Plotly for visualizations
- Requests for API communication

---

## 📊 Data Processing Pipeline

### 1. Data Preprocessing

- Duplicate removal
- Missing value handling
- Numeric data cleaning
- Text data normalization

### 2. Feature Engineering

- Text embeddings using BGE-M3
- TF-IDF vectorization
- One-hot encoding for categorical features
- Standard scaling for numeric features

### 3. Model Pipeline

- XGBoost classification model
- K-Means clustering (k=6)
- PCA visualization

---

## 🚀 Getting Started

### Environment Setup

```bash
# Clone the repository
git clone [repository-url]
cd AI-Career-Advisor

# Install required packages
pip install pandas numpy scikit-learn xgboost plotly requests joblib matplotlib
```

### Prepare Environment

- Ensure Ollama is running locally (for BGE-M3 embeddings)
- Port 11434 should be available for the Ollama API

### Run Analysis

```bash
# Start Jupyter notebook
jupyter notebook main.ipynb
```

---

## 💡 Usage Examples

```python
import pandas as pd
import joblib

# Load the trained models
model = joblib.load("models/profile_type_xgb_pipeline.joblib")
kmeans = joblib.load("models/skill_clusters2.joblib")

# Example profile
new_profile = {
    "years_of_experience": 5,
    "education_degree": "B.Tech",
    "education_institution": "IIT Delhi",
    "total_skills": "Python, Machine Learning, Data Analysis",
    "certifications": "AWS Certified Machine Learning",
    "city": "Bangalore",
    "state": "Karnataka"
}

# Get profile type prediction
profile_type = model.predict(pd.DataFrame([new_profile]))

# Get skill recommendations
recommended_skills = recommend_skills(new_profile["total_skills"])
```

---

## 📈 Analysis Features

### Profile Classification

- Multi-class classification using XGBoost
- Comprehensive feature preprocessing
- Label encoding for target variables

### Skill Clustering

- 6 distinct skill clusters
- Embedding-based similarity
- PCA visualization

### Skill Recommendations

- TF-IDF based similarity
- Context-aware suggestions
- Filtered for novelty

---

## 📁 Project Structure

```
AI-Career-Advisor/
├──  data/                          # Processed embedding data
├──  csv/                           # Processed CSV files
├──  json/                          # Raw JSON profile data
├──  models/                        # saved models
├──  fixing_jsons.py                # fixing json into usable format
├──  career_embeddings.py           # Embedding generation
├──  recommender.py                 # Recommendation system
├──  preprocess.py                  # Data preprocessing
├──  main.py                        # Main application
└──  main.ipynb                     # Analysis notebook
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Acknowledgments

- Thanks to all contributors
- Special thanks to the BGE-M3 model creators
- XGBoost and scikit-learn communities

---

**Created with ❤️ by Abhi Gupta**
