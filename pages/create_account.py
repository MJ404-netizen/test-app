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
    try:
        c.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_ci "
            "ON users(username COLLATE NOCASE)"
        )
    except sqlite3.IntegrityError:
        pass
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
        msg = str(e).lower()
        if "username" in msg:
            return False, "This username is already taken. Please choose another."
        elif "email" in msg:
            return False, "Email already registered. Please login."
        return False, "An error occurred. Please try again."
    finally:
        conn.close()

# ---------- EMAIL VALIDATION (REGEX) ----------
def validate_email_format(email):
    pattern = (
        r"^(?=.{1,254}$)"
        r"(?!.*\.\.)"
        r"(?=.{1,64}@)"
        r"[A-Za-z0-9]"
        r"(?:[A-Za-z0-9._%+\-]*[A-Za-z0-9])?"
        r"@"
        r"(?:[A-Za-z0-9]"
        r"(?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?\.)+"
        r"[A-Za-z]{2,24}$"
    )
    return re.fullmatch(pattern, email) is not None

# ---------- PASSWORD VALIDATION ----------
def validate_password_strength(password):
    missing = []
    if len(password) < 8:
        missing.append("at least 8 characters")
    if not re.search(r"[A-Za-z]", password):
        missing.append("at least 1 letter")
    if not re.search(r"\d", password):
        missing.append("at least 1 number (0–9)")
    if not re.search(r"[^A-Za-z0-9\s]", password):
        missing.append("at least 1 symbol (e.g. ! @ # $ % ^ & *)")
    if re.search(r"\s", password):
        missing.append("no spaces")
    return (len(missing) == 0), missing

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
                    return False, f"Did you mean: **{data['typo_suggestion']}**?"
                elif data.get("disposable", False):
                    return False, "Please use a permanent email address (not temporary)."
                else:
                    return False, "This email address appears to be invalid."
        else:
            return None, "Verification service unavailable — proceeding with format check only."
    except Exception as e:
        return None, f"Could not verify email: {str(e)}"

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

        div[data-testid="stTextInput"] label p {{
            font-size: 20px !important;
            font-weight: 700 !important;
            color: #1B5E20 !important;
            letter-spacing: 0.3px !important;
        }}

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

        div[data-testid="stButton"] {{
            display: flex !important;
            justify-content: center !important;
        }}

        .field-error {{
            color: #D32F2F !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            margin-top: -8px !important;
            margin-bottom: 12px !important;
            padding-left: 4px !important;
        }}

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
if "show_success" not in st.session_state:
    st.session_state.show_success = False
if "created_username" not in st.session_state:
    st.session_state.created_username = ""
if "created_email" not in st.session_state:
    st.session_state.created_email = ""

for _k in ("err_username", "err_email", "err_password", "err_confirm"):
    st.session_state.setdefault(_k, "")

# ---------- MAIN CONTENT ----------
# Check if user is already logged in
if "logged_in" in st.session_state and st.session_state.logged_in:
    st.success(f"You are already logged in as {st.session_state.get('username', 'User')}!")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/test_page.py")
    st.stop()

