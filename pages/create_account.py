import streamlit as st
import sqlite3
import hashlib
import re
import requests
import time
import os
import base64

# ---------- LOAD IMAGES AS BASE64 ----------
def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII="
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

home_img_base64 = get_base64_image("sources/home.png")

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
    try:
        url = "https://rapid-email-verifier.fly.dev/api/validate"
        response = requests.post(url, json={"email": email}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("valid", False):
                return True, "✅ Email verified successfully!"
            else:
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
hide_streamlit_style = f"""
    <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* --- REMOVE TOP SPACING --- */
        .block-container {{
            padding-top: 0rem !important; 
            padding-bottom: 2rem !important;
        }}
        .stApp > header {{
            display: none !important;
        }}
        /* --------------------------- */
        
        .stApp {{
            background: linear-gradient(#c7f9ff, #dafbff, #fbffdb, #d5f7cb, #c7f9ff);
        }}

        /* ---------- FORCE HOME BUTTON TO ABSOLUTE CORNER (HIGHER) ---------- */
        div[data-testid="stHorizontalBlock"]:has(.st-key-home_button) {{
            position: relative !important;
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            margin-top: 3rem !important; 
            margin-bottom: 1rem !important;
        }}

        .st-key-home_button {{
            position: absolute !important;
            left: 0 !important;
            top: -25px !important;
        }}

        .st-key-home_button button {{
            width: 50px !important;
            height: 50px !important;
            min-width: 50px !important;
            min-height: 50px !important;
            padding: 0 !important;
            margin: 0 !important;
            background-color: transparent !important;
            background-image: url("data:image/png;base64,{home_img_base64}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            border: none !important;
            border-radius: 50% !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }}

        .st-key-home_button button:hover {{
            transform: scale(1.08) !important;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25) !important;
        }}

        .st-key-home_button button p {{
            display: none !important;
        }}

        /* ---------- PURE WHITE INPUT CONTAINERS ---------- */
        div[data-testid="stTextInput"] div[data-baseweb="input"],
        div[data-testid="stTextInput"] div[data-baseweb="base-input"],
        div[data-testid="stTextInput"] div[data-baseweb="input"] > div,
        div[data-testid="stTextInput"] div[data-baseweb="base-input"] > div {{
            background-color: #FFFFFF !important;
            background: #FFFFFF !important;
        }}

        div[data-testid="stTextInput"] div[data-baseweb="input"] {{
            border-radius: 8px !important;
            border: 1px solid #A5D6A7 !important;
            transition: all 0.2s ease !important;
        }}

        div[data-testid="stTextInput"] input {{
            background-color: #FFFFFF !important;
            background: #FFFFFF !important;
            color: #333333 !important;
            border: none !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            padding: 0.6rem 0.8rem !important;
            font-size: 16px !important;
        }}

        div[data-testid="stTextInput"] input:-webkit-autofill,
        div[data-testid="stTextInput"] input:-webkit-autofill:hover,
        div[data-testid="stTextInput"] input:-webkit-autofill:focus {{
            -webkit-box-shadow: 0 0 0px 1000px #FFFFFF inset !important;
            -webkit-text-fill-color: #333333 !important;
            transition: background-color 5000s ease-in-out 0s !important;
        }}

        div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {{
            background-color: #FFFFFF !important;
            border: 2px solid #4CAF50 !important;
            box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.15) !important;
        }}

        /* ---------- INPUT LABELS — SAME SIZE AS LOGIN PAGE ---------- */
        div[data-testid="stTextInput"] label p {{
            font-size: 20px !important;
            font-weight: 700 !important;
            color: #1B5E20 !important;
            letter-spacing: 0.3px !important;
        }}

        /* ---------- SHORTER CREATE ACCOUNT BUTTON ---------- */
        div.stButton > button {{
            border-radius: 60px !important;
            padding: 12px 30px !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            border: none !important;
            cursor: pointer !important;
            transition: all 0.25s ease !important;
            text-align: center !important;
            min-height: 48px !important;
            background: #4CAF50 !important;
            color: white !important;
            margin-top: 15px !important;
            width: auto !important;
        }}

        div.stButton > button:hover {{
            background: #43A047 !important;
            box-shadow: 0 14px 34px rgba(76, 175, 80, 0.40) !important;
            transform: translateY(-3px) !important;
        }}

        div.stButton > button p {{
            font-size: 18px !important;
            font-weight: 600 !important;
            margin: 0 !important;
        }}

        /* Center the button inside its container without full width */
        div[data-testid="stButton"] {{
            display: flex !important;
            justify-content: center !important;
        }}

        /* ---------- MOBILE RESPONSIVENESS ---------- */
        @media (max-width: 768px) {{
            div[data-testid="stTextInput"] label p {{
                font-size: 18px !important;
            }}
        }}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------- TOP NAVIGATION: HOME BUTTON ----------
with st.container():
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="st-key-home_button">', unsafe_allow_html=True)
        if st.button("Home", key="home_button", help="Back to Home"):
            st.switch_page("main.py")
        st.markdown('</div>', unsafe_allow_html=True)

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
username = st.text_input("Create a username", placeholder="Choose a unique username")
email = st.text_input("Enter your email", placeholder="you@example.com")
password = st.text_input("Create password", type="password", placeholder="Min 6 characters")
confirm = st.text_input("Confirm password", type="password", placeholder="Re-enter password")

# Main submit button — centered column layout instead of full-width
btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
with btn_col2:
    submitted = st.button("✨ Create Account", use_container_width=True)

if submitted:
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
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = c.fetchone()
        conn.close()
        
        if existing_user:
            st.error("❌ This email is already registered. Please login.")
        else:
            with st.spinner("Verifying email address..."):
                valid, message = verify_email(email)
            
            if valid is False:
                st.error(message)
            else:
                if valid is None:
                    st.warning(message)
                else:
                    st.success(message)
                
                success, msg = create_user(username, email, password)
                if success:
                    st.success(f"✅ {msg}")
                    st.balloons()
                    st.info("You can now login with your credentials!")
                    st.session_state.account_created = True
                else:
                    st.error(f"❌ {msg}")

# ---------- GO TO LOGIN BUTTON ----------
if st.session_state.account_created:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔐 Go to Login", use_container_width=True):
            st.session_state.account_created = False
            st.switch_page("pages/login.py")