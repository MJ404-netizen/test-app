import streamlit as st
import pandas as pd
import csv
import os

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Stress Test Questions",
    page_icon="📝",
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
            background: linear-gradient(#c7f9ff, #dafbff, #fbffdb, #d5f7cb, #c7f9ff) !important;
        }
        
        .question-container {
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
        }
        
        .question-number {
            font-size: 14px;
            color: #2E7D32;
            font-weight: 500;
            margin-bottom: 8px;
            letter-spacing: 1px;
        }
        
        .question-text {
            font-size: 22px;
            font-weight: 600;
            color: #1B5E20;
            line-height: 1.7;
            margin-bottom: 10px;
        }
        
        .options-container {
            background: rgba(255, 255, 255, 0.92);
            border-radius: 20px;
            padding: 30px 35px;
            margin: 10px 20px 10px 5px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.10);
            border-right: 6px solid #2196F3;
            min-height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100%;
        }
        
        .options-title {
            font-size: 16px;
            color: #1565C0;
            font-weight: 600;
            margin-bottom: 20px;
            letter-spacing: 0.5px;
        }
        
        /* HORIZONTAL RADIO BUTTONS - Side by side */
        .stRadio {
            width: 100% !important;
            margin-top: 20px !important;
        }
        
        .stRadio > div {
            display: flex !important;
            flex-direction: row !important;
            gap: 10px !important;
            width: 100% !important;
            flex-wrap: nowrap !important;
        }
        
        .stRadio > div > label {
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
        }
        
        .stRadio > div > label:hover {
            background: #E3F2FD !important;
            border-color: #2196F3 !important;
            transform: translateY(-2px);
        }
        
        .stRadio > div > label[data-selected="true"] {
            background: #2196F3 !important;
            border-color: #1976D2 !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3) !important;
            transform: translateY(-2px);
        }
        
        .stRadio > div > label[data-selected="true"]:hover {
            background: #1976D2 !important;
            border-color: #1565C0 !important;
        }
        
        .stRadio > div > label > div {
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
            justify-content: center !important;
        }
        
        .stRadio > div > label span {
            font-size: 15px !important;
            font-weight: 500 !important;
            color: inherit !important;
            white-space: nowrap !important;
        }
        
        .stRadio > div > label input[type="radio"] {
            width: 16px !important;
            height: 20px !important;
            accent-color: #2196F3 !important;
            flex-shrink: 0 !important;
        }
        
        .stRadio > label {
            display: none !important;
        }
        
        .progress-text {
            text-align: center;
            color: #2E7D32;
            font-size: 16px;
            margin-top: 20px;
        }
        
        .stButton button {
            width: 100% !important;
            border-radius: 60px !important;
            padding: 25px 20px !important;
            font-size: 24px !important;
            font-weight: 600 !important;
            border: none !important;
            cursor: pointer !important;
            transition: all 0.25s ease !important;
            text-align: center !important;
            font-family: inherit !important;
            line-height: 1.4 !important;
            min-height: 70px !important;
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
        
        .stButton button[kind="secondary"] {
            background: #2196F3 !important;
            color: white !important;
        }
        .stButton button[kind="secondary"]:hover {
            background: #1976D2 !important;
            box-shadow: 0 14px 34px rgba(33, 150, 243, 0.40) !important;
            transform: translateY(-3px);
        }

        .stButton button:not([kind="primary"]):not([kind="secondary"]) {
            background: rgba(255, 255, 255, 0.20) !important;
            color: #1B5E20 !important;
            border: 2px solid rgba(76, 175, 80, 0.3) !important;
            backdrop-filter: blur(10px);
        }
        .stButton button:not([kind="primary"]):not([kind="secondary"]):hover {
            background: rgba(255, 255, 255, 0.35) !important;
            border-color: #4CAF50 !important;
            transform: translateY(-3px);
        }
        
        .stProgress > div > div {
            background-color: #4CAF50 !important;
        }
        .stSubheader {
            color: #1B5E20 !important;
        }
        
        .user-info {
            margin-top: 15px;
            padding: 12px 15px;
            background: rgba(232, 245, 233, 0.6);
            border-radius: 10px;
            font-size: 14px;
            color: #2E7D32;
            border: 1px solid #A5D6A7;
        }
        
        .user-info-item {
            display: inline-block;
            margin-right: 25px;
        }
        
        .user-info-label {
            font-weight: 600;
        }
        
        .user-info-value {
            background: white;
            padding: 2px 12px;
            border-radius: 12px;
            margin-left: 5px;
            font-weight: 500;
        }
        
        .warning-text {
            color: #F57C00;
            font-weight: 500;
        }
        
        .button-container {
            display: flex;
            gap: 15px;
            justify-content: center;
        }
        
        .button-container .stButton {
            flex: 1;
        }
        
        .stButton button:disabled {
            display: none !important;
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

# ---------- CSV FILE PATH ----------
CSV_PATH = "Stress_Dataset.csv"

# ---------- DEFINE QUESTIONS DIRECTLY ----------
def get_questions():
    """Define all questions directly - no CSV loading needed for question text"""
    
    # Define the exact questions you want to display
    stress_questions = [
        {
            "text": "Have you recently experienced stress in your life?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Have you noticed a rapid heartbeat or palpitations?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Have you been dealing with anxiety or tension recently? (How Serious is it?)",
            "options": ["1 - Minimal/Mild", "2 - Moderate", "3 - Severe", "4 - Panic-Level", "5 - Debilitating/Chronic"]
        },
        {
            "text": "Do you face any sleep problems or difficulties falling asleep?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "How often have you been dealing with anxiety or tension recently?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Have you been getting headaches more than usual?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Do you get irritated easily?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Do you have trouble concentrating on your academic tasks?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Have you been feeling sadness or low mood?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Have you been experiencing any illness or health issues?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Do you often feel lonely or isolated?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Do you feel overwhelmed with your academic workload?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Are you in competition with your peers, and does it affect you?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Do you find that your relationship often causes you stress?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Are you facing any difficulties with your professors or instructors?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Is your working environment unpleasant or stressful?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Do you struggle to find time for relaxation and leisure activities?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Is your hostel or home environment causing you difficulties?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Do you lack confidence in your academic performance?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Do you lack confidence in your choice of academic subjects?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Academic and extracurricular activities conflicting for you?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Do you attend classes regularly?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        },
        {
            "text": "Have you gained/lost weight?",
            "options": ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        }
    ]
    
    questions = []
    
    # Add Gender as Question 1
    questions.append({
        "id": 1,
        "question": "What is your gender?",
        "category": "Demographics",
        "options": ["Male", "Female"],
        "column_name": "Gender",
        "is_demographic": True
    })
    
    # Add Age as Question 2
    questions.append({
        "id": 2,
        "question": "What is your age?",
        "category": "Demographics",
        "options": ["18", "19", "20", "21"],
        "column_name": "Age",
        "is_demographic": True
    })
    
    # Add stress questions (Questions 3-25)
    for idx, question_data in enumerate(stress_questions, start=3):
        questions.append({
            "id": idx,
            "question": question_data["text"],
            "category": "Stress Assessment",
            "options": question_data["options"],
            "column_name": question_data["text"],
            "is_demographic": False
        })
    
    return questions

# ---------- LOAD CSV FOR DATA STORAGE (optional) ----------
@st.cache_data
def load_csv_data():
    """Load CSV data if it exists, otherwise return None"""
    try:
        if os.path.exists(CSV_PATH):
            df = pd.read_csv(CSV_PATH)
            return df
        else:
            return None
    except Exception as e:
        st.warning(f"Could not load CSV: {str(e)}")
        return None

# ---------- INITIALIZE SESSION STATE ----------
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "test_completed" not in st.session_state:
    st.session_state.test_completed = False
if "user_responses" not in st.session_state:
    st.session_state.user_responses = {}
if "formatted_answers" not in st.session_state:
    st.session_state.formatted_answers = {}
if "gender" not in st.session_state:
    st.session_state.gender = None
if "gender_code" not in st.session_state:
    st.session_state.gender_code = None
if "age" not in st.session_state:
    st.session_state.age = None

# ---------- LOAD QUESTIONS ----------
questions = get_questions()

# Try to load CSV data (optional)
df = load_csv_data()
if df is not None:
    st.session_state.full_df = df
else:
    st.session_state.full_df = None

# ---------- MAIN CONTENT ----------
st.title("📝 Stress Type Test")

if not questions:
    st.error("❌ No questions loaded.")
    if st.button("← Back to Home"):
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
            st.switch_page("pages/results.py")
        if st.button("← Back to Home", use_container_width=True):
            st.switch_page("main.py")
    st.stop()

# ---------- DISPLAY CURRENT QUESTION ----------
if current_index >= 0 and current_index < total_questions:
    question = questions[current_index]
    q_id = question.get("id", current_index + 1)
    q_text = question.get("question", "Question not found")
    options = question.get("options", ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"])
    is_demographic = question.get("is_demographic", False)
    
    # Progress bar
    progress = (current_index) / total_questions
    st.progress(progress)
    st.caption(f"Question {current_index + 1} of {total_questions}")
    
    # Display user info if already set (for stress questions)
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
    
    # ---------- TWO COLUMN LAYOUT: QUESTION | OPTIONS ----------
    col_q, col_o = st.columns([1.2, 2])
    
    with col_q:
        # Create HTML for question container
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
        # Get the current selection from session state if it exists
        current_selection = st.session_state.answers.get(q_id, None)
        if current_selection in options:
            index_value = options.index(current_selection)
        else:
            index_value = None
        
        # Radio button - this will be inside the options container
        selected_option = st.radio(
            label="Select your answer:",
            options=options,
            key=f"q_{q_id}",
            index=index_value,
            label_visibility="collapsed",
        )
    
    # ---------- NAVIGATION BUTTONS ----------
    st.divider()
    
    # Check if we're on the first question
    is_first_question = (current_index == 0)
    is_last_question = (current_index == total_questions - 1)
    
    # Create columns for buttons - use different layouts based on question position
    if is_first_question:
        # First question: Only show Next button (full width)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➡️ Next", use_container_width=True, type="primary"):
                if selected_option is None:
                    st.warning("⚠️ Please select an answer before proceeding.")
                else:
                    # Store the answer
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
        # Not first question: Show both Back and Next/Submit buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                # Back button
                if st.button("◀️ Back", use_container_width=True, type="secondary"):
                    # Save current answer before going back
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
                    # Last question - Show SUBMIT button
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
                            
                            st.session_state.test_completed = True
                            st.rerun()
                else:
                    # Not last question - Show NEXT button
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
    
    # Show progress text
    answered_count = len(st.session_state.answers)
    st.markdown(f"""
        <div class="progress-text">
            {current_index + 1} of {total_questions} questions • 
            {answered_count} answers recorded • 
            {'Demographic' if is_demographic else 'Stress'} Question
            {'' if not is_last_question else ' 🎯 Final Question - Click Submit!'}
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            # Reset all session state
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
            # Clear individual question variables
            for i in range(1, 26):
                if f"q_{i}_answer" in st.session_state:
                    del st.session_state[f"q_{i}_answer"]
            st.rerun()

# If no question is selected, start from the beginning
if current_index < 0 or current_index >= total_questions:
    st.session_state.current_q_index = 0
    st.rerun()