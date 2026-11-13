import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="SurveyBot",
    page_icon="🤖",
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
        
        /* MULTIPLE SELECTORS TO FORCE FONT SIZE */
        .stButton button,
        .stButton > button,
        button[kind="primary"],
        button[kind="secondary"],
        .stButton button[kind="primary"],
        .stButton button[kind="secondary"],
        .stButton .st-emotion-cache-1r6slb0,
        .stButton .st-emotion-cache-1r6slb0 button {
            font-size: 50px !important;
        }
        
        /* Target ALL buttons with any selector */
        .stButton button {
            width: 100% !important;
            border-radius: 60px !important;
            padding: 25px 20px !important;
            font-size: 50px !important;
            font-weight: 600 !important;
            border: none !important;
            cursor: pointer !important;
            transition: all 0.25s ease !important;
            display: block !important;
            text-align: center !important;
            font-family: inherit !important;
            line-height: 1.4 !important;
            min-height: 250px !important;
            margin-bottom: 10px !important;
        }
        .stButton button:hover {
            transform: translateY(-3px) !important;
        }
        
        /* Login Button (Primary) */
        .stButton button[kind="primary"] {
            background: #4CAF50 !important;
            color: white !important;
            margin-right: 15px !important;
        }
        .stButton button[kind="primary"]:hover {
            background: #43A047 !important;
            box-shadow: 0 14px 34px rgba(76, 175, 80, 0.40) !important;
        }
        
        /* Create Account Button (Secondary) */
        .stButton button:not([kind="primary"]) {
            background: rgba(255, 255, 255, 0.20) !important;
            color: #1B5E20 !important;
            border: 2px solid rgba(76, 175, 80, 0.3) !important;
            backdrop-filter: blur(10px);
            margin-left: 15px !important;
        }
        .stButton button:not([kind="primary"]):hover {
            background: rgba(255, 255, 255, 0.35) !important;
            border-color: #4CAF50 !important;
        }

        .main-title {
            text-align: center;
            color: #1B5E20;
            font-size: 42px;
            font-weight: 700;
        }
        .subtitle {
            text-align: center;
            color: #2E7D32;
            font-size: 18px;
            margin-bottom: 30px;
        }
        .footer {
            text-align: center;
            color: #4CAF50;
            font-size: 13px;
            margin-top: 40px;
            opacity: 0.7;
        }
        .logo {
            font-size: 72px;
            display: block;
            position: absolute;
            top: 20px;
            left: 30px;
            margin-bottom: 10px;
        }

        /* ---------- FORCE BIGGER TEXT INSIDE BUTTON LABELS ---------- */
        .stButton button p,
        .stButton > button p,
        .stButton button[kind="primary"] p,
        .stButton button:not([kind="primary"]) p {
            font-size: 30px !important;
            font-weight: 700 !important;
            line-height: 1.2 !important;
            margin: 0 !important;
        }

        /* ---------- DISCLAIMER FOOTER ---------- */
        .disclaimer-wrapper {
            display: flex;
            justify-content: center;
            margin-top: 80px; /* Pushes it down towards the bottom of the page */
            margin-bottom: 30px;
            padding: 0 20px;
        }
        .disclaimer-text {
            color: black;
            font-weight: bold;
            font-size: 14px;
            text-align: center;
            max-width: 700px; /* Prevents the text from stretching too wide */
            line-height: 1.5;
        }

        /* ---------- MOBILE RESPONSIVENESS ---------- */
        @media (max-width: 768px) {
            div[data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
                align-items: center !important;
                gap: 14px !important;
            }
            div[data-testid="column"] {
                width: 100% !important;
                display: flex !important;
                justify-content: center !important;
            }
            .stButton button[kind="primary"] {
                margin-right: 0 !important;
                margin-left: 0 !important;
            }
            .stButton button:not([kind="primary"]) {
                margin-left: 0 !important;
                margin-right: 0 !important;
            }
            .stButton {
                width: 100% !important;
                display: flex !important;
                justify-content: center !important;
            }
            .stButton button {
                width: 85% !important;
                max-width: 420px !important;
                min-height: 160px !important;
                padding: 20px 15px !important;
                margin: 0 auto !important;
            }
            .stButton button p,
            .stButton > button p {
                font-size: 26px !important;
            }
        }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------- MAIN CONTENT ----------
#st.markdown('<span class="logo">🤖</span>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">Stress Type Test</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Discover and know your stress type with our test</p>', unsafe_allow_html=True)

# ---------- BUTTONS ----------
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    left_col, right_col = st.columns(2)
    
    with left_col:
        login_clicked = st.button(
            "🔐 Login",
            key="login_btn",
            use_container_width=True,
            type="primary",
        )
    
    with right_col:
        create_clicked = st.button(
            "✨ Create Account",
            key="create_btn",
            use_container_width=True,
        )

# ---------- FOOTER ----------
st.markdown('<p class="footer">All responses are kept strictly confidential</p>', unsafe_allow_html=True)

# Wrapped in a div with flexbox to center it perfectly
st.markdown(
    """
    <div class="disclaimer-wrapper">
        <div class="disclaimer-text">
            💡 This report is for informational purposes only. If you're experiencing severe stress, please consult a mental health professional.
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# ---------- NAVIGATION LOGIC ----------
if login_clicked:
    st.switch_page("pages/login.py")

if create_clicked:
    st.switch_page("pages/create_account.py")