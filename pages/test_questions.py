import streamlit as st
import pandas as pd
import csv
import os
import base64

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Stress Test Questions",
    page_icon="📝",
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
        
        .stApp {{
            background: linear-gradient(#c7f9ff, #dafbff, #fbffdb, #d5f7cb, #c7f9ff) !important;
        }}
        
        .question-container {{
            background: rgba(255, 255, 255, 0.92);
            border-radius: 20px;
            padding: 30px 35px;
            margin: 10px 5px 10px 0;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.10);
            border-left: 6px solid #4CAF50;
            min-height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100%;
        }}
        
        .question-number {{
            font-size: 14px;
            color: #2E7D32;
            font-weight: 500;
            margin-bottom: 8px;
            letter-spacing: 1px;
        }}
        
        .question-text {{
            font-size: 22px;
            font-weight: 600;
            color: #1B5E20;
            line-height: 1.7;
            margin-bottom: 10px;
        }}
        
        /* HORIZONTAL RADIO BUTTONS - Side by side */
        .stRadio {{
            width: 100% !important;
            margin-top: 20px !important;
        }}
        
        .stRadio > div {{
            display: flex !important;
            flex-direction: row !important;
            gap: 10px !important;
            width: 100% !important;
            flex-wrap: nowrap !important;
        }}
        
        .stRadio > div > label {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 10px 12px !important;
            border-radius: 12px !important;
            background: #f8f9fa !important;
            border: 2px solid #e0e0e0 !important;
            cursor: pointer !important;
            transition: all 0.25s ease !important;
            flex: 1 !important;
            min-width: 140px !important;
            min-height: 55px !important;
            text-align: center !important;
            color: #333333 !important;
        }}
        
        .stRadio > div > label:hover {{
            background: #E3F2FD !important;
            border-color: #2196F3 !important;
            transform: translateY(-2px);
        }}
        
        .stRadio > div > label[data-selected="true"] {{
            background: #2196F3 !important;
            border-color: #1976D2 !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3) !important;
            transform: translateY(-2px);
        }}
        
        .stRadio > div > label[data-selected="true"]:hover {{
            background: #1976D2 !important;
            border-color: #1565C0 !important;
        }}
        
        .stRadio > div > label > div {{
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
            justify-content: center !important;
        }}
        
        .stRadio > div > label span {{
            font-size: 15px !important;
            font-weight: 500 !important;
            color: inherit !important;
            white-space: nowrap !important;
        }}
        
        .stRadio > div > label input[type="radio"] {{
            width: 16px !important;
            height: 20px !important;
            accent-color: #2196F3 !important;
            flex-shrink: 0 !important;
        }}
        
        .stRadio > label {{
            display: none !important;
        }}
        
        .progress-text {{
            text-align: center;
            color: #2E7D32;
            font-size: 16px;
            margin-top: 20px;
        }}
        
        /* ---------- NAVIGATION BUTTONS (NEXT/BACK/SUBMIT) ---------- */
        div[data-testid="stHorizontalBlock"] div.stButton > button {{
            width: 100% !important;
            border-radius: 60px !important;
            padding: 25px 20px !important;
            font-weight: 600 !important;
            border: none !important;
            cursor: pointer !important;
            transition: all 0.25s ease !important;
            text-align: center !important;
            font-family: inherit !important;
            line-height: 1.4 !important;
            min-height: 70px !important;
        }}

        /* TARGET THE TEXT INSIDE THE BUTTONS TO MATCH FONT SIZE */
        div[data-testid="stHorizontalBlock"] div.stButton > button p {{
            font-size: 24px !important; 
            font-weight: 700 !important;
            margin: 0 !important;
        }}
        
        /* Primary (Next / Submit) - Green */
        div[data-testid="stHorizontalBlock"] div.stButton > button[kind="primary"] {{
            background: #4CAF50 !important;
            color: white !important;
        }}
        div[data-testid="stHorizontalBlock"] div.stButton > button[kind="primary"] p {{
            color: white !important;
        }}
        div[data-testid="stHorizontalBlock"] div.stButton > button[kind="primary"]:hover {{
            background: #43A047 !important;
            box-shadow: 0 14px 34px rgba(76, 175, 80, 0.40) !important;
            transform: translateY(-3px);
        }}
        
        /* Secondary (Back) - Blue */
        div[data-testid="stHorizontalBlock"] div.stButton > button[kind="secondary"] {{
            background: #2196F3 !important;
            color: white !important;
        }}
        div[data-testid="stHorizontalBlock"] div.stButton > button[kind="secondary"] p {{
            color: white !important;
        }}
        div[data-testid="stHorizontalBlock"] div.stButton > button[kind="secondary"]:hover {{
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
            margin-top: -4rem !important; 
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

        /* ---------- MOBILE FORMATTING (SIDE-BY-SIDE BUTTONS) ---------- */
        @media (max-width: 768px) {{
            /* 1. Target the container holding Back and Next buttons */
            div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stHorizontalBlock"] {{
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                gap: 10px !important;
                width: 100% !important;
            }}
            
            /* 2. Force columns to exactly 50% width */
            div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
                width: 50% !important;
                min-width: 50% !important;
                flex: 1 1 50% !important;
                display: block !important;
            }}

            /* 3. Automatically shrink button height, padding, and text size for mobile */
            div[data-testid="stHorizontalBlock"] div.stButton > button {{
                padding: 10px 5px !important;
                min-height: 55px !important;
                border-radius: 30px !important;
            }}
            
            div[data-testid="stHorizontalBlock"] div.stButton > button p {{
                font-size: 18px !important; 
            }}
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

