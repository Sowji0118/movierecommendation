import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Base Directory Resolution
BASE_DIR = Path(__file__).resolve().parent.parent

# API Keys
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")

# Data Paths
MOVIES_PATH = os.path.join(BASE_DIR, "data", "movies.csv")
RATINGS_PATH = os.path.join(BASE_DIR, "data", "ratings.csv")

# Model Paths
MODELS_DIR = os.path.join(BASE_DIR, "models")
COLLAB_MODEL_PATH = os.path.join(MODELS_DIR, "collaborative.pkl")
CONTENT_MODEL_PATH = os.path.join(MODELS_DIR, "content.pkl")

# Asset Paths
CSS_PATH = os.path.join(BASE_DIR, "assets", "style.css")

# App Config
APP_TITLE = "Netflix AI Recommender"
APP_THEME_COLOR = "#E50914"
