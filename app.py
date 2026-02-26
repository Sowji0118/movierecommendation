import streamlit as st
import os
from src import config

# Page Configuration
st.set_page_config(
    page_title=f"{config.APP_TITLE} - Login",
    page_icon="🎬",
    layout="centered"
)

# Demo User Store (Username: Password)
USER_DB = {
    "admin": "admin123",
    "guest": "guest123",
    "user1": "pass123"
}

# User Mapping (Username: User_ID for recommendation logic)
USER_IDS = {
    "admin": 1,
    "guest": 2,
    "user1": 3
}

# Load Custom CSS
@st.cache_data(show_spinner=False)
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css(config.CSS_PATH)

# Session State Initialization
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

# Authentication Logic
def login_user(username, password):
    if username in USER_DB and USER_DB[username] == password:
        st.session_state['authenticated'] = True
        st.session_state['username'] = username
        st.session_state['user_id'] = USER_IDS[username]
        return True
    return False

def logout_user():
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.session_state['user_id'] = None
    st.rerun()

# UI Layout
if not st.session_state['authenticated']:
    st.markdown(f"<h1 style='text-align: center; color: {config.APP_THEME_COLOR};'>NETFLIX</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Sign In</h3>", unsafe_allow_html=True)
    
    with st.container():
        st.write("---")
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Sign In", use_container_width=True):
                if login_user(username_input, password_input):
                    st.success(f"Welcome back, {username_input}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        with col2:
            st.button("Need help?", use_container_width=True)
        
        st.markdown("<br><p style='text-align: center; color: grey;'>Demo users: admin/admin123, guest/guest123</p>", unsafe_allow_html=True)

else:
    st.markdown("<h1 style='text-align: center; color: #E50914;'>Your Profile</h1>", unsafe_allow_html=True)
    st.success(f"Logged in as: **{st.session_state['username']}** (User ID: {st.session_state['user_id']})")
    
    st.info("💡 Navigation Tip: Use the sidebar to go to the **Home** or **Dashboard** pages.")
    
    if st.button("Sign Out", use_container_width=True):
        logout_user()

# Sidebar Navigation Hint
st.sidebar.markdown("<h2 style='color: #E50914;'>NETFLIX AI</h2>", unsafe_allow_html=True)
if st.session_state['authenticated']:
    st.sidebar.write(f"Logged in: {st.session_state['username']}")
else:
    st.sidebar.warning("Please Sign In")
