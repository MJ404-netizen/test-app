import streamlit as st
import json
import os
import base64

# ---------- LOAD IMAGES AS BASE64 ----------
def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII="
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

back_arrow_base64 = get_base64_image("sources/arrow.png")

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Test History",
    page_icon="📜",
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
            background: linear-gradient(#c7f9ff, #dafbff, #fbffdb, #d5f7cb, #c7f9ff) !important;
        }}
        
        .history-item {{
            background: rgba(255, 255, 255, 0.92);
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 2px 15px rgba(0, 0, 0, 0.08);
            transition: transform 0.2s;
            border-left: 5px solid #4CAF50;
        }}
        
        .history-item:hover {{
            transform: translateX(5px);
        }}
        
        .history-date {{
            font-size: 14px;
            color: #666;
        }}
        
        .history-stress-type {{
            font-size: 20px;
            font-weight: 600;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
        }}
        
        .empty-state-icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        
        .empty-state-text {{
            font-size: 20px;
            color: #666;
        }}
        
        /* ---------- STANDARD BUTTONS (View Results) ---------- */
        .stButton button {{
            border-radius: 12px !important;
            padding: 10px 25px !important;
            font-weight: 600 !important;
            font-size: 18px !important; 
            transition: all 0.25s ease !important;
        }}
        
        .stButton button[kind="primary"] {{
            background: #4CAF50 !important;
            color: white !important;
        }}
        .stButton button[kind="primary"]:hover {{
            background: #43A047 !important;
            transform: translateY(-2px);
        }}

        /* ---------- CLEAR HISTORY & TAKE FIRST TEST BUTTONS ---------- */
        .st-key-clear_history_btn button,
        .st-key-take_first_test_btn button {{
            width: 100% !important;
            border-radius: 60px !important;
            padding: 15px 20px !important;
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

        .st-key-clear_history_btn button p,
        .st-key-take_first_test_btn button p {{
            font-size: 24px !important; 
            font-weight: 700 !important;
            color: white !important;
            margin: 0 !important;
        }}

        .st-key-clear_history_btn button:hover,
        .st-key-take_first_test_btn button:hover {{
            background: #43A047 !important;
            box-shadow: 0 14px 34px rgba(76, 175, 80, 0.40) !important;
            transform: translateY(-3px) !important;
            color: white !important;
        }}

        /* ---------- PIN BACK ARROW TO TOP-LEFT CORNER ---------- */
        div[data-testid="stHorizontalBlock"]:has(.st-key-back_button) {{
            position: relative !important;
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            margin-top: 1rem !important;
            margin-bottom: 1rem !important;
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
            background-image: url("data:image/png;base64,{back_arrow_base64}") !important;
            background-size: contain !important;
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
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------- CHECK LOGIN ----------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login to access this page.")
    if st.button("🔐 Go to Login"):
        st.switch_page("main.py")
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

# ---------- TOP-LEFT BACK BUTTON ----------
with st.container():
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Back", key="back_button", help="Back to Test"):
            st.switch_page("pages/test_page.py")

# ---------- HEADER ----------
st.write("")
st.write("")
st.title("📜 Test History")

# ---------- LOAD HISTORY ----------
history = load_test_history()

if history:
    st.write(f"Showing {len(history)} previous test results")
    
    for idx, entry in enumerate(history):
        date = entry.get("date", "Unknown date")
        stress_type = entry.get("stress_type", "No Data")
        total_q = entry.get("total_questions", 0)
        age = entry.get("age", "N/A")
        gender = entry.get("gender", "N/A")
        
        # Get Model Confidence (Fallback to percentage if svm_confidence doesn't exist in old records)
        svm_confidence = entry.get("svm_confidence", entry.get("percentage", 0))
        
        # Determine emoji and color
        if stress_type == "Eustress":
            emoji = "💪"
            border_color = "#0D47A1"
        elif stress_type == "Distress":
            emoji = "😰"
            border_color = "#B71C1C"
        else:
            emoji = "😌"
            border_color = "#1B5E20"
        
        # Format Confidence (Check if it's a decimal like 0.855 or a whole number like 85.5)
        if svm_confidence <= 1.0 and svm_confidence > 0:
            conf_display = f"{svm_confidence * 100:.1f}%"
        else:
            conf_display = f"{svm_confidence:.1f}%"

        # History item
        st.markdown(f"""
            <div class="history-item" style="border-left-color: {border_color};">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <div class="history-stress-type">{emoji} {stress_type}</div>
                        <div class="history-date">📅 {date}</div>
                    </div>
                    <div style="text-align: right;">
                        <span style="color: #666; font-weight: 600; display: block; font-size: 14px;">🤖 AI Confidence</span>
                        <span style="color: #333; font-weight: 700; font-size: 18px;">{conf_display}</span>
                    </div>
                </div>
                <div style="margin-top: 10px; font-size: 14px; color: #888;">
                    👤 {gender} (Age: {age}) • 📝 {total_q} questions answered
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # View Results button
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button(f"📊 View Results", key=f"view_{idx}", use_container_width=True):
                # Load answers and demographics
                st.session_state.answers = entry.get("answers", {})
                st.session_state.gender = entry.get("gender")
                st.session_state.gender_code = entry.get("gender_code")
                st.session_state.age = entry.get("age")
                
                # Load the saved snapshot data to bypass recalculation
                st.session_state.saved_percentage = entry.get("percentage", 0)
                st.session_state.saved_svm_confidence = entry.get("svm_confidence", None)
                st.session_state.saved_svm_probabilities = entry.get("svm_probabilities", None)
                st.session_state.saved_stress_type = entry.get("stress_type", "No Stress")
                st.session_state.saved_category_scores = entry.get("category_scores", {})
                st.session_state.saved_top_stress_areas = entry.get("top_stress_areas", [])
                
                st.session_state.test_completed = True
                st.session_state.viewing_history = True
                st.session_state.history_saved = True
                st.switch_page("pages/results.py")
    
    # Clear history button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🗑️ Clear All History", key="clear_history_btn", use_container_width=True):
            history_file = get_user_history_file()
            if os.path.exists(history_file):
                os.remove(history_file)
            st.rerun()

else:
    st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <div class="empty-state-text">No test history found</div>
            <div style="color: #888; margin-top: 10px;">
                Take your first stress test to start tracking your results!
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Take Your First Test", key="take_first_test_btn", use_container_width=True):
            st.switch_page("pages/test_page.py")

# ---------- FOOTER ----------
st.markdown(
    "<p style='color: black; font-weight: bold; font-size: 14px;'>"
    "💡 Your test history is stored locally and only accessible by you."
    "</p>", 
    unsafe_allow_html=True
)