# ---------- RESET VIEWING HISTORY FLAG ----------
st.session_state.viewing_history = False

# ---------- CSV FILE PATH ----------
CSV_PATH = "Stress_Dataset.csv"

# ---------- DEFINE QUESTIONS DIRECTLY ----------
def get_questions():
    stress_questions = [
        {"text": "Have you recently experienced stress in your life?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Have you noticed a rapid heartbeat or palpitations?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Have you been dealing with anxiety or tension recently? (How Serious is it?)", "options": ["1 - Minimal/Mild", "2 - Moderate", "3 - Severe", "4 - Panic-Level", "5 - Debilitating/Chronic"]},
        {"text": "Do you face any sleep problems or difficulties falling asleep?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "How often have you been dealing with anxiety or tension recently?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Have you been getting headaches more than usual?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Do you get irritated easily?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Do you have trouble concentrating on your academic tasks?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Have you been feeling sadness or low mood?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Have you been experiencing any illness or health issues?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Do you often feel lonely or isolated?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Do you feel overwhelmed with your academic workload?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Are you in competition with your peers, and does it affect you?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Do you find that your relationship often causes you stress?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Are you facing any difficulties with your professors or instructors?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Is your working environment unpleasant or stressful?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Do you struggle to find time for relaxation and leisure activities?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Is your hostel or home environment causing you difficulties?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Do you lack confidence in your academic performance?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Do you lack confidence in your choice of academic subjects?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Academic and extracurricular activities conflicting for you?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Do you attend classes regularly?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]},
        {"text": "Have you gained/lost weight?", "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]}
    ]
    
    questions = []
    questions.append({
        "id": 1, "question": "What is your gender?", "category": "Demographics",
        "options": ["Male", "Female"], "column_name": "Gender", "is_demographic": True
    })
    questions.append({
        "id": 2, "question": "What is your age?", "category": "Demographics",
        "options": ["18", "19", "20", "21"], "column_name": "Age", "is_demographic": True
    })
    
    for idx, question_data in enumerate(stress_questions, start=3):
        questions.append({
            "id": idx, "question": question_data["text"], "category": "Stress Assessment",
            "options": question_data["options"], "column_name": question_data["text"], "is_demographic": False
        })
    return questions

# ---------- LOAD CSV FOR DATA STORAGE (optional) ----------
@st.cache_data
def load_csv_data():
    try:
        if os.path.exists(CSV_PATH):
            return pd.read_csv(CSV_PATH)
        return None
    except Exception as e:
        st.warning(f"Could not load CSV: {str(e)}")
        return None

