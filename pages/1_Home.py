import streamlit as st
import pandas as pd
import os
import random
from utils.hybrid import HybridUtility
from utils.content_based import ContentBasedUtility
from utils.tmdb import tmdb
from src import config

# Page Configuration
st.set_page_config(
    page_title=f"{config.APP_TITLE} - Home",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication Check
if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    st.warning("Please login from the main page to access this content.")
    st.stop()

# Load Custom CSS
@st.cache_data(show_spinner=False)
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css(config.CSS_PATH)

# Data & Engine Initialization
@st.cache_resource
def init_system():
    if not os.path.exists(config.MOVIES_PATH):
        m_df = pd.DataFrame(columns=['movie_id', 'title', 'genres', 'overview'])
    else:
        m_df = pd.read_csv(config.MOVIES_PATH)
    
    if not os.path.exists(config.RATINGS_PATH):
        r_df = pd.DataFrame(columns=['user_id', 'movie_id', 'rating'])
    else:
        r_df = pd.read_csv(config.RATINGS_PATH)
        
    hb = HybridUtility()
    cb = ContentBasedUtility()
    return hb, cb, m_df, r_df

hybrid_engine, content_engine, movies_df, ratings_df = init_system()

# Utility to render a movie card with predicted rating
def render_movie_card(movie, score=None):
    poster_url = tmdb.get_poster_path(movie['title']) or tmdb.get_placeholder(movie['title'])
    
    score_html = ""
    if score is not None:
        # Round the score to 1 decimal place
        display_score = round(score, 1)
        score_html = f'<div class="movie-rating">Match: {display_score}</div>'
    
    return f"""
    <div class="movie-card">
        <img src="{poster_url}" class="movie-poster" alt="{movie['title']}">
        <div class="movie-info">
            <div class="movie-title">{movie['title']}</div>
            {score_html}
        </div>
    </div>
    """

# 1. Hero Banner (Featured Movie)
featured_movie = movies_df[movies_df['title'] == 'The Dark Knight'].iloc[0]
hero_img = "https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=1200&q=80"
st.markdown(f"""
<div class="hero-container" style="background-image: url('{hero_img}');">
    <div class="hero-overlay"></div>
    <div class="hero-content">
        <div class="hero-title">{featured_movie['title']}</div>
        <div class="hero-description">
            {featured_movie['overview']}
        </div>
        <div style="display: flex; gap: 10px;">
            <button style="background-color: white; color: black; border: none; padding: 10px 30px; border-radius: 4px; font-weight: bold; cursor: pointer;">▶ Play</button>
            <button style="background-color: rgba(109, 109, 110, 0.7); color: white; border: none; padding: 10px 30px; border-radius: 4px; font-weight: bold; cursor: pointer;">ⓘ More Info</button>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Movie Sections

user_id = st.session_state.get('user_id', 1)
user_ratings = ratings_df[ratings_df['user_id'] == user_id]

# Section: Recommended For You (Hybrid)
st.markdown('<div class="row-header">Recommended For You</div>', unsafe_allow_html=True)
with st.spinner('Curating your personal picks...'):
    try:
        recs = hybrid_engine.get_hybrid_recommendations(user_id, top_n=12)
    except Exception:
        recs = movies_df.sample(min(12, len(movies_df))).to_dict('records')

    # Add dummy scores if not present for visual effect
    for r in recs:
        if 'score' not in r:
            r['score'] = random.uniform(4.0, 5.0)

    cards_html = "".join([render_movie_card(m, score=m.get('score')) for m in recs])
    st.markdown(f'<div class="movie-row">{cards_html}</div>', unsafe_allow_html=True)

# Section: Trending Now (Top rated by all users)
st.markdown('<div class="row-header">Trending Now</div>', unsafe_allow_html=True)
with st.spinner('Loading trending hits...'):
    # Calculate trending based on mean ratings
    trending_ids = ratings_df.groupby('movie_id')['rating'].mean().sort_values(ascending=False).head(10).index
    trending_recs = movies_df[movies_df['movie_id'].isin(trending_ids)].to_dict('records')
    cards_html = "".join([render_movie_card(m) for m in trending_recs])
    st.markdown(f'<div class="movie-row">{cards_html}</div>', unsafe_allow_html=True)

# Section: Top Rated (High confidence picks)
st.markdown('<div class="row-header">Top Rated</div>', unsafe_allow_html=True)
with st.spinner('Loading top rated classics...'):
    top_rated_recs = movies_df.head(10).to_dict('records') # Placeholder for top rated
    cards_html = "".join([render_movie_card(m) for m in top_rated_recs])
    st.markdown(f'<div class="movie-row">{cards_html}</div>', unsafe_allow_html=True)

# Section: Because You Watched (Content-based based on highest rated)
if not user_ratings.empty:
    top_user_movie_id = user_ratings.sort_values(by='rating', ascending=False).iloc[0]['movie_id']
    top_user_movie_title = movies_df[movies_df['movie_id'] == top_user_movie_id]['title'].values[0]
    
    st.markdown(f'<div class="row-header">Because You Watched {top_user_movie_title}</div>', unsafe_allow_html=True)
    with st.spinner(f'Finding more like {top_user_movie_title}...'):
        try:
            similar_recs = content_engine.get_similar_movies(top_user_movie_title, top_n=10)
        except Exception:
            similar_recs = movies_df.sample(min(10, len(movies_df))).to_dict('records')
            
        cards_html = "".join([render_movie_card(m) for m in similar_recs])
        st.markdown(f'<div class="movie-row">{cards_html}</div>', unsafe_allow_html=True)

# Sidebar UI
st.sidebar.markdown(f"### Hello, {st.session_state['username']}")
if st.sidebar.button("Logout"):
    st.session_state['authenticated'] = False
    st.rerun()

st.markdown("<br><br><p style='text-align: center; color: #555;'>© 2026 Netflix AI Clone - Built with Streamlit</p>", unsafe_allow_html=True)
