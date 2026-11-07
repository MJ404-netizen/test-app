import streamlit as st
import sqlite3
import hashlib
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

        .stApp {{
            background: linear-gradient(#c7f9ff, #dafbff, #fbffdb, #d5f7cb, #c7f9ff);
        }}

        /* ---------- FORGOT PASSWORD LINK ---------- */
        .forgot-link-side {{
            display: flex;
            align-items: center;
            justify-content: flex-end;
            height: 100%;
            padding-top: 25px;
            padding-right: 15px;
        }}
        .forgot-link-side a {{
            color: #4CAF50;
            text-decoration: none;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: color 0.3s ease;
            white-space: nowrap;
        }}
        .forgot-link-side a:hover {{
            color: #2E7D32;
            text-decoration: underline;
        }}

        /* ---------- FORCE HOME BUTTON TO ABSOLUTE CORNER ---------- */
        div[data-testid="stHorizontalBlock"]:has(.st-key-home_button) {{
            position: relative !important;
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            margin-top: 1rem !important;
            margin-bottom: 2rem !important;
        }}

        .st-key-home_button {{
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
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

        /* ---------- LOGIN BUTTON DESIGN ---------- */
        div[data-testid="stButton"] > button {{
            width: 100% !important;
            border-radius: 60px !important;
            padding: 15px 20px !important;
            font-size: 20px !important;
            font-weight: 600 !important;
            border: none !important;
            cursor: pointer !important;
            transition: all 0.25s ease !important;
            text-align: center !important;
            min-height: 60px !important;
            background: #4CAF50 !important;
            color: white !important;
            margin-top: 15px !important;
        }}

        div[data-testid="stButton"] > button:hover {{
            background: #43A047 !important;
            box-shadow: 0 14px 34px rgba(76, 175, 80, 0.40) !important;
            transform: translateY(-3px);
        }}

        /* ---------- INPUT BOXES ---------- */
        div[data-baseweb="input"] {{
            background-color: #FFFFFF !important;
            border-radius: 8px !important;
            border: 1px solid #A5D6A7 !important;
        }}

        div[data-baseweb="base-input"] {{
            background-color: #FFFFFF !important;
        }}

        input[type="text"], input[type="password"] {{
            background-color: #FFFFFF !important;
            color: #333333 !important;
        }}

        div[data-baseweb="input"]:focus-within {{
            background-color: #FFFFFF !important;
            border: 2px solid #4CAF50 !important;
        }}

        div[data-testid="stTextInput"] label p {{
            font-size: 20px !important;
            font-weight: 700 !important;
            color: #1B5E20 !important;
            letter-spacing: 0.3px !important;
        }}

        /* ---------- MOBILE: TRUE CENTER ALIGNMENT ---------- */
        @media (max-width: 768px) {{

            /* Stack every horizontal block vertically */
            div[data-testid="stHorizontalBlock"] {{
                flex-direction: column !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 0.75rem !important;
                width: 100% !important;
            }}

            /* Every column becomes a centered full-width-ish block */
            div[data-testid="column"] {{
                width: 100% !important;
                max-width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 0 !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                justify-content: center !important;
            }}

            /* Center the title */
            h1 {{
                text-align: center !important;
                width: 100% !important;
            }}

            /* Center forgot password link */
            .forgot-link-side {{
                justify-content: center !important;
                padding: 0 !important;
                margin: 0 auto 10px auto !important;
                width: 100% !important;
                text-align: center !important;
            }}

            /* Inputs: centered, max width, no stretch to edge */
            div[data-testid="stTextInput"] {{
                width: 100% !important;
                max-width: 340px !important;
                margin: 0 auto !important;
            }}

            div[data-testid="stTextInput"] input {{
                text-align: left !important;
            }}

            div[data-testid="stTextInput"] label p {{
                font-size: 18px !important;
                text-align: left !important;
            }}

            /* Login button: centered, fixed max width */
            div[data-testid="stButton"] {{
                width: 100% !important;
                max-width: 340px !important;
                margin: 0 auto !important;
                display: flex !important;
                justify-content: center !important;
            }}

            div[data-testid="stButton"] > button {{
                width: 100% !important;
                max-width: 340px !important;
            }}

            /* Keep home button top-left and NOT stretched */
            div[data-testid="stHorizontalBlock"]:has(.st-key-home_button) {{
                flex-direction: row !important;
                align-items: center !important;
                justify-content: flex-start !important;
            }}
            div[data-testid="stHorizontalBlock"]:has(.st-key-home_button) div[data-testid="column"] {{
                width: auto !important;
                max-width: none !important;
                min-width: auto !important;
                flex: 0 0 auto !important;
                align-items: flex-start !important;
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
        if st.button("Home", key="home_button", help="Go to Home"):
            st.switch_page("main.py")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------- MAIN CONTENT ----------
st.title("🔐 Login")

# Check if user is already logged in - redirect to test page
if "logged_in" in st.session_state and st.session_state.logged_in:
    st.success(f"Welcome back, {st.session_state.get('username', 'User')}!")
    st.info("⏳ Redirecting to test page...")
    time.sleep(1)
    st.switch_page("pages/test_page.py")
    st.stop()

# ---------- CENTERED LOGIN FORM ----------
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

# ---------- BUTTON AND LINK ROW ----------
outer1, outer2, outer3 = st.columns([1, 1.2, 1])

with outer2:
    btn_col1, btn_col2 = st.columns([1.2, 1])

    with btn_col1:
        st.markdown(
            """
            <div class="forgot-link-side">
                <a href="forgot_pwd" target="_self">🔑 Forgot Password?</a>
            </div>
            """,
            unsafe_allow_html=True
        )

    with btn_col2:
        if st.button("🔐 Login", use_container_width=True):
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