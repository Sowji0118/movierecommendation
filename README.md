# Netflix-style AI Movie Recommendation System

A production-grade recommendation engine built with Python, Streamlit, and Machine Learning.

## Features
- **Hybrid Recommendation Engine**: Combines Collaborative Filtering (SVD) and Content-based Filtering (TF-IDF).
- **Netflix UI**: Custom CSS to mimic the premium Netflix experience.
- **Multi-page Architecture**: Home, Login, and Dashboard pages.
- **TMDB Integration**: Real-time movie posters via TMDB API.
- **Evaluation**: RMSE and Precision@K metrics.

## Tech Stack
- **Languages**: Python
- **Frontend**: Streamlit
- **ML Libraries**: Scikit-learn, Surprise, Pandas, NumPy
- **Persistence**: Pickle
- **API**: TMDB API

## Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install streamlit scikit-learn surprise pandas numpy requests
   ```
3. Set up TMDB API key in `src/config.py`.
4. Run the app:
   ```bash
   streamlit run app.py
   ```
