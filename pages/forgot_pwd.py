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
    """
    Send verification code via email (requires SMTP setup)
    This is a template - you need to configure with your email provider
    """
    try:
        # Email configuration (REPLACE WITH YOUR SETTINGS)
        sender_email = "your_email@gmail.com"
        sender_password = "your_app_password"  # Use App Password for Gmail
        
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
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email (uncomment when configured)
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
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp {
            background: linear-gradient(#c7f9ff, #dafbff, #fbffdb, #d5f7cb, #c7f9ff);
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

# ---------- SESSION STATE ----------
if "reset_step" not in st.session_state:
    st.session_state.reset_step = "email"  # email | verify | reset
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
    
    with st.form("email_form"):
        reset_email = st.text_input("Email Address", placeholder="you@example.com")
        
        submitted = st.form_submit_button("📧 Send Verification Code", use_container_width=True)
        
        if submitted:
            if not reset_email:
                st.warning("⚠️ Please enter your email address.")
            elif not validate_email(reset_email):
                st.warning("⚠️ Please enter a valid email address.")
            else:
                # Check if email exists in database
                user = get_user_by_email(reset_email)
                if user:
                    # Generate and store verification code
                    code = generate_verification_code()
                    st.session_state.verification_code = code
                    st.session_state.reset_email = reset_email
                    st.session_state.reset_step = "verify"
                    st.session_state.attempts = 0
                    
                    # Send verification email
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
    
    # Back to login
    if st.button("← Back to Login", use_container_width=True):
        st.switch_page("pages/login.py")

# ---------- STEP 2: VERIFY CODE ----------
elif st.session_state.reset_step == "verify":
    st.write(f"📩 A verification code has been sent to **{st.session_state.reset_email}**")
    st.write("Enter the 6-digit code below:")
    
    # Show code for testing (remove in production)
    if st.checkbox("Show code (testing only)"):
        st.info(f"📝 Your verification code is: **{st.session_state.verification_code}**")
    
    with st.form("verify_form"):
        code_input = st.text_input("Verification Code", placeholder="Enter 6-digit code", max_chars=6)
        
        submitted = st.form_submit_button("✅ Verify Code", use_container_width=True)
        
        if submitted:
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
    
    # Resend code
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Resend Code", use_container_width=True):
            code = generate_verification_code()
            st.session_state.verification_code = code
            st.success(f"✅ New code sent to {st.session_state.reset_email}")
            st.info(f"📝 Your new code is: **{code}** (for testing)")
            st.rerun()
    
    with col2:
        if st.button("← Back to Email", use_container_width=True):
            st.session_state.reset_step = "email"
            st.rerun()

# ---------- STEP 3: RESET PASSWORD ----------
elif st.session_state.reset_step == "reset":
    st.write(f"🔐 Set new password for **{st.session_state.reset_email}**")
    
    with st.form("reset_form"):
        new_password = st.text_input("New Password", type="password", placeholder="Min 6 characters")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("🔄 Reset Password", use_container_width=True)
        
        if submitted:
            if not new_password:
                st.warning("⚠️ Please enter a new password.")
            elif len(new_password) < 6:
                st.warning("⚠️ Password must be at least 6 characters.")
            elif new_password != confirm_password:
                st.warning("⚠️ Passwords do not match.")
            else:
                # Update password in database
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
    
    if st.button("🔐 Go to Login", use_container_width=True):
        st.session_state.reset_success = False
        st.session_state.reset_step = "email"
        st.session_state.code_verified = False
        st.switch_page("pages/login.py")