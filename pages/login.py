import streamlit as st
import sqlite3
import hashlib
import re

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

def get_user_by_email(email):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user

def update_password(email, new_password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET password = ? WHERE email = ?",
        (hash_password(new_password), email)
    )
    conn.commit()
    conn.close()
    return True

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="centered"
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
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "reset_mode" not in st.session_state:
    st.session_state.reset_mode = False

# ---------- MAIN CONTENT ----------
st.title("🔐 Login")

if "logged_in" in st.session_state and st.session_state.logged_in:
    st.success(f"Welcome back, {st.session_state.get('username', 'User')}!")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/dashboard.py")
    st.stop()

# ---------- FORGOT PASSWORD MODE ----------
if st.session_state.reset_mode:
    st.subheader("🔑 Reset Password")
    st.write("Enter your email address to reset your password.")
    
    reset_email = st.text_input("Email Address", placeholder="you@example.com")
    new_password = st.text_input("New Password", type="password", placeholder="Min 6 characters")
    confirm_password = st.text_input("Confirm New Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset Password", use_container_width=True):
            if not reset_email or not new_password:
                st.warning("⚠️ Please fill in all fields.")
            elif not validate_email(reset_email):
                st.warning("⚠️ Please enter a valid email address.")
            elif len(new_password) < 6:
                st.warning("⚠️ Password must be at least 6 characters.")
            elif new_password != confirm_password:
                st.warning("⚠️ Passwords do not match.")
            else:
                user = get_user_by_email(reset_email)
                if user:
                    update_password(reset_email, new_password)
                    st.success("✅ Password reset successfully!")
                    st.session_state.reset_mode = False
                    st.rerun()
                else:
                    st.error("❌ No account found with this email address.")
    
    with col2:
        if st.button("← Back", use_container_width=True):
            st.session_state.reset_mode = False
            st.rerun()
    
    st.stop()

# ---------- LOGIN MODE ----------
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
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

# ---------- FORGOT PASSWORD BUTTON ----------
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🔑 Forgot Password?", use_container_width=True):
        st.session_state.reset_mode = True
        st.rerun()

# Back to Home
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("← Back to Home", use_container_width=True):
        st.switch_page("app.py")