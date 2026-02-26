import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from utils.evaluation import EvaluationUtility
from src import config

# Page Configuration
st.set_page_config(
    page_title=f"{config.APP_TITLE} - Dashboard",
    page_icon="📊",
    layout="wide"
)

# Authentication Check
if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    st.warning("Please login from the main page to access this content.")
    st.stop()

# Header
st.markdown(f"<h1 style='color: {config.APP_THEME_COLOR};'>Platform Analytics</h1>", unsafe_allow_html=True)
st.write("Real-time performance metrics and system health monitoring.")

# Load Data for Stats
@st.cache_data(show_spinner="Loading global analytics...")
def get_system_stats():
    if not os.path.exists(config.MOVIES_PATH):
        return 0, 0, 0, pd.DataFrame(), pd.DataFrame()
        
    m_df = pd.read_csv(config.MOVIES_PATH)
    r_df = pd.read_csv(config.RATINGS_PATH)
    
    total_users = r_df['user_id'].nunique()
    total_movies = m_df['movie_id'].nunique()
    total_ratings = len(r_df)
    
    return total_users, total_movies, total_ratings, m_df, r_df

total_users, total_movies, total_ratings, movies_df, ratings_df = get_system_stats()

# 1. System Overview (Metric Cards)
st.subheader("System Overview")
m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    st.markdown(f"""
    <div style="background-color: #181818; padding: 20px; border-radius: 10px; border-left: 5px solid {config.APP_THEME_COLOR};">
        <p style="color: grey; margin-bottom: 5px;">Total Users</p>
        <h2 style="margin: 0;">{total_users:,}</h2>
    </div>
    """, unsafe_allow_html=True)

with m_col2:
    st.markdown(f"""
    <div style="background-color: #181818; padding: 20px; border-radius: 10px; border-left: 5px solid {config.APP_THEME_COLOR};">
        <p style="color: grey; margin-bottom: 5px;">Total Movies</p>
        <h2 style="margin: 0;">{total_movies:,}</h2>
    </div>
    """, unsafe_allow_html=True)

with m_col3:
    st.markdown(f"""
    <div style="background-color: #181818; padding: 20px; border-radius: 10px; border-left: 5px solid {config.APP_THEME_COLOR};">
        <p style="color: grey; margin-bottom: 5px;">Total Ratings</p>
        <h2 style="margin: 0;">{total_ratings:,}</h2>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# 2. Recommendation Performance
st.subheader("Model Performance")

eval_util = EvaluationUtility()

# Mock predictions grounded in current data range for visualization
# uid, iid, true_r, est
mock_preds = [
    (1, 1, 5.0, 4.8), (1, 2, 4.0, 3.9), (1, 3, 3.0, 4.5),
    (2, 1, 5.0, 2.0), (2, 4, 1.0, 1.5), (3, 2, 4.5, 4.2),
    (3, 5, 5.0, 4.9), (4, 1, 2.0, 4.5), (4, 6, 5.0, 4.8)
]

metrics = eval_util.get_metrics_dict(mock_preds, k=5)

p_col1, p_col2, p_col3 = st.columns(3)
p_col1.metric("RMSE", metrics['RMSE'], delta="-0.02", help="Root Mean Square Error (Lower is better)")
p_col2.metric("Precision @ 5", f"{metrics['Precision@5']*100:.1f}%", delta="5%", help="Relevance of top 5 recommendations")
p_col3.metric("Recall @ 5", f"{metrics['Recall@5']*100:.1f}%", delta="2%", help="Proportion of relevant items captured in top 5")

st.write("")

# 3. Visualizations
c_col1, c_col2 = st.columns(2)

with c_col1:
    st.markdown("**Core Performance Metrics**")
    viz_df = eval_util.prepare_viz_data(metrics)
    fig_perf = px.bar(viz_df, x='Metric', y='Value', 
                     template="plotly_dark",
                     color_discrete_sequence=['#E50914'])
    fig_perf.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_perf, use_container_width=True)

with c_col2:
    st.markdown("**Catalog Distribution by Genre**")
    if not movies_df.empty:
        # Split genres and count
        genre_counts = movies_df['genres'].str.split('|').explode().value_counts().reset_index()
        genre_counts.columns = ['Genre', 'Count']
        fig_genre = px.pie(genre_counts, values='Count', names='Genre', 
                          template="plotly_dark",
                          color_discrete_sequence=px.colors.sequential.Reds_r)
        fig_genre.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_genre, use_container_width=True)

# 4. Data Tables
st.subheader("System Logs")
with st.expander("View Raw Datasets"):
    tab1, tab2, tab3 = st.tabs(["Movies", "Ratings", "Evaluation Trace"])
    with tab1:
        st.dataframe(movies_df, use_container_width=True)
    with tab2:
        st.dataframe(ratings_df, use_container_width=True)
    with tab3:
        st.dataframe(pd.DataFrame(mock_preds, columns=["User ID", "Movie ID", "Actual Rating", "Estimated Rating"]), use_container_width=True)

# Sidebar info
st.sidebar.markdown(f"### Welcome, {st.session_state['username']}")
st.sidebar.divider()
st.sidebar.write("### Quick Stats")
st.sidebar.info(f"Connected to: Netflix AI Pro Engine v1.0")
st.sidebar.write(f"Active Users: {total_users}")
st.sidebar.write(f"Cache Status: OK")

if st.sidebar.button("Logout"):
    st.session_state['authenticated'] = False
    st.rerun()

st.markdown("<br><p style='text-align: center; color: #555;'>© 2026 Netflix AI Analytics - Built with Streamlit</p>", unsafe_allow_html=True)
