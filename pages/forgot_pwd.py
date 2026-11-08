import streamlit as st
import sqlite3
import hashlib
import re
import random
import string
import time
import os
import base64
import smtplib
from email.message import EmailMessage

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

def update_password(email, new_password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET password = ? WHERE LOWER(TRIM(email)) = ?",
        (hash_password(new_password), email.strip().lower())
    )
    conn.commit()
    conn.close()
    return True

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password):
    """Matches the rules from create_account.py"""
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

def get_username_from_db(email):
    """Fetches the username for a given email, or None if not found"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE LOWER(TRIM(email)) = ?", (email.strip().lower(),))
    result = c.fetchone()
    conn.close()
    return result["username"] if result else None

# ---------- EMAIL VERIFICATION FUNCTIONS ----------
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(recipient_email, username, code):
    try:
        # Load credentials from secrets.toml
        sender_email = st.secrets["gmail"]["email"]
        app_password = st.secrets["gmail"]["app_password"]

        # Create the email
        msg = EmailMessage()
        msg['Subject'] = "Account Recovery - Verification Code"
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # HTML version of the email
        html_content = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #1B5E20;">Account Recovery</h2>
            <p>You requested to reset your password for SurveyBot.</p>
            
            <p style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; font-size: 16px;">
                <strong>Your Username:</strong> {username}
            </p>
            
            <p>Your verification code is:</p>
            <h1 style="color: #4CAF50; letter-spacing: 5px;">{code}</h1>
            <p style="color: #666; font-size: 12px;">This code will expire in 5 minutes.</p>
        </div>
        """
        
        # Plain text fallback (if HTML is blocked)
        plain_text = f"Your username is: {username}\n\nYour verification code is: {code}"

        msg.set_content(plain_text)
        msg.add_alternative(html_content, subtype='html')

        # --- SMTP CONNECTION WITH FALLBACK ---
        try:
            # Try Port 587 with STARTTLS first (Standard)
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.ehlo()          # Identify ourselves
                smtp.starttls()      # Upgrade to secure
                smtp.ehlo()          # Identify again over secure
                smtp.login(sender_email, app_password)
                smtp.send_message(msg)
        except Exception as e_587:
            # If 587 fails, try Port 465 with SSL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(sender_email, app_password)
                smtp.send_message(msg)

        return True, f"Verification code sent to {recipient_email}!"
        
    except Exception as e:
        # Print full traceback to the terminal for debugging
        import traceback
        traceback.print_exc()
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

        div[data-testid="stTextInput"] label p {{
            font-size: 20px !important;
            font-weight: 700 !important;
            color: #1B5E20 !important;
            letter-spacing: 0.3px !important;
        }}

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

        /* Disabled state for the resend button */
        div.stButton > button:disabled {{
            opacity: 0.5 !important;
            cursor: not-allowed !important;
            background: #e0e0e0 !important;
            color: #888888 !important;
            border-color: #cccccc !important;
            transform: none !important;
            box-shadow: none !important;
        }}

        .st-key-short_btn_wrap div.stButton > button {{
            max-width: 140px !important;
            margin: 0 auto !important;
            display: block !important;
        }}

        /* ---------- INLINE FIELD ERROR STYLE ---------- */
        .field-error {{
            color: #D32F2F !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            margin-top: -8px !important;
            margin-bottom: 12px !important;
            padding-left: 4px !important;
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
if "last_sent_time" not in st.session_state:
    st.session_state.last_sent_time = 0
if "err_new_password" not in st.session_state:
    st.session_state.err_new_password = ""
if "err_confirm_password" not in st.session_state:
    st.session_state.err_confirm_password = ""

# ---------- MAIN CONTENT ----------
st.title("🔑 Forgot Password / Username")

# ---------- STEP 1: ENTER EMAIL ----------
if st.session_state.reset_step == "email":
    st.write("Enter your email address to recover your username and reset your password.")
    
    reset_email = st.text_input("Email Address", placeholder="you@example.com", key="email_input")
    
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    with btn_col2:
        send_clicked = st.button("📧 Send Verification Code", type="primary", use_container_width=True)
    
    if send_clicked:
        if not reset_email:
            st.warning("⚠️ Please enter your email address.")
        elif not validate_email(reset_email):
            st.warning("⚠️ Please enter a valid email address.")
        else:
            # Fetch username instead of just checking existence
            username = get_username_from_db(reset_email)
            
            if username:
                code = generate_verification_code()
                st.session_state.verification_code = code
                st.session_state.reset_email = reset_email
                
                # Pass the username to the email function
                success, message = send_verification_email(reset_email, username, code)
                
                if success:
                    st.session_state.reset_step = "verify"
                    st.session_state.attempts = 0
                    st.session_state.last_sent_time = time.time() # Start cooldown timer
                    st.success(f"✅ {message}")
                    st.info(f"📩 We sent an email to **{reset_email}**. It contains your username and verification code.")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.error("❌ This email address is not registered in our system.")

# ---------- STEP 2: VERIFY CODE ----------
elif st.session_state.reset_step == "verify":
    st.write(f"📩 A verification code has been sent to **{st.session_state.reset_email}**")
    st.write("Enter the 6-digit code below:")
    
    # Testing checkbox - REMOVE THIS BEFORE LAUNCH
    if st.checkbox("Show code (testing only)"):
        st.info(f"📝 Your verification code is: **{st.session_state.verification_code}**")
    
    code_input = st.text_input("Verification Code", placeholder="Enter 6-digit code", max_chars=6)
    
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
    
    col1, col2, col3, col4, col5 = st.columns([1.5, 1, 0.3, 1, 1.5])
    with col2:
        st.markdown('<div class="st-key-short_btn_wrap">', unsafe_allow_html=True)
        
        # Calculate cooldown
        time_passed = time.time() - st.session_state.last_sent_time
        can_resend = time_passed > 60
        
        if st.button("🔄 Resend Code", type="secondary", use_container_width=True, disabled=not can_resend):
            code = generate_verification_code()
            st.session_state.verification_code = code
            st.session_state.last_sent_time = time.time() # Reset timer
            
            # Fetch username again for the resend email
            username = get_username_from_db(st.session_state.reset_email)
            success, message = send_verification_email(st.session_state.reset_email, username, code)
            
            if success:
                st.success(f"✅ New code sent to {st.session_state.reset_email}")
            else:
                st.error(f"❌ {message}")
            st.rerun()
            
        if not can_resend:
            st.caption(f"Wait {int(60 - time_passed)}s")
            
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
    
    new_password = st.text_input("New Password", type="password", placeholder="Min 8 chars: letters, numbers, symbols")
    
    # Live password checklist
    if new_password:
        checks = [
            (len(new_password) >= 8,                           "at least 8 characters"),
            (bool(re.search(r"[A-Za-z]", new_password)),       "1 letter"),
            (bool(re.search(r"\d", new_password)),             "1 number"),
            (bool(re.search(r"[^A-Za-z0-9\s]", new_password)), "1 symbol"),
            (not re.search(r"\s", new_password),               "no spaces"),
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
        
    if st.session_state.err_new_password:
        st.markdown(
            f"<div class='field-error'>⚠️ {st.session_state.err_new_password}</div>",
            unsafe_allow_html=True,
        )

    confirm_password = st.text_input("Confirm New Password", type="password")
    
    if st.session_state.err_confirm_password:
        st.markdown(
            f"<div class='field-error'>⚠️ {st.session_state.err_confirm_password}</div>",
            unsafe_allow_html=True,
        )
        
    r_col1, r_col2, r_col3 = st.columns([1, 2, 1])
    with r_col2:
        reset_clicked = st.button("🔄 Reset Password", type="primary", use_container_width=True)
    
    if reset_clicked:
        # Reset errors
        st.session_state.err_new_password = ""
        st.session_state.err_confirm_password = ""
        ok = True
        
        if not new_password:
            st.session_state.err_new_password = "Password cannot be empty."
            ok = False
        else:
            pw_ok, missing = validate_password_strength(new_password)
            if not pw_ok:
                st.session_state.err_new_password = "Password must contain " + ", ".join(missing) + "."
                ok = False
                
        if not confirm_password:
            st.session_state.err_confirm_password = "Please re-enter your new password."
            ok = False
        elif new_password and confirm_password != new_password:
            st.session_state.err_confirm_password = "Passwords do not match."
            ok = False
            
        if ok:
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
    
    l_col1, l_col2, l_col3 = st.columns([1, 2, 1])
    with l_col2:
        if st.button("🔐 Go to Login", type="primary", use_container_width=True):
            st.session_state.reset_success = False
            st.session_state.reset_step = "email"
            st.session_state.code_verified = False
            st.switch_page("pages/login.py")