# ---------- INITIALIZE SESSION STATE ----------
if "current_q_index" not in st.session_state: st.session_state.current_q_index = 0
if "answers" not in st.session_state: st.session_state.answers = {}
if "test_completed" not in st.session_state: st.session_state.test_completed = False
if "history_saved" not in st.session_state: st.session_state.history_saved = False
if "user_responses" not in st.session_state: st.session_state.user_responses = {}
if "formatted_answers" not in st.session_state: st.session_state.formatted_answers = {}
if "gender" not in st.session_state: st.session_state.gender = None
if "gender_code" not in st.session_state: st.session_state.gender_code = None
if "age" not in st.session_state: st.session_state.age = None

# ---------- LOAD QUESTIONS ----------
questions = get_questions()
st.session_state.full_df = load_csv_data()

# ---------- TOP NAVIGATION: FORCED LEFT & RIGHT ----------
with st.container():
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="st-key-home_button">', unsafe_allow_html=True)
        if st.button("Home", key="home_button", help="Go to Home"):
            st.session_state.viewing_history = False
            st.switch_page("main.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="st-key-logout_button">', unsafe_allow_html=True)
        if st.button("Logout", key="logout_button", help="Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.user_id = ""
            st.session_state.current_q_index = 0
            st.session_state.answers = {}
            st.session_state.user_responses = {}
            st.session_state.formatted_answers = {}
            st.session_state.test_completed = False
            st.session_state.gender = None
            st.session_state.gender_code = None
            st.session_state.age = None
            st.session_state.history_saved = False
            for i in range(1, 26):
                if f"q_{i}_answer" in st.session_state:
                    del st.session_state[f"q_{i}_answer"]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ---------- MAIN CONTENT ----------
st.title("📝 Stress Type Test")

if not questions:
    st.error("❌ No questions loaded.")
    if st.button("Home", key="home_button_fallback", help="Go to Home"):
        st.switch_page("main.py")
    st.stop()

total_questions = len(questions)
current_index = st.session_state.current_q_index

# ---------- CHECK IF TEST IS COMPLETED ----------
if st.session_state.test_completed:
    st.success("✅ Test completed! Thank you for your responses.")
    st.balloons()
    
    st.subheader("📊 Your Responses")
    st.write(f"👤 Gender: {st.session_state.gender} (Code: {st.session_state.gender_code})")
    st.write(f"📅 Age: {st.session_state.age}")
    
    for q_id, answer in sorted(st.session_state.answers.items()):
        question_text = next((q["question"] for q in questions if q["id"] == q_id), f"Q{q_id}")
        st.write(f"Q{q_id}: {question_text[:50]}... → {answer}")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📊 View Results", use_container_width=True, type="primary"):
            st.session_state.history_saved = False
            st.session_state.viewing_history = False
            st.switch_page("pages/results.py")
    st.stop()

# ---------- DISPLAY CURRENT QUESTION ----------
if current_index >= 0 and current_index < total_questions:
    question = questions[current_index]
    q_id = question.get("id", current_index + 1)
    q_text = question.get("question", "Question not found")
    options = question.get("options", ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"])
    is_demographic = question.get("is_demographic", False)
    
    st.progress((current_index) / total_questions)
    st.caption(f"Question {current_index + 1} of {total_questions}")
    
    if st.session_state.gender and st.session_state.age and not is_demographic:
        st.markdown(f"""
            <div class="user-info">
                <span class="user-info-item">
                    <span class="user-info-label">👤 Gender:</span>
                    <span class="user-info-value">{st.session_state.gender} (Code: {st.session_state.gender_code})</span>
                </span>
                <span class="user-info-item">
                    <span class="user-info-label">📅 Age:</span>
                    <span class="user-info-value">{st.session_state.age}</span>
                </span>
            </div>
        """, unsafe_allow_html=True)
    
    col_q, col_o = st.columns([1.2, 2])
    
    with col_q:
        category_text = "📋 Demographic" if is_demographic else "📝 Stress Assessment"
        st.markdown(f"""
            <div class="question-container">
                <div class="question-number">
                    {category_text} - Question {current_index + 1}
                </div>
                <div class="question-text">{q_text}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_o:
        current_selection = st.session_state.answers.get(q_id, None)
        index_value = options.index(current_selection) if current_selection in options else None
        
        selected_option = st.radio(
            label="Select your answer:", options=options, key=f"q_{q_id}",
            index=index_value, label_visibility="collapsed",
        )
    
    st.write("")
    st.write("")
    
    is_first_question = (current_index == 0)
    is_last_question = (current_index == total_questions - 1)
    
    if is_first_question:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➡️ Next", use_container_width=True, type="primary"):
                if selected_option is None:
                    st.warning("⚠️ Please select an answer before proceeding.")
                else:
                    st.session_state.answers[q_id] = selected_option
                    st.session_state.user_responses[question.get("column_name", q_text)] = selected_option
                    st.session_state[f"q_{q_id}_answer"] = selected_option
                    st.session_state.formatted_answers[question.get("column_name")] = selected_option
                    
                    if is_demographic:
                        if q_id == 1:
                            st.session_state.gender = selected_option
                            st.session_state.gender_code = 0 if selected_option == "Male" else 1
                        elif q_id == 2:
                            st.session_state.age = int(selected_option)
                    
                    st.session_state.current_q_index += 1
                    st.rerun()
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                if st.button("◀️ Back", use_container_width=True, type="secondary"):
                    if selected_option is not None:
                        st.session_state.answers[q_id] = selected_option
                        st.session_state.user_responses[question.get("column_name", q_text)] = selected_option
                        st.session_state[f"q_{q_id}_answer"] = selected_option
                        st.session_state.formatted_answers[question.get("column_name")] = selected_option
                        
                        if is_demographic:
                            if q_id == 1:
                                st.session_state.gender = selected_option
                                st.session_state.gender_code = 0 if selected_option == "Male" else 1
                            elif q_id == 2:
                                st.session_state.age = int(selected_option)
                    
                    st.session_state.current_q_index -= 1
                    st.rerun()
            
            with btn_col2:
                if is_last_question:
                    if st.button("📤 Submit Test", use_container_width=True, type="primary"):
                        if selected_option is None:
                            st.warning("⚠️ Please select an answer before submitting.")
                        else:
                            st.session_state.answers[q_id] = selected_option
                            st.session_state.user_responses[question.get("column_name", q_text)] = selected_option
                            st.session_state[f"q_{q_id}_answer"] = selected_option
                            st.session_state.formatted_answers[question.get("column_name")] = selected_option
                            
                            if is_demographic:
                                if q_id == 1:
                                    st.session_state.gender = selected_option
                                    st.session_state.gender_code = 0 if selected_option == "Male" else 1
                                elif q_id == 2:
                                    st.session_state.age = int(selected_option)
                            
                            st.session_state.history_saved = False
                            st.session_state.viewing_history = False
                            st.session_state.test_completed = True
                            st.rerun()

                else:
                    if st.button("➡️ Next", use_container_width=True, type="primary"):
                        if selected_option is None:
                            st.warning("⚠️ Please select an answer before proceeding.")
                        else:
                            st.session_state.answers[q_id] = selected_option
                            st.session_state.user_responses[question.get("column_name", q_text)] = selected_option
                            st.session_state[f"q_{q_id}_answer"] = selected_option
                            st.session_state.formatted_answers[question.get("column_name")] = selected_option
                            
                            if is_demographic:
                                if q_id == 1:
                                    st.session_state.gender = selected_option
                                    st.session_state.gender_code = 0 if selected_option == "Male" else 1
                                elif q_id == 2:
                                    st.session_state.age = int(selected_option)
                            
                            st.session_state.current_q_index += 1
                            st.rerun()
    
    answered_count = len(st.session_state.answers)
    st.markdown(f"""
        <div class="progress-text">
            {current_index + 1} of {total_questions} questions • 
            {answered_count} answers recorded • 
            {'Demographic' if is_demographic else 'Stress'} Question
            {'' if not is_last_question else ' 🎯 Final Question - Click Submit!'}
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")

# If no question is selected, start from the beginning
if current_index < 0 or current_index >= total_questions:
    st.session_state.current_q_index = 0
    st.rerun()