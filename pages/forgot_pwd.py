import streamlit as st
import sqlite3
import hashlib
import re
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import os
import base64

# ---------- LOAD IMAGES AS BASE64 ----------
def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII="
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

arrow_img_base64 = get_base64_image("sources/arrow.png")

# ---------- DATABASE FUNCTIONS ----------
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_email(email):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
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

# ---------- EMAIL VERIFICATION FUNCTIONS ----------
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(recipient_email, code):
    try:
        sender_email = "your_email@gmail.com"
        sender_password = "your_app_password"
        
        subject = "Password Reset Verification Code"
        body = f"""
        Hello,
        
        You requested to reset your password for SurveyBot.
        
        Your verification code is: {code}
        
        This code will expire in 5 minutes.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        SurveyBot Team
        """
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login(sender_email, sender_password)
        # server.send_message(msg)
        # server.quit()
        
        return True, "Verification code sent to your email!"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Forgot Password",
    page_icon="🔑",
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

        /* ---------- FORCE BACK BUTTON TO ABSOLUTE CORNER ---------- */
        div[data-testid="stHorizontalBlock"]:has(.st-key-back_button) {{
            position: relative !important;
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            margin-top: 1rem !important; 
            margin-bottom: 2rem !important;
        }}

        .st-key-back_button {{
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
        }}

        .st-key-back_button button {{
            width: 50px !important;
            height: 50px !important;
            min-width: 50px !important;
            min-height: 50px !important;
            padding: 0 !important;
            margin: 0 !important;
            background-color: transparent !important;
            background-image: url("data:image/png;base64,{arrow_img_base64}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            border: none !important;
            border-radius: 50% !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }}

        .st-key-back_button button:hover {{
            transform: scale(1.08) !important;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25) !important;
        }}

        .st-key-back_button button p {{
            display: none !important;
        }}

        /* ---------- WHITE INPUT CONTAINERS (Email, Code, Password) ---------- */
        div[data-testid="stTextInput"] > div > div > input {{
            background-color: #ffffff !important;
            border-radius: 12px !important;
            border: 1px solid #d0e3f5 !important;
            padding: 0.6rem 1rem !important;
            color: #1a1a1a !important;
            box-shadow: 0 2px 8px rgba(91, 134, 229, 0.08) !important;
            transition: all 0.2s ease !important;
        }}

        div[data-testid="stTextInput"] > div > div > input:focus {{
            border-color: #5b86e5 !important;
            box-shadow: 0 0 0 3px rgba(91, 134, 229, 0.2) !important;
            outline: none !important;
        }}

        /* ---------- BIGGER INPUT LABELS (Email / Code / Password) ---------- */
        div[data-testid="stTextInput"] label p {{
            font-size: 20px !important;
            font-weight: 700 !important;
            color: #1B5E20 !important;
            letter-spacing: 0.3px !important;
        }}

        /* ---------- PRIMARY ACTION BUTTONS (Send / Verify / Reset / Login) ---------- */
        div.stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, #36d1dc 0%, #5b86e5 100%) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            letter-spacing: 0.3px !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 0.75rem 1.5rem !important;
            box-shadow: 0 4px 14px rgba(91, 134, 229, 0.35) !important;
            transition: all 0.25s ease !important;
        }}

        div.stButton > button[kind="primary"]:hover {{
            background: linear-gradient(135deg, #2bc0ca 0%, #4a74d4 100%) !important;
            box-shadow: 0 6px 20px rgba(91, 134, 229, 0.5) !important;
            transform: translateY(-2px) !important;
        }}

        div.stButton > button[kind="primary"]:active {{
            transform: translateY(0px) !important;
            box-shadow: 0 3px 10px rgba(91, 134, 229, 0.4) !important;
        }}

        div.stButton > button[kind="primary"]:focus-visible {{
            outline: 3px solid rgba(91, 134, 229, 0.5) !important;
            outline-offset: 2px !important;
        }}

        /* ---------- SECONDARY BUTTONS (Resend / Back to Email) ---------- */
        div.stButton > button[kind="secondary"] {{
            background: #ffffff !important;
            color: #5b86e5 !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            border: 2px solid #5b86e5 !important;
            border-radius: 25px !important;
            padding: 0.4rem 0.7rem !important;
            box-shadow: 0 2px 8px rgba(91, 134, 229, 0.15) !important;
            transition: all 0.25s ease !important;
            white-space: nowrap !important;
        }}

        div.stButton > button[kind="secondary"]:hover {{
            background: #5b86e5 !important;
            color: #ffffff !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 18px rgba(91, 134, 229, 0.35) !important;
        }}

        div.stButton > button[kind="secondary"]:active {{
            transform: translateY(0px) !important;
        }}

        div.stButton > button[kind="secondary"]:focus-visible {{
            outline: 3px solid rgba(91, 134, 229, 0.5) !important;
            outline-offset: 2px !important;
        }}

        /* ---------- FIXED-WIDTH WRAPPER FOR SECONDARY BUTTONS ---------- */
        .st-key-short_btn_wrap div.stButton > button {{
            max-width: 140px !important;
            margin: 0 auto !important;
            display: block !important;
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

# ---------- TOP NAVIGATION: BACK BUTTON ----------
with st.container():
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="st-key-back_button">', unsafe_allow_html=True)
        if st.button("Back", key="back_button", help="Back to Login"):
            st.switch_page("pages/login.py")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "reset_step" not in st.session_state:
    st.session_state.reset_step = "email"
if "reset_email" not in st.session_state:
    st.session_state.reset_email = ""
if "verification_code" not in st.session_state:
    st.session_state.verification_code = ""
if "reset_success" not in st.session_state:
    st.session_state.reset_success = False
if "code_verified" not in st.session_state:
    st.session_state.code_verified = False
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

# ---------- MAIN CONTENT ----------
st.title("🔑 Forgot Password")

# ---------- STEP 1: ENTER EMAIL ----------
if st.session_state.reset_step == "email":
    st.write("Enter your email address to receive a verification code.")
    
    reset_email = st.text_input("Email Address", placeholder="you@example.com", key="email_input")
    
    # Centered, shorter button (middle column only)
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    with btn_col2:
        send_clicked = st.button("📧 Send Verification Code", type="primary", use_container_width=True)
    
    if send_clicked:
        if not reset_email:
            st.warning("⚠️ Please enter your email address.")
        elif not validate_email(reset_email):
            st.warning("⚠️ Please enter a valid email address.")
        else:
            user = get_user_by_email(reset_email)
            if user:
                code = generate_verification_code()
                st.session_state.verification_code = code
                st.session_state.reset_email = reset_email
                st.session_state.reset_step = "verify"
                st.session_state.attempts = 0
                
                success, message = send_verification_email(reset_email, code)
                if success:
                    st.success(f"✅ {message}")
                    st.info("📩 Please check your email for the verification code.")
                    st.rerun()
                else:
                    st.warning("⚠️ Could not send email. Using demo mode.")
                    st.info(f"📝 Your verification code is: **{code}** (for testing)")
                    st.rerun()
            else:
                st.error("❌ No account found with this email address.")

# ---------- STEP 2: VERIFY CODE ----------
elif st.session_state.reset_step == "verify":
    st.write(f"📩 A verification code has been sent to **{st.session_state.reset_email}**")
    st.write("Enter the 6-digit code below:")
    
    if st.checkbox("Show code (testing only)"):
        st.info(f"📝 Your verification code is: **{st.session_state.verification_code}**")
    
    code_input = st.text_input("Verification Code", placeholder="Enter 6-digit code", max_chars=6)
    
    # Centered, shorter Verify button
    v_col1, v_col2, v_col3 = st.columns([1, 2, 1])
    with v_col2:
        verify_clicked = st.button("✅ Verify Code", type="primary", use_container_width=True)
    
    if verify_clicked:
        if not code_input:
            st.warning("⚠️ Please enter the verification code.")
        elif code_input == st.session_state.verification_code:
            st.session_state.code_verified = True
            st.session_state.reset_step = "reset"
            st.success("✅ Code verified! Now set your new password.")
            st.rerun()
        else:
            st.session_state.attempts += 1
            remaining = 3 - st.session_state.attempts
            if remaining > 0:
                st.error(f"❌ Invalid code. {remaining} attempts remaining.")
            else:
                st.error("❌ Too many failed attempts. Please start over.")
                st.session_state.reset_step = "email"
                st.rerun()
    
    # Side-by-side shorter Resend / Back buttons
    col1, col2, col3, col4, col5 = st.columns([1.5, 1, 0.3, 1, 1.5])
    with col2:
        st.markdown('<div class="st-key-short_btn_wrap">', unsafe_allow_html=True)
        if st.button("🔄 Resend Code", type="secondary", use_container_width=True):
            code = generate_verification_code()
            st.session_state.verification_code = code
            st.success(f"✅ New code sent to {st.session_state.reset_email}")
            st.info(f"📝 Your new code is: **{code}** (for testing)")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="st-key-short_btn_wrap">', unsafe_allow_html=True)
        if st.button("← Back to Email", type="secondary", use_container_width=True):
            st.session_state.reset_step = "email"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ---------- STEP 3: RESET PASSWORD ----------
elif st.session_state.reset_step == "reset":
    st.write(f"🔐 Set new password for **{st.session_state.reset_email}**")
    
    new_password = st.text_input("New Password", type="password", placeholder="Min 6 characters")
    confirm_password = st.text_input("Confirm New Password", type="password")
    
    # Centered, shorter Reset button
    r_col1, r_col2, r_col3 = st.columns([1, 2, 1])
    with r_col2:
        reset_clicked = st.button("🔄 Reset Password", type="primary", use_container_width=True)
    
    if reset_clicked:
        if not new_password:
            st.warning("⚠️ Please enter a new password.")
        elif len(new_password) < 6:
            st.warning("⚠️ Password must be at least 6 characters.")
        elif new_password != confirm_password:
            st.warning("⚠️ Passwords do not match.")
        else:
            update_password(st.session_state.reset_email, new_password)
            st.success("✅ Password reset successfully!")
            st.balloons()
            st.session_state.reset_success = True
            st.session_state.reset_step = "complete"
            st.rerun()

# ---------- STEP 4: COMPLETE ----------
elif st.session_state.reset_step == "complete":
    st.success("✅ Password reset successful!")
    st.write("You can now login with your new password.")
    
    # Centered, shorter Login button
    l_col1, l_col2, l_col3 = st.columns([1, 2, 1])
    with l_col2:
        if st.button("🔐 Go to Login", type="primary", use_container_width=True):
            st.session_state.reset_success = False
            st.session_state.reset_step = "email"
            st.session_state.code_verified = False
            st.switch_page("pages/login.py")