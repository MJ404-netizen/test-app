import streamlit as st
import sqlite3
import hashlib
import time

# ---------- DATABASE FUNCTIONS ----------
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, hash_password(password))
    )
    user = c.fetchone()
    conn.close()
    return user

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- CSS ----------
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp {
            background: linear-gradient(#c7f9ff, #dafbff, #fbffdb, #d5f7cb, #c7f9ff);
        }
        
        /* Style for forgot password link */
        .forgot-link {
            text-align: center;
            margin-top: 10px;
            margin-bottom: 20px;
        }
        .forgot-link a {
            color: #4CAF50;
            text-decoration: none;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: color 0.3s ease;
        }
        .forgot-link a:hover {
            color: #2E7D32;
            text-decoration: underline;
        }
        
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
        .back-link a {
            color: #4CAF50;
            text-decoration: none;
            font-size: 14px;
        }
        .back-link a:hover {
            text-decoration: underline;
        }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------- MAIN CONTENT ----------
st.title("🔐 Login")

# Check if user is already logged in - redirect to test page
if "logged_in" in st.session_state and st.session_state.logged_in:
    st.success(f"Welcome back, {st.session_state.get('username', 'User')}!")
    st.info("⏳ Redirecting to test page...")
    time.sleep(1)
    st.switch_page("pages/test_page.py")
    st.stop()

# ---------- LOGIN FORM ----------
with st.form("login_form"):
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    submitted = st.form_submit_button("🔐 Login", use_container_width=True)
    
    if submitted:
        if not username or not password:
            st.warning("⚠️ Please enter both username and password.")
        else:
            user = verify_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.session_state.user_id = user["id"]
                st.success("✅ Login successful! Redirecting to test...")
                time.sleep(1)
                st.switch_page("pages/test_page.py")
            else:
                st.error("❌ Invalid username or password.")

# ---------- FORGOT PASSWORD LINK ----------
st.markdown(
    """
    <div class="forgot-link">
        <a href="forgot_pwd" target="_self">🔑 Forgot Password?</a>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- BACK TO HOME ----------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("← Back to Home", use_container_width=True):
        st.switch_page("main.py")