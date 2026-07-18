import streamlit as st
import sqlite3
import hashlib
import re
import requests
import time

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

def validate_email_format(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ---------- EMAIL VERIFICATION FUNCTION ----------
def verify_email(email):
    """
    Verify if an email address actually exists.
    Uses free API - no API key required.
    """
    try:
        # Free email verification API
        url = "https://rapid-email-verifier.fly.dev/api/validate"
        
        response = requests.post(
            url,
            json={"email": email},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if email is valid
            if data.get("valid", False):
                return True, "✅ Email verified successfully!"
            else:
                # Check for typo suggestions
                if data.get("typo_suggestion"):
                    return False, f"❌ Did you mean: **{data['typo_suggestion']}**?"
                elif data.get("disposable", False):
                    return False, "❌ Please use a permanent email address (not temporary)."
                else:
                    return False, "❌ This email address appears to be invalid."
        else:
            return None, "⚠️ Verification service unavailable. Proceeding with format check only."
            
    except Exception as e:
        return None, f"⚠️ Could not verify email: {str(e)}"

# ---------- INITIALIZE DATABASE ----------
init_db()

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Create Account",
    page_icon="📝",
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
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "account_created" not in st.session_state:
    st.session_state.account_created = False

# ---------- MAIN CONTENT ----------
st.title("📝 Create Account")

# Check if user is already logged in
if "logged_in" in st.session_state and st.session_state.logged_in:
    st.success(f"You are already logged in as {st.session_state.get('username', 'User')}!")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/dashboard.py")
    st.stop()

# ---------- CREATE ACCOUNT FORM ----------
with st.form("create_account_form"):
    username = st.text_input("Create a username", placeholder="Choose a unique username")
    email = st.text_input("Enter your email", placeholder="you@example.com")
    password = st.text_input("Create password", type="password", placeholder="Min 6 characters")
    confirm = st.text_input("Confirm password", type="password", placeholder="Re-enter password")
    
    # Main submit button
    submitted = st.form_submit_button("✨ Create Account", use_container_width=True)
    
    if submitted:
        # Validate inputs
        if not username or not email or not password:
            st.warning("⚠️ Please fill in all fields.")
        elif len(username) < 3:
            st.warning("⚠️ Username must be at least 3 characters.")
        elif not validate_email_format(email):
            st.warning("⚠️ Please enter a valid email address.")
        elif len(password) < 6:
            st.warning("⚠️ Password must be at least 6 characters.")
        elif password != confirm:
            st.warning("⚠️ Passwords do not match.")
        else:
            # Check if email already exists in database
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email = ?", (email,))
            existing_user = c.fetchone()
            conn.close()
            
            if existing_user:
                st.error("❌ This email is already registered. Please login.")
            else:
                # Verify the email
                with st.spinner("Verifying email address..."):
                    valid, message = verify_email(email)
                
                # If verification failed or API unavailable, still allow account creation
                # (You can change this behavior by uncommenting the check below)
                if valid is False:
                    st.error(message)
                else:
                    if valid is None:
                        st.warning(message)
                    else:
                        st.success(message)
                    
                    # Create the account
                    success, msg = create_user(username, email, password)
                    if success:
                        st.success(f"✅ {msg}")
                        st.balloons()
                        st.info("You can now login with your credentials!")
                        st.session_state.account_created = True
                    else:
                        st.error(f"❌ {msg}")

# ---------- BACK BUTTONS (OUTSIDE THE FORM) ----------
if st.session_state.account_created:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔐 Go to Login", use_container_width=True):
            st.session_state.account_created = False
            st.switch_page("pages/login.py")
else:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("← Back to Home", use_container_width=True):
            st.switch_page("main.py")