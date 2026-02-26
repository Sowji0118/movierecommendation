import requests
import streamlit as st
from src import config

class TMDBHelper:
    def __init__(self):
        self.api_key = config.TMDB_API_KEY
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"

    @st.cache_data(show_spinner=False, ttl=86400)
    def get_poster_path(_self, movie_title):
        """Fetches poster path from TMDB with robust error handling and caching."""
        if not _self.api_key or _self.api_key == "your_api_key_here":
            return None
            
        search_url = f"{_self.base_url}/search/movie"
        params = {
            "api_key": _self.api_key,
            "query": movie_title
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=5)
            response.raise_for_status()
            results = response.json().get('results')
            if results:
                poster_path = results[0].get('poster_path')
                return f"{_self.image_base_url}{poster_path}" if poster_path else None
        except Exception:
            # Silent fail for posters to avoid breaking UI
            return None
            
        return None

    def get_placeholder(self, title):
        """Returns a placeholder image URL."""
        return f"https://via.placeholder.com/200x300/181818/E50914?text={title.replace(' ', '+')}"

# Singleton instance
tmdb = TMDBHelper()
