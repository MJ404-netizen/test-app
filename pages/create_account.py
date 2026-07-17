import streamlit as st
import sqlite3
import hashlib
import re

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        hashed = hash_password(password)
        c.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed)
        )
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already exists. Please choose another."
        elif "email" in str(e):
            return False, "Email already registered. Please login."
        return False, "An error occurred. Please try again."
    finally:
        conn.close()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ---------- INITIALIZE DATABASE ----------
init_db()

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Create Account",
    page_icon="📝",
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

# ---------- MAIN CONTENT ----------
st.title("📝 Create Account")

# Check if user is already logged in
if "logged_in" in st.session_state and st.session_state.logged_in:
    st.success(f"You are already logged in as {st.session_state.get('username', 'User')}!")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/dashboard.py")
    st.stop()

with st.form("create_account_form"):
    username = st.text_input("Create a username", placeholder="Choose a unique username")
    email = st.text_input("Enter your email", placeholder="you@example.com")
    password = st.text_input("Create password", type="password", placeholder="Min 6 characters")
    confirm = st.text_input("Confirm password", type="password", placeholder="Re-enter password")
    
    submitted = st.form_submit_button("✨ Create Account", use_container_width=True)
    
    if submitted:
        # Validate inputs
        if not username or not email or not password:
            st.warning("⚠️ Please fill in all fields.")
        elif len(username) < 3:
            st.warning("⚠️ Username must be at least 3 characters.")
        elif not validate_email(email):
            st.warning("⚠️ Please enter a valid email address.")
        elif len(password) < 6:
            st.warning("⚠️ Password must be at least 6 characters.")
        elif password != confirm:
            st.warning("⚠️ Passwords do not match.")
        else:
            # Try to create user
            success, message = create_user(username, email, password)
            if success:
                st.success(f"✅ {message}")
                st.info("You can now login with your credentials!")
                if st.button("← Back to Login"):
                    st.switch_page("main.py")
            else:
                st.error(f"❌ {message}")

# Back button outside the form
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("← Back to Login", use_container_width=True):
        st.switch_page("main.py")