import streamlit as st
import json
import os

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Stress Test Dashboard",
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
        
        .stButton button[kind="primary"] {
            background: #4CAF50 !important;
            color: white !important;
        }
        .stButton button[kind="primary"]:hover {
            background: #43A047 !important;
            box-shadow: 0 14px 34px rgba(76, 175, 80, 0.40) !important;
            transform: translateY(-3px);
        }
        
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

# ---------- CHECK LOGIN ----------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login to access this page.")
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/login.py")
    st.stop()

# ---------- HISTORY FUNCTIONS ----------
def get_user_history_file():
    username = st.session_state.get("username", "default")
    return f"user_history_{username}.json"

def load_test_history():
    history_file = get_user_history_file()
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

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

# ---------- ACTION BUTTONS ----------
st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Start Test", use_container_width=True, type="primary"):
        st.session_state.current_q_index = 0
        st.session_state.answers = {}
        st.session_state.user_responses = {}
        st.session_state.formatted_answers = {}
        st.session_state.test_completed = False
        st.session_state.gender = None
        st.session_state.gender_code = None
        st.session_state.age = None
        st.session_state.viewing_history = False
        st.session_state.history_saved = False  # <-- Reset for new test
        st.switch_page("pages/test_questions.py")

with col2:
    if st.button("📜 View History", use_container_width=True):
        st.switch_page("pages/history.py")

# ---------- QUICK STATS ----------
history = load_test_history()

if history:
    st.divider()
    st.subheader("📊 Your Test History Summary")
    
    total_tests = len(history)
    latest = history[0] if history else None
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tests", total_tests)
    with col2:
        if latest:
            stress_type = latest.get("stress_type", "N/A")
            st.metric("Latest Result", stress_type)
    with col3:
        if latest:
            percentage = latest.get("percentage", 0)
            st.metric("Latest Score", f"{percentage:.1f}%")
    with col4:
        if latest:
            date = latest.get("date", "N/A")
            if len(date) > 10:
                date = date[:10]
            st.metric("Last Test Date", date)
    
    if latest:
        st.info(f"💡 Your last test on **{latest.get('date', 'N/A')}** showed **{latest.get('stress_type', 'N/A')}** with a stress level of **{latest.get('stress_level', 'N/A')}**")
else:
    st.divider()
    st.info("📭 You haven't taken any tests yet. Click 'Start Test' to begin!")

# ---------- LOGOUT ----------
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.user_id = ""
        st.rerun()