import streamlit as st
import json
import os
import base64

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Stress Test Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- LOAD IMAGES AS BASE64 ----------
def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII="
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

profile_img_base64 = get_base64_image("sources/profile.png")
home_img_base64 = get_base64_image("sources/home.png")

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
        h1 {{
            margin-top: -1rem !important;
            padding-top: 0 !important;
        }}
        /* --------------------------- */

        /* Main Background */
        .stApp {{
            background: linear-gradient(#c7f9ff, #dafbff, #fbffdb, #d5f7cb, #c7f9ff);
        }}

        /* Welcome Box */
        .welcome-container {{
            text-align: center;
            padding: 40px 50px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 40px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            margin: 20px auto;
            max-width: 700px;
            width: 100%;
        }}

        .welcome-title {{ font-size: 48px; font-weight: 700; color: #1B5E20; }}
        .welcome-subtitle {{ font-size: 24px; color: #2E7D32; margin-top: 10px; }}
        .user-greeting {{ font-size: 28px; color: #1B5E20; font-weight: 600; margin: 20px 0; }}

        /* General Button Styling */
        div[data-testid="stHorizontalBlock"] div.stButton > button {{
            width: 100% !important;
            border-radius: 60px !important;
            padding: 20px 20px !important;
            font-size: 22px !important;
            font-weight: 600 !important;
            border: none !important;
            cursor: pointer !important;
            transition: all 0.25s ease !important;
            text-align: center !important;
            font-family: inherit !important;
            line-height: 1.4 !important;
            min-height: 65px !important;
        }}

        div[data-testid="stHorizontalBlock"] div.stButton > button[kind="primary"] {{
            background: #4CAF50 !important;
            color: white !important;
        }}
        div[data-testid="stHorizontalBlock"] div.stButton > button[kind="primary"]:hover {{
            background: #43A047 !important;
            box-shadow: 0 14px 34px rgba(76, 175, 80, 0.40) !important;
            transform: translateY(-3px);
        }}

        div[data-testid="stHorizontalBlock"] div.stButton > button:not([kind="primary"]) {{
            background: #2196F3 !important;
            color: white !important;
        }}
        div[data-testid="stHorizontalBlock"] div.stButton > button:not([kind="primary"]):hover {{
            background: #1976D2 !important;
            box-shadow: 0 14px 34px rgba(33, 150, 243, 0.40) !important;
            transform: translateY(-3px);
        }}

        /* ---------- FORCE NAVIGATION TO ABSOLUTE CORNERS ---------- */
        div[data-testid="stHorizontalBlock"]:has(.st-key-home_button) {{
            position: relative !important;
            display: flex !important;
            justify-content: space-between !important;
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

        .st-key-logout_button {{
            position: absolute !important;
            right: 0 !important;
            top: 0 !important;
        }}

        .st-key-logout_button button {{
            width: 50px !important;
            height: 50px !important;
            min-width: 50px !important;
            min-height: 50px !important;
            padding: 0 !important;
            margin: 0 !important;
            background-color: transparent !important;
            background-image: url("data:image/png;base64,{profile_img_base64}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            border: none !important;
            border-radius: 50% !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }}

        .st-key-logout_button button:hover {{
            transform: scale(1.08) !important;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25) !important;
        }}

        .st-key-logout_button button p {{
            display: none !important;
        }}
    </style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# ---------- CHECK LOGIN ----------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login to access this page.")
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/login.py")
    st.stop()


# ---------- TOP NAVIGATION: FORCED LEFT & RIGHT ----------
with st.container():
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="st-key-home_button">', unsafe_allow_html=True)
        if st.button("Home", key="home_button", help="Go to Home"):
            st.switch_page("main.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="st-key-logout_button">', unsafe_allow_html=True)
        if st.button("Logout", key="logout_button", help="Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.user_id = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ---------- HISTORY FUNCTIONS ----------
def get_user_history_file():
    username = st.session_state.get("username", "default")
    return f"user_history_{username}.json"

def load_test_history():
    history_file = get_user_history_file()
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                return json.load(f)
        except:
            return []
    return []


# ---------- WELCOME MESSAGE ----------
username = st.session_state.get("username", "User")

st.markdown(f"""
    <div class="welcome-container">
        <div class="welcome-title">Stress Type Test</div>
        <div class="user-greeting">👋 Welcome, {username}!</div>
        <div class="welcome-subtitle">
            Discover and know your stress type with our test
        </div>
    </div>
""", unsafe_allow_html=True)


# ==========================================
# ABOUT THE TEST
# ==========================================
st.markdown("### 📝 About the Test")

st.write("""
    This test will help you understand your stress type and how you respond
    to different situations. Answer each question honestly for the most
    accurate results.
""")

col1, col2 = st.columns(2)

with col1:
    st.metric("⏱️ Duration", "15-20 min")

with col2:
    st.metric("📋 Questions", "25")


# ---------- START TEST BUTTON ----------
btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 2])

with btn_col2:
    if st.button(
        "🚀 Start Test",
        type="primary",
        use_container_width=True
    ):
        st.session_state.current_q_index = 0
        st.session_state.answers = {}
        st.session_state.user_responses = {}
        st.session_state.formatted_answers = {}
        st.session_state.test_completed = False
        st.session_state.gender = None
        st.session_state.gender_code = None
        st.session_state.age = None
        st.session_state.viewing_history = False
        st.session_state.history_saved = False

        st.switch_page("pages/test_questions.py")


# ---------- SPACING ----------
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")


# ==========================================
# TEST HISTORY SUMMARY
# ==========================================
history = load_test_history()

st.markdown("### 📊 Your Test History Summary")

if history:
    total_tests = len(history)
    latest = history[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Tests", total_tests)

    with col2:
        st.metric(
            "Latest Result",
            latest.get("stress_type", "N/A")
        )

    with col3:
        percentage = latest.get("percentage", 0)
        st.metric(
            "Latest Score",
            f"{percentage:.1f}%"
        )

    with col4:
        date = latest.get("date", "N/A")

        if len(date) > 10:
            date = date[:10]

        st.metric("Last Test Date", date)

    st.info(
        f"💡 Your last test on **{latest.get('date', 'N/A')}** "
        f"showed **{latest.get('stress_type', 'N/A')}**"
    )

else:
    st.info(
        "📭 You haven't taken any tests yet. "
        "Click 'Start Test' to begin!"
    )


# ---------- VIEW HISTORY BUTTON ----------
btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 2])

with btn_col2:
    if history:
        if st.button(
            "📜 View Full History",
            use_container_width=True
        ):
            st.switch_page("pages/history.py")

    else:
        st.button(
            "📜 View Full History",
            use_container_width=True,
            disabled=True
        )