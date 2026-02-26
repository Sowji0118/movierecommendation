import streamlit as st
import pandas as pd
import os
from src.recommender_content import ContentRecommender
from src.recommender_collaborative import CollaborativeRecommender
from src.recommender_hybrid import HybridRecommender

# Page Configuration
st.set_page_config(
    page_title="Netflix AI Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("assets/css/style.css")

# Initialize Session State
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = 1
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Data Loading
@st.cache_resource
def load_engines():
    m_df = pd.read_csv('data/movies.csv')
    r_df = pd.read_csv('data/ratings.csv')
    
    cr = ContentRecommender(m_df)
    cr.fit()
    
    colr = CollaborativeRecommender(r_df)
    colr.fit()
    
    hr = HybridRecommender(cr, colr)
    return hr, m_df

hybrid_engine, movies_df = load_engines()

# Header
st.markdown("<h1 style='text-align: center;'>NETFLIX</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: grey;'>AI-Powered Movie Recommendations</p>", unsafe_allow_html=True)

# Main Navigation
menu = ["Home", "Dashboard", "Login"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Home":
    st.subheader("Trending Now")
    
    # Hero Section
    cols = st.columns([2, 1])
    with cols[0]:
        st.image("https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=800&q=80", use_container_width=True)
    with cols[1]:
        st.title("The Dark Knight")
        st.write("When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.")
        if st.button("Watch Now"):
            st.success("Redirecting to player...")
            
    st.divider()
    
    st.subheader("Personalized Picks for You")
    # Get hybrid recommendations based on a seed movie for the home page demo
    recs = hybrid_engine.get_recommendations(st.session_state['user_id'], 'The Dark Knight', movies_df, top_n=5)
    
    rec_cols = st.columns(5)
    for i, rec in enumerate(recs):
        with rec_cols[i]:
            st.markdown(f"""
            <div class="movie-card">
                <img src="https://via.placeholder.com/200x300?text={rec['title']}" class="movie-poster">
                <div class="movie-title">{rec['title']}</div>
            </div>
            """, unsafe_allow_html=True)

elif choice == "Dashboard":
    if not st.session_state['authenticated']:
        st.warning("Please login to see your personalized dashboard.")
    else:
        st.title(f"Welcome back, User {st.session_state['user_id']}")
        # Dashboard logic...

elif choice == "Login":
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Sign In"):
        st.session_state['authenticated'] = True
        st.success("Successfully logged in!")
        st.rerun()
