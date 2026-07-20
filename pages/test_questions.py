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
            background: linear-gradient(#c7f9ff, #dafbff, #fbffdb, #d5f7cb, #c7f9ff);
        }
        .question-container {
            text-align: center;
            padding: 30px 40px;
            background: rgba(255, 255, 255, 0.7);
            border-radius: 40px;
            backdrop-filter: blur(10px);
            margin: 20px auto;
            max-width: 900px;
            width: 100%;
        }
        .question-number {
            font-size: 18px;
            color: #2E7D32;
            font-weight: 500;
        }
        .question-text {
            font-size: 28px;
            font-weight: 600;
            color: #1B5E20;
            margin: 20px 0;
            line-height: 1.6;
        }
        .progress-text {
            text-align: center;
            color: #2E7D32;
            font-size: 16px;
            margin-top: 20px;
        }
        .stButton button {
            font-size: 24px !important;
            border-radius: 60px !important;
            padding: 20px 20px !important;
            font-weight: 600 !important;
            min-height: 60px !important;
            width: 100% !important;
        }
        .stButton button[kind="primary"] {
            background: #4CAF50 !important;
            color: white !important;
        }
        .stButton button[kind="primary"]:hover {
            background: #43A047 !important;
            transform: translateY(-3px);
            box-shadow: 0 14px 34px rgba(76, 175, 80, 0.40) !important;
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

# ---------- CSV FILE PATH ----------
CSV_PATH = "Stress_Dataset.csv"  # Your dataset file

# ---------- LOAD QUESTIONS FROM CSV ----------
@st.cache_data
def load_questions():
    """Load questions from the CSV file"""
    try:
        if not os.path.exists(CSV_PATH):
            st.error(f"❌ CSV file not found at: {CSV_PATH}")
            st.info("📁 Please place your CSV file in the root folder.")
            return []
        
        # Read CSV
        df = pd.read_csv(CSV_PATH)
        
        # --- MAP YOUR KAGGLE COLUMNS ---
        # These are the question columns from your dataset
        question_columns = [
            "Have you recently experienced stress in your life?",
            "Have you noticed a rapid heartbeat or palpitations?",
            "Have you been dealing with anxiety or tension recently?",
            "Do you face any sleep problems or difficulties falling asleep?",
            "Have you been getting headaches more often than usual?",
            "Do you get irritated easily?",
            "Do you have trouble concentrating on your academic tasks?",
            "Have you been feeling sadness or low mood?",
            "Have you been experiencing any illness or health issues?",
            "Do you often feel lonely or isolated?",
            "Do you feel overwhelmed with your academic workload?",
            "Are you in competition with your peers, and does it affect you?",
            "Do you find that your relationship often causes you stress?",
            "Are you facing any difficulties with your professors or instructors?",
            "Is your working environment unpleasant or stressful?",
            "Do you struggle to find time for relaxation and leisure activities?",
            "Is your hostel or home environment causing you difficulties?",
            "Do you lack confidence in your academic performance?",
            "Do you lack confidence in your choice of academic subjects?",
            "Academic and extracurricular activities conflicting for you?",
            "Do you attend classes regularly?",
            "Have you gained/lost weight?"
        ]
        
        # Options for all questions (Likert scale 1-5)
        options = ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"]
        
        # Build questions list
        questions = []
        for idx, col in enumerate(question_columns):
            if col in df.columns:
                questions.append({
                    "id": idx + 1,
                    "question": col,
                    "category": "Stress Assessment",
                    "options": options,
                    "column_name": col  # Store original column name for later
                })
            else:
                st.warning(f"Column not found: {col}")
        
        # Store the full dataframe for later use (results)
        st.session_state.full_df = df
        
        return questions
        
    except Exception as e:
        st.error(f"Error loading questions: {str(e)}")
        return []

# ---------- INITIALIZE SESSION STATE ----------
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "test_completed" not in st.session_state:
    st.session_state.test_completed = False
if "user_responses" not in st.session_state:
    st.session_state.user_responses = {}

# ---------- LOAD QUESTIONS ----------
questions = load_questions()

# ---------- MAIN CONTENT ----------
st.title("📝 Stress Type Test")

if not questions:
    st.error("❌ No questions loaded. Please check your CSV file.")
    if st.button("← Back to Home"):
        st.switch_page("main.py")
    st.stop()

total_questions = len(questions)
current_index = st.session_state.current_q_index

# ---------- CHECK IF TEST IS COMPLETED ----------
if st.session_state.test_completed:
    st.success("✅ Test completed! Thank you for your responses.")
    st.balloons()
    
    # Save all answers
    st.subheader("📊 Your Responses")
    for q_id, answer in st.session_state.answers.items():
        st.write(f"Q{q_id}: {answer}")
    
    if st.button("📊 View Results"):
        st.switch_page("pages/results.py")
    
    if st.button("← Back to Home"):
        st.switch_page("main.py")
    st.stop()

# ---------- DISPLAY CURRENT QUESTION ----------
if current_index < total_questions:
    question = questions[current_index]
    q_id = question.get("id", current_index + 1)
    q_text = question.get("question", "Question not found")
    options = question.get("options", ["1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"])
    category = question.get("category", "Stress Assessment")
    
    # Progress bar
    progress = (current_index) / total_questions
    st.progress(progress)
    st.caption(f"Question {current_index + 1} of {total_questions}")
    
    # Question container
    st.markdown(f"""
        <div class="question-container">
            <div class="question-number">Question {current_index + 1} of {total_questions}</div>
            <div class="question-text">{q_text}</div>
            <div style="font-size: 14px; color: #888;">Category: {category}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # ---------- OPTIONS ----------
    st.subheader("Select your answer:")
    
    selected_option = st.radio(
        label="Choose one:",
        options=options,
        key=f"q_{q_id}",
        index=None,
        horizontal=False,
    )
    
    # ---------- NAVIGATION BUTTONS ----------
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if current_index == total_questions - 1:
            if st.button("📤 Submit Test", use_container_width=True, type="primary"):
                if selected_option is None:
                    st.warning("⚠️ Please select an answer before submitting.")
                else:
                    # Save answer
                    st.session_state.answers[q_id] = selected_option
                    st.session_state.user_responses[question.get("column_name", q_text)] = selected_option
                    st.session_state.test_completed = True
                    st.rerun()
        else:
            if st.button("➡️ Next Question", use_container_width=True, type="primary"):
                if selected_option is None:
                    st.warning("⚠️ Please select an answer before proceeding.")
                else:
                    # Save answer and move to next
                    st.session_state.answers[q_id] = selected_option
                    st.session_state.user_responses[question.get("column_name", q_text)] = selected_option
                    st.session_state.current_q_index += 1
                    st.rerun()
    
    st.markdown(f"""
        <div class="progress-text">
            {current_index + 1} of {total_questions} questions answered
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.user_id = ""
            st.session_state.current_q_index = 0
            st.session_state.answers = {}
            st.session_state.user_responses = {}
            st.session_state.test_completed = False
            st.rerun()