# ---------- SUCCESS PAGE ----------
if st.session_state.show_success:
    st.title("🎉 Account Created!")
    st.success("Your account has been successfully created.")
    
    st.markdown(f"""
    <div style="background-color: #F1F8E9; padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50; margin-bottom: 20px;">
        <p style="margin: 0; font-size: 16px; color: #333;"><strong>Username:</strong> {st.session_state.created_username}</p>
        <p style="margin: 5px 0 0 0; font-size: 16px; color: #333;"><strong>Email:</strong> {st.session_state.created_email}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("You can now log in using the credentials you just created.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐 Go to Login", use_container_width=True):
            # Reset all states
            st.session_state.show_success = False
            st.session_state.account_created = False
            st.session_state.created_username = ""
            st.session_state.created_email = ""
            for _k in ("err_username", "err_email", "err_password", "err_confirm"):
                st.session_state[_k] = ""
            st.switch_page("pages/login.py")
            
    # Stop rendering the form
    st.stop()

# ---------- CREATE ACCOUNT FORM ----------
st.title("📝 Create Account")

username = st.text_input(
    "Create a username",
    placeholder="3–20 chars, letters/digits/underscore",
    key="input_username",
)
if st.session_state.err_username:
    st.markdown(
        f"<div class='field-error'>⚠️ {st.session_state.err_username}</div>",
        unsafe_allow_html=True,
    )

email = st.text_input(
    "Enter your email",
    placeholder="name@gmail.com",
    key="input_email",
)
if st.session_state.err_email:
    st.markdown(
        f"<div class='field-error'>⚠️ {st.session_state.err_email}</div>",
        unsafe_allow_html=True,
    )

password = st.text_input(
    "Create password",
    type="password",
    placeholder="Min 8 chars: letters, numbers, symbols",
    key="input_password",
)

if password:
    checks = [
        (len(password) >= 8,                          "at least 8 characters"),
        (bool(re.search(r"[A-Za-z]", password)),      "1 letter"),
        (bool(re.search(r"\d", password)),            "1 number"),
        (bool(re.search(r"[^A-Za-z0-9\s]", password)), "1 symbol"),
        (not re.search(r"\s", password),              "no spaces"),
    ]
    items = "".join(
        f"<div style='font-size:14px; margin:2px 0; "
        f"color:{'#2E7D32' if ok else '#9E9E9E'};'>"
        f"{'✅' if ok else '⬜'} {label}</div>"
        for ok, label in checks
    )
    st.markdown(
        f"<div style='background:#F1F8E9; border-left:3px solid #A5D6A7; "
        f"padding:8px 12px; border-radius:6px; margin-top:-8px; margin-bottom:12px;'>"
        f"{items}</div>",
        unsafe_allow_html=True,
    )

if st.session_state.err_password:
    st.markdown(
        f"<div class='field-error'>⚠️ {st.session_state.err_password}</div>",
        unsafe_allow_html=True,
    )

confirm = st.text_input(
    "Confirm password",
    type="password",
    placeholder="Re-enter password",
    key="input_confirm",
)
if st.session_state.err_confirm:
    st.markdown(
        f"<div class='field-error'>⚠️ {st.session_state.err_confirm}</div>",
        unsafe_allow_html=True,
    )

btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
with btn_col2:
    submitted = st.button("✨ Create Account", use_container_width=True)

if submitted:
    for _k in ("err_username", "err_email", "err_password", "err_confirm"):
        st.session_state[_k] = ""

    ok = True

    # ---- username (PRESERVES CASE) ----
    uname = (username or "").strip()
    if not uname:
        st.session_state.err_username = "Username cannot be empty."
        ok = False
    elif len(uname) < 3:
        st.session_state.err_username = "Username must be at least 3 characters."
        ok = False
    elif len(uname) > 20:
        st.session_state.err_username = "Username must be 20 characters or fewer."
        ok = False
    elif not re.fullmatch(r"[A-Za-z0-9_]+", uname):
        st.session_state.err_username = "Username may only contain letters, digits, and underscores."
        ok = False

    # ---- email (regex-based) ----
    email_clean = (email or "").strip()
    if not email_clean:
        st.session_state.err_email = "Email cannot be empty."
        ok = False
    elif "@" not in email_clean:
        st.session_state.err_email = "Email must contain an '@' (e.g. name@gmail.com)."
        ok = False
    elif email_clean.count("@") != 1:
        st.session_state.err_email = "Email must contain exactly one '@'."
        ok = False
    elif ".." in email_clean:
        st.session_state.err_email = "Email cannot contain consecutive dots ('..')."
        ok = False
    elif email_clean.startswith(".") or email_clean.endswith("."):
        st.session_state.err_email = "Email cannot start or end with a dot."
        ok = False
    elif " " in email_clean:
        st.session_state.err_email = "Email cannot contain spaces."
        ok = False
    elif not validate_email_format(email_clean):
        st.session_state.err_email = (
            "Please enter a valid email address "
            "(e.g. name@gmail.com — valid domain, 2+ letter TLD)."
        )
        ok = False
    else:
        email_clean = email_clean.lower()

    # ---- password ----
    if not password:
        st.session_state.err_password = "Password cannot be empty."
        ok = False
    else:
        pw_ok, missing = validate_password_strength(password)
        if not pw_ok:
            st.session_state.err_password = (
                "Password must contain " + ", ".join(missing) + "."
            )
            ok = False

    # ---- confirm ----
    if not confirm:
        st.session_state.err_confirm = "Please re-enter your password."
        ok = False
    elif password and confirm != password:
        st.session_state.err_confirm = "Passwords do not match."
        ok = False

    # ---- DB uniqueness (case-insensitive username + email) ----
    if ok:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        c.execute("SELECT 1 FROM users WHERE LOWER(TRIM(username)) = ?", (uname.lower(),))
        if c.fetchone():
            st.session_state.err_username = "This username is already taken. Please choose another."
            ok = False
            
        c.execute("SELECT 1 FROM users WHERE LOWER(TRIM(email)) = ?", (email_clean,))
        if c.fetchone():
            st.session_state.err_email = "This email is already registered. Try logging in."
            ok = False
            
        conn.close()

    # ---- server-side email verification ----
    if ok:
        trusted_domains = ("@gmail.com", "@yahoo.com", "@outlook.com", "@hotmail.com", "@icloud.com")
        if email_clean.endswith(trusted_domains):
            pass
        else:
            with st.spinner("Verifying email address..."):
                valid, message = verify_email(email_clean)
            
            if valid is False:
                if "Did you mean" in message or "temporary" in message:
                    st.session_state.err_email = message
                    ok = False

    # ---- create ----
    if ok:
        success, msg = create_user(uname, email_clean, password)
        if success:
            st.session_state.created_username = uname
            st.session_state.created_email = email_clean
            st.session_state.show_success = True
            st.rerun()
        else:
            low = msg.lower()
            if "username" in low:
                st.session_state.err_username = msg
            elif "email" in low:
                st.session_state.err_email = msg
            else:
                st.error(f"❌ {msg}")

    if not ok:
        st.rerun()