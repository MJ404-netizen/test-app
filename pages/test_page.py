import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Stress Test",
    page_icon="📊",
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
        
        .welcome-container {
            text-align: center;
            padding: 40px 50px;
            background: rgba(255, 255, 255, 0.7);
            border-radius: 40px;
            backdrop-filter: blur(10px);
            margin: 20px auto;
            max-width: 700px;
            width: 100%;
        }
        .welcome-title {
            font-size: 48px;
            font-weight: 700;
            color: #1B5E20;
        }
        .welcome-subtitle {
            font-size: 24px;
            color: #2E7D32;
            margin-top: 10px;
        }
        .user-greeting {
            font-size: 28px;
            color: #1B5E20;
            font-weight: 600;
            margin: 20px 0;
        }
        
        /* FORCE BUTTON STYLES - MORE SPECIFIC SELECTORS */
        .stButton button {
            width: 100% !important;
            border-radius: 60px !important;
            padding: 25px 20px !important;
            font-size: 30px !important;
            font-weight: 600 !important;
            border: none !important;
            cursor: pointer !important;
            transition: all 0.25s ease !important;
            text-align: center !important;
            font-family: inherit !important;
            line-height: 1.4 !important;
            min-height: 80px !important;
        }
        
        .stButton {
            display: flex !important;
            justify-content: center !important;
        }
        
        /* Primary button (green) */
        .stButton button[kind="primary"] {
            background: #4CAF50 !important;
            color: white !important;
        }
        .stButton button[kind="primary"]:hover {
            background: #43A047 !important;
            box-shadow: 0 14px 34px rgba(76, 175, 80, 0.40) !important;
            transform: translateY(-3px);
        }
        
        /* Secondary button (transparent) */
        .stButton button:not([kind="primary"]) {
            background: rgba(255, 255, 255, 0.20) !important;
            color: #1B5E20 !important;
            border: 2px solid rgba(76, 175, 80, 0.3) !important;
            backdrop-filter: blur(10px);
        }
        .stButton button:not([kind="primary"]):hover {
            background: rgba(255, 255, 255, 0.35) !important;
            border-color: #4CAF50 !important;
            transform: translateY(-3px);
        }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------- CHECK LOGIN STATUS ----------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login to access this page.")
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/login.py")
    st.stop()

# ---------- WELCOME MESSAGE ----------
username = st.session_state.get("username", "User")

st.markdown(f"""
    <div class="welcome-container">
        <div class="welcome-title">📊 Stress Type Test</div>
        <div class="user-greeting">👋 Welcome, {username}!</div>
        <div class="welcome-subtitle">Discover and know your stress type with our test</div>
    </div>
""", unsafe_allow_html=True)

# ---------- CONTENT ----------
st.subheader("📝 About the Test")
st.write("""
    This test will help you understand your stress type and how you respond to different situations.
    Answer each question honestly for the most accurate results.
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("⏱️ Duration", "15-20 min")

with col2:
    st.metric("📋 Questions", "25")

with col3:
    st.metric("🎯 Purpose", "Stress Type Assessment")

# ---------- START TEST BUTTON ----------
st.divider()

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🚀 Start Test", use_container_width=True, type="primary"):
        st.switch_page("pages/test_questions.py")  # ← Navigation works!

# ---------- LOGOUT BUTTON ----------
st.divider()

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.user_id = ""
        st.rerun()